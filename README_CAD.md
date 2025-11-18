# CAD Viewer/Editor for macOS

A simple CAD file viewer and editor for macOS, built with Python and tkinter.

## Features

- **View CAD files**: DXF, SVG formats
- **Edit simple shapes**: Lines, Circles, Rectangles, Arcs
- **Export**: Save as JSON, DXF, or SVG
- **Zoom & Pan**: Navigate your drawings easily
- **Select & Delete**: Edit your drawings

## Installation

1. **Install Python** (if not already installed):
   ```bash
   # Python 3 is usually pre-installed on macOS
   python3 --version
   ```

2. **Install required libraries**:
   ```bash
   pip3 install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip3 install ezdxf      # For DXF support
   pip3 install svg.path   # For SVG support
   ```

3. **Make the script executable**:
   ```bash
   chmod +x cad_viewer.py
   ```

## Usage

### Run the application:
```bash
python3 cad_viewer.py
```

### Or make it executable and run directly:
```bash
./cad_viewer.py
```

## How to Use

### Drawing Tools:
- **Line**: Click and drag to draw a line
- **Circle**: Click center, drag to set radius
- **Rectangle**: Click corner, drag to opposite corner
- **Arc**: Click start, drag to end
- **Select**: Click on shapes to select them (they turn red)
- **Pan**: Click and drag to move the view

### File Operations:
- **New**: Create a new drawing
- **Open**: Open DXF, SVG, or JSON files
- **Save**: Save as JSON format
- **Export DXF**: Export to DXF format (requires ezdxf)
- **Export SVG**: Export to SVG format

### View Controls:
- **Zoom In/Out**: Use mouse wheel or Tools menu
- **Fit to Window**: Automatically fit all shapes to view
- **Reset View**: Reset zoom and pan

## Supported File Formats

### Input:
- **DXF** (.dxf) - Requires `ezdxf` library
- **SVG** (.svg) - Requires `svg.path` library  
- **JSON** (.json) - Native format

### Output:
- **JSON** (.json) - Native format
- **DXF** (.dxf) - Requires `ezdxf` library
- **SVG** (.svg) - Always available

## Notes

- The application uses tkinter which comes with Python on macOS
- DXF and SVG support are optional - install libraries only if needed
- Basic functionality (drawing, JSON save/load) works without any additional libraries

## Troubleshooting

**"No module named 'ezdxf'"**: 
- Install with: `pip3 install ezdxf`

**"No module named 'svg.path'"**:
- Install with: `pip3 install svg.path`

**Application won't start**:
- Make sure Python 3 is installed: `python3 --version`
- Check that tkinter is available (usually pre-installed on macOS)

