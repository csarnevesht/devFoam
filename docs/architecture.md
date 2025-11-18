# Architecture: gcode_generator.py vs cad_to_gcode.py

## Overview

**`gcode_generator.py`** and **`cad_to_gcode.py`** work together in a layered architecture:

```
┌─────────────────────────────────────────┐
│   cad_to_gcode.py (GUI Application)    │
│   - User interface (Tkinter)            │
│   - CAD file loading (DXF/SVG/JSON)      │
│   - Visual preview canvas                │
│   - Interactive path configuration       │
│   - Parameter input forms               │
└─────────────────┬───────────────────────┘
                  │ uses
                  ▼
┌─────────────────────────────────────────┐
│   gcode_generator.py (Core Library)    │
│   - GCodeGenerator class                │
│   - G-code generation logic             │
│   - Cutting operations (contours, etc.) │
│   - File I/O (DXF import, G-code save)  │
└─────────────────────────────────────────┘
```

## Relationship

**`cad_to_gcode.py` USES `gcode_generator.py`**

- `cad_to_gcode.py` imports: `from gcode_generator import GCodeGenerator`
- `cad_to_gcode.py` creates an instance: `gen = GCodeGenerator()`
- `cad_to_gcode.py` calls methods on the generator to produce G-code

## Responsibilities

### `gcode_generator.py` (Core Engine)
- **Purpose**: Pure G-code generation library
- **Responsibilities**:
  - Generate G-code commands (G0, G1, G2, G3, etc.)
  - Handle cutting operations (contours, circles, rectangles)
  - Manage G-code state (current position, feed rates, etc.)
  - Import CAD files (DXF) and convert to shapes
  - Export G-code to files
- **Can be used**: 
  - As a library (imported by other scripts)
  - As a command-line tool (standalone execution)
- **No GUI**: Pure Python logic, no Tkinter dependencies

### `cad_to_gcode.py` (GUI Application)
- **Purpose**: User-friendly interface for G-code generation
- **Responsibilities**:
  - Provide graphical user interface (Tkinter)
  - Load and display CAD files visually
  - Allow interactive path configuration (start points, entry/exit points)
  - Show visual feedback (arrows, markers, highlights)
  - Collect user parameters (feed rates, tool radius, etc.)
  - Preview generated G-code
  - Save G-code files
- **Uses `gcode_generator.py`**: 
  - Creates `GCodeGenerator` instance
  - Passes shapes and parameters to generator
  - Calls `gen.generate_from_shapes()` to create G-code
  - Displays the result in preview window

## Data Flow

1. **User loads CAD file** → `cad_to_gcode.py` loads DXF/SVG/JSON
2. **User views shapes** → `cad_to_gcode.py` renders on canvas
3. **User configures paths** → `cad_to_gcode.py` stores metadata in shape dicts
4. **User sets parameters** → `cad_to_gcode.py` collects from UI inputs
5. **User clicks "Generate"** → `cad_to_gcode.py`:
   - Creates `GCodeGenerator()` instance
   - Sets parameters: `gen.set_feed_rate(...)`, etc.
   - Calls `gen.generate_from_shapes(self.shapes, depth)`
   - Gets result: `gcode = gen.get_gcode()`
   - Displays in preview window
6. **User saves** → `cad_to_gcode.py` calls `gen.save(filename)`

## Key Differences

| Aspect | `gcode_generator.py` | `cad_to_gcode.py` |
|--------|---------------------|-------------------|
| **Type** | Library/CLI tool | GUI Application |
| **Dependencies** | Minimal (ezdxf optional) | Requires tkinter |
| **User Interface** | Command-line or API | Graphical (Tkinter) |
| **Visualization** | None | Canvas with shapes, arrows, markers |
| **Path Configuration** | Programmatic | Interactive (click to select) |
| **Standalone** | Yes (can run alone) | Yes (but uses generator) |
| **Reusable** | Yes (import as library) | No (application entry point) |

## Example Usage

### Using `gcode_generator.py` directly (library):
```python
from gcode_generator import GCodeGenerator

gen = GCodeGenerator()
gen.set_feed_rate(150.0)
gen.header("My Cut")
gen.cut_rectangle(0, 0, 100, 50, depth=0.0)
gen.footer()
gen.save("output.nc")
```

### Using `cad_to_gcode.py` (GUI):
```bash
python3 cad_to_gcode.py
# Opens GUI, user interacts visually, generates G-code
```

## Why This Architecture?

- **Separation of Concerns**: G-code logic separate from UI logic
- **Reusability**: `gcode_generator.py` can be used by other scripts
- **Testability**: Core logic can be tested without GUI
- **Flexibility**: Can generate G-code programmatically or via GUI

