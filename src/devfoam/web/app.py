"""
Flask web application for DevFoam G-code generator.

Provides web-based CAD to G-code conversion with interactive canvas viewer.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from devfoam.gcode_generator import GCodeGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'dxf', 'svg', 'json'}


def allowed_file(filename):
    """
    Check if file extension is allowed.

    Args:
        filename (str): Name of the file to check.

    Returns:
        bool: True if extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Render the main web application page.

    Returns:
        str: Rendered HTML template.
    """
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle CAD file upload and parse shapes.

    Returns:
        json: Parsed shapes data or error message.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: DXF, SVG, JSON'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Parse the file based on extension
        ext = filename.rsplit('.', 1)[1].lower()

        if ext == 'json':
            with open(filepath, 'r') as f:
                shapes = json.load(f)
        elif ext == 'dxf':
            shapes = parse_dxf_file(filepath)
        elif ext == 'svg':
            shapes = parse_svg_file(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Clean up temporary file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'shapes': shapes,
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/api/generate', methods=['POST'])
def generate_gcode():
    """
    Generate G-code from shapes and parameters.

    Expected JSON payload:
        {
            "shapes": [...],
            "feed_rate": 150.0,
            "safety_height": 10.0,
            "wire_temp": 200.0,
            "units": "mm",
            "depth": 0.0
        }

    Returns:
        json: Generated G-code or error message.
    """
    try:
        data = request.get_json()

        if not data or 'shapes' not in data:
            return jsonify({'error': 'No shapes provided'}), 400

        shapes = data['shapes']
        feed_rate = float(data.get('feed_rate', 150.0))
        safety_height = float(data.get('safety_height', 10.0))
        wire_temp = float(data.get('wire_temp', 200.0))
        units = data.get('units', 'mm')
        depth = float(data.get('depth', 0.0))

        # Convert shapes from dictionary format to list format
        # Web format: {"lines": [...], "circles": [...], "polylines": [...]}
        # Expected format: [{"type": "line", ...}, {"type": "circle", ...}, ...]
        shape_list = []
        
        if isinstance(shapes, dict):
            # Convert from dictionary format
            if 'lines' in shapes:
                for line in shapes['lines']:
                    shape_list.append({
                        'type': 'line',
                        'x1': line.get('x1', 0),
                        'y1': line.get('y1', 0),
                        'x2': line.get('x2', 0),
                        'y2': line.get('y2', 0)
                    })
            
            if 'circles' in shapes:
                for circle in shapes['circles']:
                    shape_list.append({
                        'type': 'circle',
                        'cx': circle.get('cx', 0),
                        'cy': circle.get('cy', 0),
                        'radius': circle.get('radius', 0)
                    })
            
            if 'rectangles' in shapes:
                for rect in shapes['rectangles']:
                    shape_list.append({
                        'type': 'rectangle',
                        'x1': rect.get('x1', 0),
                        'y1': rect.get('y1', 0),
                        'x2': rect.get('x2', 0),
                        'y2': rect.get('y2', 0)
                    })
            
            if 'arcs' in shapes:
                for arc in shapes['arcs']:
                    shape_list.append({
                        'type': 'arc',
                        'cx': arc.get('cx', 0),
                        'cy': arc.get('cy', 0),
                        'radius': arc.get('radius', 0),
                        'start_angle': arc.get('start_angle', 0),
                        'end_angle': arc.get('end_angle', 180)
                    })
            
            if 'polylines' in shapes:
                for poly in shapes['polylines']:
                    shape_list.append({
                        'type': 'polyline',
                        'points': poly.get('points', []),
                        'closed': poly.get('closed', True),
                        'start_index': poly.get('start_index', None),
                        'clockwise': poly.get('clockwise', None),
                        'entry_index': poly.get('entry_index', None),
                        'exit_index': poly.get('exit_index', None)
                    })
        elif isinstance(shapes, list):
            # Already in list format
            shape_list = shapes
        else:
            return jsonify({'error': 'Invalid shapes format'}), 400

        # Create G-code generator
        gen = GCodeGenerator()
        gen.set_feed_rate(feed_rate)
        gen.set_safety_height(safety_height)
        gen.set_wire_temp(wire_temp)
        gen.set_units(units)

        # Generate G-code
        gen.header("DevFoam Web - Foam Cutting")
        gen.generate_from_shapes(shape_list, depth=depth)
        gen.footer()

        gcode = gen.get_gcode()

        return jsonify({
            'success': True,
            'gcode': gcode,
            'line_count': len(gcode.splitlines())
        })

    except Exception as e:
        return jsonify({'error': f'Error generating G-code: {str(e)}'}), 500


@app.route('/api/download', methods=['POST'])
def download_gcode():
    """
    Download G-code as a file.

    Expected JSON payload:
        {
            "gcode": "...",
            "filename": "output.nc"
        }

    Returns:
        file: G-code file for download.
    """
    try:
        data = request.get_json()

        if not data or 'gcode' not in data:
            return jsonify({'error': 'No G-code provided'}), 400

        gcode = data['gcode']
        filename = data.get('filename', 'output.gcode')

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.gcode')
        temp_file.write(gcode)
        temp_file.close()

        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )

    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500


def parse_dxf_file(filepath):
    """
    Parse DXF file and extract shapes.

    Args:
        filepath (str): Path to DXF file.

    Returns:
        dict: Shapes dictionary compatible with GCodeGenerator.
    """
    try:
        import ezdxf
    except ImportError:
        raise ImportError("ezdxf is required for DXF file support. Install with: pip install ezdxf")

    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    shapes = {
        'lines': [],
        'circles': [],
        'rectangles': [],
        'arcs': [],
        'polylines': []
    }

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            shapes['lines'].append({
                'x1': start.x, 'y1': start.y,
                'x2': end.x, 'y2': end.y
            })

        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            shapes['circles'].append({
                'cx': center.x,
                'cy': center.y,
                'radius': entity.dxf.radius
            })

        elif entity.dxftype() == 'ARC':
            center = entity.dxf.center
            shapes['arcs'].append({
                'cx': center.x,
                'cy': center.y,
                'radius': entity.dxf.radius,
                'start_angle': entity.dxf.start_angle,
                'end_angle': entity.dxf.end_angle
            })

        elif entity.dxftype() == 'LWPOLYLINE':
            points = []
            with entity.points('xy') as point_list:
                for point in point_list:
                    points.append({'x': point[0], 'y': point[1]})

            shapes['polylines'].append({
                'points': points,
                'closed': entity.closed
            })

    return shapes


def parse_svg_file(filepath):
    """
    Parse SVG file and extract shapes.

    Args:
        filepath (str): Path to SVG file.

    Returns:
        dict: Shapes dictionary compatible with GCodeGenerator.
    """
    # Basic SVG parsing - can be enhanced with svg.path library
    shapes = {
        'lines': [],
        'circles': [],
        'rectangles': [],
        'arcs': [],
        'polylines': []
    }

    # Placeholder for SVG parsing logic
    # In production, use svg.path or similar library

    return shapes


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
