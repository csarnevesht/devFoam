# devFoam - CAD Tools for Foam Cutting

A collection of CAD tools and G-code generators for hot-wire foam cutting, designed for macOS.

## Tools

### 1. CAD Viewer/Editor (`cad_viewer.py`)
A simple CAD file viewer and editor for viewing and editing 2D shapes.

**Features:**
- View DXF, SVG, and JSON files
- Draw simple shapes (lines, circles, rectangles, arcs)
- Export to DXF, SVG, or JSON
- Zoom, pan, select, and delete tools

See [README_CAD.md](README_CAD.md) for detailed documentation.

### 2. G-code Generator (`gcode_generator.py`)
A comprehensive G-code generator for hot-wire foam cutting machines.

**Features:**
- 2D contour cutting
- Pocket cutting
- 3D surface cutting
- DXF file import
- Customizable cutting parameters

See [README_GCODE.md](README_GCODE.md) for detailed documentation.

### 3. CAD to G-code Converter (`cad_to_gcode.py`)
GUI application that integrates CAD file loading with G-code generation.

**Features:**
- Load CAD files (DXF, JSON)
- Adjust cutting parameters via GUI
- Preview generated G-code
- Export G-code files

## Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Make scripts executable
chmod +x *.py
```

## Quick Start

### CAD Viewer
```bash
python3 cad_viewer.py
```

### G-code Generator (Command Line)
```bash
python3 gcode_generator.py example   # Simple rectangle
python3 gcode_generator.py circle    # Circle cut
python3 gcode_generator.py complex  # Complex pattern
```

### CAD to G-code Converter (GUI)
```bash
python3 cad_to_gcode.py
```

## Requirements

- Python 3.6+
- tkinter (comes with Python on macOS)
- Optional: `ezdxf` for DXF file support
- Optional: `svg.path` for SVG file support

## Usage Example

1. **Draw shapes** in the CAD viewer
2. **Save as JSON**
3. **Load in CAD to G-code converter**
4. **Adjust parameters** (feed rate, depth, etc.)
5. **Generate and save G-code**
6. **Use on your foam cutting machine**

## License

Free to use for personal and commercial projects.

## Contributing

Contributions welcome! Feel free to submit issues or pull requests.

