# G-code Generator for Foam Cutting

A comprehensive G-code generator specifically designed for hot-wire foam cutting machines. Supports 2D contour cutting, pocket cutting, and 3D surface cutting.

## Features

- **2D Contour Cutting**: Cut lines, circles, rectangles, arcs, and polylines
- **Pocket Cutting**: Cut pockets with outer and inner contours
- **3D Surface Cutting**: Support for complex 3D foam shapes
- **DXF Import**: Load CAD files directly (requires ezdxf)
- **Customizable Parameters**: Feed rate, depth, safety height, wire temperature
- **Multiple Units**: Millimeters or inches
- **GUI Tool**: Easy-to-use interface for CAD to G-code conversion

## Installation

```bash
# Install required library for DXF support (optional)
pip3 install ezdxf

# Make scripts executable
chmod +x gcode_generator.py cad_to_gcode.py
```

## Usage

### Command Line Examples

**Simple rectangle cut:**
```bash
python3 gcode_generator.py example
```

**Circle cut:**
```bash
python3 gcode_generator.py circle
```

**Complex pattern:**
```bash
python3 gcode_generator.py complex
```

### Using as a Library

```python
from gcode_generator import GCodeGenerator

# Create generator
gen = GCodeGenerator()
gen.set_feed_rate(150.0)  # mm/min
gen.set_safety_height(10.0)  # mm

# Generate G-code
gen.header("My Foam Cutting Job")
gen.cut_rectangle(0, 0, 100, 50, depth=0.0)
gen.cut_circle(50, 25, 20, depth=0.0)
gen.footer()

# Save to file
gen.save("output.nc")

# Or get as string
gcode = gen.get_gcode()
print(gcode)
```

### GUI Application

Run the integrated CAD to G-code converter:

```bash
python3 cad_to_gcode.py
```

This opens a GUI where you can:
1. Load CAD files (DXF, JSON)
2. Adjust cutting parameters
3. Preview generated G-code
4. Save G-code to file

## G-code Methods

### Basic Operations

- `header(comment)`: Generate G-code header with initialization
- `footer()`: Generate G-code footer with cleanup
- `rapid_move(x, y, z)`: Rapid positioning (G0)
- `linear_move(x, y, z, feed)`: Linear cutting move (G1)
- `arc_move(x, y, i, j, clockwise)`: Arc cutting (G2/G3)

### Cutting Operations

- `cut_contour(points, closed, depth)`: Cut a 2D contour
- `cut_circle(cx, cy, radius, depth)`: Cut a circle
- `cut_rectangle(x1, y1, x2, y2, depth)`: Cut a rectangle
- `cut_pocket(outer, inner_contours, stepdown, final_depth)`: Cut a pocket
- `cut_3d_surface(points, feed)`: Cut a 3D surface

### File Operations

- `load_from_dxf(filename, depth)`: Load shapes from DXF file
- `generate_from_shapes(shapes, depth)`: Generate from shape dictionary
- `save(filename)`: Save G-code to file
- `get_gcode()`: Get G-code as string

## Example: Complete Workflow

```python
from gcode_generator import GCodeGenerator

# Initialize
gen = GCodeGenerator()
gen.set_feed_rate(120.0)  # mm/min - adjust for your foam type
gen.set_safety_height(5.0)  # Safe Z height
gen.set_wire_temp(200.0)  # Wire temperature (if supported)

# Generate header
gen.header("Foam Wing Template")

# Cut outer contour
outer_points = [(0, 0), (200, 0), (200, 100), (0, 100)]
gen.cut_contour(outer_points, closed=True, depth=0.0)

# Cut inner hole
gen.cut_circle(100, 50, 25, depth=0.0)

# Cut additional features
gen.cut_rectangle(10, 10, 50, 30, depth=0.0)

# Generate footer
gen.footer()

# Save
gen.save("foam_wing.nc")
```

## G-code Parameters

### Feed Rate
- Typical range: 50-300 mm/min
- Depends on foam type and wire temperature
- Start slow and increase as needed

### Safety Height
- Height for rapid moves (non-cutting)
- Should be above the foam surface
- Typical: 5-10 mm

### Cut Depth
- For 2D cutting, usually 0.0 (full depth)
- For 3D or multi-pass: negative values
- Example: -5.0 for 5mm deep cut

### Wire Temperature
- Adjust based on foam type
- EPS foam: ~180-220°C
- XPS foam: ~200-240°C
- Check your machine's documentation

## Supported File Formats

### Input:
- **DXF** (.dxf) - Requires `ezdxf` library
- **JSON** (.json) - Native format from CAD viewer

### Output:
- **G-code** (.nc, .gcode, .txt) - Standard CNC format

## Integration with CAD Viewer

1. Draw shapes in `cad_viewer.py`
2. Save as JSON
3. Load in `cad_to_gcode.py`
4. Generate G-code
5. Save and use on your foam cutting machine

## Machine Compatibility

The generated G-code uses standard G/M codes:
- **G0**: Rapid positioning
- **G1**: Linear interpolation
- **G2/G3**: Circular interpolation (arcs)
- **G17**: XY plane selection
- **G20/G21**: Inches/Millimeters
- **G90**: Absolute positioning
- **M3/M5**: Spindle/wire on/off (adjust for your machine)

**Note**: Some machines may use different M-codes for wire control. Adjust the `set_wire_on()` and `set_wire_off()` methods if needed.

## Tips for Foam Cutting

1. **Start with test cuts**: Always test on scrap foam first
2. **Adjust feed rate**: Too fast = rough cuts, too slow = wire drag
3. **Wire tension**: Keep wire properly tensioned
4. **Temperature control**: Adjust based on foam type and thickness
5. **Safety first**: Always use proper ventilation and safety equipment

## Troubleshooting

**"No module named 'ezdxf'"**:
```bash
pip3 install ezdxf
```

**G-code doesn't run on machine**:
- Check machine compatibility with G-codes used
- Verify units (G20/G21)
- Check coordinate system (G90/G91)
- Adjust M-codes for wire control if needed

**Cuts are inaccurate**:
- Verify units match between CAD and machine
- Check machine calibration
- Verify feed rate is appropriate

## Advanced Usage

### Multi-pass Cutting

```python
# Cut in multiple passes
for depth in [0, -2, -4, -6]:
    gen.cut_contour(points, closed=True, depth=depth)
```

### Custom Feed Rates

```python
# Different feed rates for different operations
gen.linear_move(100, 50, feed=150.0)  # Fast cut
gen.linear_move(100, 60, feed=80.0)  # Slow cut for detail
```

### Complex 3D Surfaces

```python
# Generate 3D surface points
points_3d = [
    (0, 0, 0),
    (50, 0, 5),
    (100, 0, 10),
    (100, 50, 8),
    # ... more points
]
gen.cut_3d_surface(points_3d, feed=100.0)
```

## License

Free to use for personal and commercial projects.

