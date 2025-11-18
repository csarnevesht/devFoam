name: "CAD to G-code Converter for Hot-Wire Foam Cutting"
description: |

## Purpose
Build a comprehensive toolchain for converting CAD files (DXF, SVG, JSON) into G-code for hot-wire foam cutting machines. The system includes a core G-code generator engine and an integrated GUI application with visual CAD viewer, interactive path configuration, and real-time G-code generation.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md

---

## Goal
Create a production-ready CAD to G-code conversion system for hot-wire foam cutting that:
- Loads and displays CAD files (DXF with bulge values, SVG, JSON) with accurate rendering
- Provides interactive visual editing with corner snapping and coordinate conversion
- Generates G-code with tool radius compensation, contour ordering, and path planning
- Offers visual feedback with directional arrows showing cutting paths
- Supports configurable start/entry/exit points for each shape
- Handles inner/outer contour classification automatically
- Generates safe G-code with proper retraction and linking moves

## Why
- **Business value**: Enables precise foam cutting for aerospace, RC models, signage, and prototyping
- **Integration**: Combines CAD visualization with G-code generation in one tool
- **Problems solved**:
  - Manual G-code generation is error-prone and time-consuming
  - Tool radius compensation requires complex offset calculations
  - Path planning (entry/exit points, direction) needs visual feedback
  - Existing tools lack integrated CAD viewer with interactive editing

## What
A two-component system:

### 1. G-code Generator (`gcode_generator.py`)
Core engine that generates G-code with:
- Tool radius compensation (offsetting)
- Inner/outer contour classification and ordering
- Lead-in/lead-out moves
- Safe linking moves between contours
- Support for lines, arcs (G2/G3), circles, and polylines

### 2. CAD to G-code Converter (`cad_to_gcode.py`)
GUI application with:
- Interactive CAD viewer with auto-scaling and centering
- File loading for DXF (with LWPOLYLINE and bulge values), SVG, and JSON
- Visual path configuration (start points, entry/exit points, direction)
- Real-time visual feedback with directional arrows and markers
- Coordinate conversion between canvas (Y-down) and CAD (Y-up) systems
- Corner snapping (50 CAD unit threshold) for precise point selection
- G-code preview and export

### Success Criteria
- [ ] Load and render DXF files with LWPOLYLINE bulge values correctly
- [ ] Load and render SVG and JSON files accurately
- [ ] Interactive canvas with accurate coordinate conversion (Y-axis flip)
- [ ] Corner snapping works within 50 CAD unit threshold
- [ ] Tool radius offsetting generates correct paths (outer offset out, inner offset in)
- [ ] Contour classification identifies inner/outer automatically
- [ ] Visual feedback shows cutting direction with green arrows
- [ ] Start/entry/exit point configuration updates in real-time
- [ ] Generated G-code follows standards (G21, G90, G17, M3/M5, M30)
- [ ] G-code includes safe retraction and linking moves
- [ ] All tests pass with 80%+ coverage

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

# DXF Handling with ezdxf
- url: https://ezdxf.readthedocs.io/en/stable/dxfentities/lwpolyline.html
  why: CRITICAL - LWPOLYLINE bulge value handling, get_points() returns (x, y, start_width, end_width, bulge)
  critical: Bulge is at index 4, NOT a separate method. Bulge value defines arc segments between points.

- url: https://ezdxf.readthedocs.io/en/stable/tutorials/lwpolyline.html
  why: Tutorial showing practical LWPOLYLINE usage patterns
  critical: entity.get_points() returns list of tuples, bulge at index [4]

- url: https://ezdxf.readthedocs.io/en/stable/math/core.html
  why: bulge_to_arc() and arc_to_bulge() helper functions for converting bulge to arc parameters

# Font Rendering with fontTools
- url: https://fonttools.readthedocs.io/en/latest/pens/index.html
  why: Glyph extraction using RecordingPen for font rendering in sign generation
  critical: Use RecordingPen to extract glyph outlines as Bezier curves

# Tool Radius Compensation
- url: https://github.com/jbuckmccready/CavalierContours
  why: Reference implementation of polyline offsetting with arc segments
  critical: Edge-based offsetting with self-intersection detection

- url: http://fcacciola.50webs.com/Offseting%20Methods.htm
  why: Comprehensive survey of polygon offsetting strategies and algorithms
  critical: Offset direction based on signed area (CCW=outer=offset out, CW=inner=offset in)

# G-code Standards for Foam Cutting
- url: https://cnchotwiresoftware.com/
  why: G-code conventions for hot-wire foam cutting machines
  critical: G21 (mm), G90 (absolute), G17 (XY plane), M3 (spindle on), M5 (spindle off), M30 (end)

- url: https://rckeith.co.uk/how-to-use-jedicut-g-code-with-grbl-4-axis-cnc-foam-cutter/
  why: Practical G-code generation patterns for foam cutters

# Tkinter Canvas Coordinate System
- url: https://stackoverflow.com/questions/41652978/tkinter-set-0-0-coords-on-the-bottom-of-a-canvas
  why: Y-axis conversion between CAD (Y-up) and canvas (Y-down) coordinate systems
  critical: tkinter_y = canvas_height - cad_y - offset_y for accurate conversion

# Existing Codebase Files to Reference
- file: gcode_generator.py
  why: Core class pattern for G-code generation with methods for header, footer, moves
  pattern: Class-based with setter methods, line-by-line G-code accumulation

- file: cad_to_gcode.py
  why: GUI structure with Tkinter, canvas rendering, coordinate conversion, click handlers
  pattern: Main app class, setup_ui() method, separate frames for controls and canvas

- file: DESIGN_DOCUMENT.md
  why: Complete architecture, algorithms, data structures, UI workflow
  critical: Signed area for orientation, offset algorithm, contour ordering rules

- file: INITIAL.md
  why: Lists all 10 critical gotchas discovered during implementation
  critical: MUST READ to avoid repeating implementation mistakes

- file: Gcode_Generator_Requirements.md
  why: Detailed requirements specification
```

### Current Codebase Tree
```bash
/Users/carolinasarneveshtair/devfoam
├── CLAUDE.md                      # Project conventions
├── DESIGN_DOCUMENT.md             # Architecture reference
├── Gcode_Generator_Requirements.md
├── INITIAL.md                     # Feature description with gotchas
├── README.md
├── README_CAD.md
├── README_GCODE.md
├── cad_to_gcode.py               # GUI application
├── cad_viewer.py
├── gcode_generator.py            # Core generator
├── create_devfoam_sign.py        # Example usage
├── create_devfoam_sign_v2.py
├── create_devfoam_sign_v3.py
├── requirements.txt
├── sample_*.json                  # Test files
├── sample_*.svg
├── sample_*.dxf
└── PRPs/
    ├── EXAMPLE_multi_agent_prp.md
    └── templates/
        └── prp_base.md
```

### Desired Codebase Tree (Files to Create/Modify)
```bash
/Users/carolinasarneveshtair/devfoam
├── gcode_generator.py            # Core G-code generator class
├── cad_to_gcode.py              # GUI application with CAD viewer
├── requirements.txt              # Dependencies (ezdxf, fontTools, svg.path)
├── tests/                        # NEW: Test suite
│   ├── __init__.py
│   ├── test_gcode_generator.py  # Test G-code generation
│   ├── test_cad_loader.py       # Test file loading (DXF, SVG, JSON)
│   ├── test_offsetting.py       # Test tool radius compensation
│   ├── test_coordinate_conversion.py  # Test canvas↔CAD conversion
│   └── test_contour_classification.py # Test inner/outer detection
├── DESIGN_DOCUMENT.md            # Architecture documentation
├── README.md                     # User documentation
└── samples/                      # Example files for testing
    ├── sample_simple_shape.json
    ├── sample_sign.dxf
    └── sample_simple.svg
```

### Known Gotchas & Library Quirks
```python
# ==========================================
# CRITICAL GOTCHAS - MUST HANDLE CORRECTLY
# ==========================================

# 1. DXF LWPOLYLINE Bulge Values
# CRITICAL: Use entity.get_points() which returns tuples (x, y, start_width, end_width, bulge)
# Bulge is at index 4, NOT entity.bulge_values() (that method doesn't exist)
# Bulge values represent arc segments between consecutive points
# Example:
points = entity.get_points('xyb')  # Get x, y, bulge only
for x, y, bulge in points:
    if abs(bulge) > 0.0001:
        # This is an arc segment from this point to the next
        pass

# 2. Coordinate System Conversion (MAJOR BUG SOURCE)
# CRITICAL: Canvas Y-axis is inverted (top-down) vs CAD Y-axis (bottom-up)
# Must flip Y when converting: cad_y = (canvas_height - canvas_y - offset_y) / scale
# This was a major bug source - clicks weren't registering correctly
# Always convert BEFORE any distance calculations or snapping checks

# 3. Corner Snapping
# Threshold is 50 CAD units (not pixels) - must convert click coordinates FIRST
# Check both vertex proximity AND line segment proximity
# Snap to nearest endpoint when clicking on line segments

# 4. Font Rendering Transform Order
# CRITICAL: fontTools.misc.transform.Transform applies transformations right-to-left
# Correct: Transform().translate(x, y).scale(scale, scale)  # scale first, then translate
# Wrong: Transform().scale(scale, scale).translate(x, y)    # would translate first, then scale

# 5. Arc Rendering in Tkinter
# Tkinter's create_arc uses different angle conventions than CAD
# Must flip angles: start=180-end_angle for proper display
# Extent must be normalized to -360 to 360 range

# 6. Tool Radius Offsetting
# CRITICAL: Outer contours offset outward, inner holes offset inward
# Use signed area to determine contour type (positive = CCW = outer)
# Collapsed contours (tool radius too large) must be detected and skipped
# Algorithm: offset each vertex perpendicular to average of adjacent edges

# 7. Path Direction
# CRITICAL: Outer contours should be CCW, inner holes should be CW
# Arrows must respect start_index and clockwise settings
# Reorder points array based on start_index before drawing arrows

# 8. Edit Mode State Management
# Edit mode must be explicitly toggled via checkbox
# Canvas click handler always bound, but only processes when edit_mode is True
# Selected shape index must be tracked separately from edit mode state

# 9. Shape Metadata Storage
# Start/entry/exit indices stored directly in shape dict
# Must validate indices are within bounds before accessing
# Dropdowns must be populated with valid vertex indices only

# 10. G-code Generation Safety
# CRITICAL: Always retract to safe height between contours
# Lead-in/lead-out must be added to path points, not just G-code
# Linking moves use G0 (rapid) at safe height
# Plunge uses separate plunge_feed_rate, cutting uses cut_feed_rate
```

## Implementation Blueprint

### Data Models and Structure

```python
# Core data structures to use throughout implementation

# Point representation (simple tuple or dataclass)
Point2D = Tuple[float, float]  # (x, y)

# Shape representation in CAD data
class Shape:
    """
    Represents a loaded CAD shape with metadata.

    Attributes:
        type: str - 'line', 'circle', 'arc', 'polyline'
        points: List[Point2D] - Vertices of the shape
        closed: bool - Whether shape is closed
        start_index: Optional[int] - User-selected start vertex
        entry_index: Optional[int] - Entry point for tool
        exit_index: Optional[int] - Exit point for tool
        clockwise: Optional[bool] - Direction override
    """
    pass

# G-code generator settings
class MachiningParameters:
    """
    Parameters for G-code generation.

    Attributes:
        units: str - 'mm' or 'inches'
        feed_rate: float - Cutting feed rate (mm/min)
        plunge_rate: float - Plunge feed rate (mm/min)
        tool_radius: float - Tool radius for offsetting
        cut_depth: float - Cutting depth
        safety_height: float - Safe Z height for moves
        curve_tolerance: float - Polygonization tolerance
        lead_in_length: float - Lead-in/out length
        wire_temp: float - Wire temperature setting
    """
    pass

# Contour classification
class Contour:
    """
    Classified contour with offset path.

    Attributes:
        points: List[Point2D] - Offset path points
        is_outer: bool - True if outer contour, False if inner hole
        original_points: List[Point2D] - Original points before offset
    """
    pass
```

### List of Tasks (Implementation Order)

```yaml
Task 1: Setup Project Structure and Dependencies
CREATE requirements.txt:
  - ezdxf>=1.0.0  # DXF file support
  - fontTools>=4.0.0  # Font rendering
  - svg.path>=1.5.0  # SVG support
  - PATTERN: Follow existing requirements.txt format

CREATE tests/ directory structure:
  - tests/__init__.py
  - tests/test_gcode_generator.py
  - tests/test_cad_loader.py
  - tests/test_offsetting.py

Task 2: Implement G-code Generator Core Class
CREATE gcode_generator.py:
  - PATTERN: Class-based design with setter methods
  - Implement __init__ with default parameters
  - Add header() method: Generate G21, G90, G17, M3, safe Z
  - Add footer() method: Generate safe Z, M5, G0 X0 Y0, M30
  - Add rapid_move(x, y, z): Generate G0 commands
  - Add linear_move(x, y, z, feed): Generate G1 commands
  - Add arc_move(x, y, i, j, clockwise): Generate G2/G3 commands
  - Track current position (current_x, current_y, current_z)
  - Accumulate G-code lines in self.lines list

Task 3: Add Contour Cutting Methods to G-code Generator
MODIFY gcode_generator.py:
  - FIND: class GCodeGenerator
  - ADD cut_contour(points, closed=True) method
    - PATTERN: Iterate points, generate linear_move for each
    - Handle closed contours (return to start)
    - Add comments for debugging
  - ADD cut_circle(center, radius) method
    - PATTERN: Use arc_move for full circle (two 180° arcs)
  - ADD cut_arc(start, end, center, clockwise) method
    - PATTERN: Calculate I, J offsets from start to center

Task 4: Implement Tool Radius Offsetting Algorithm
ADD to gcode_generator.py:
  - ADD calculate_signed_area(points) function
    - PATTERN: Shoelace formula to determine orientation
    - Positive area = CCW = outer contour
    - Negative area = CW = inner hole

  - ADD offset_polygon(points, tool_radius, is_outer) function
    - CRITICAL: Use perpendicular offset based on edge normals
    - For each vertex, calculate average perpendicular from adjacent edges
    - Offset outward for outer, inward for inner
    - Detect collapsed contours (points too close)
    - Return None if contour collapses
    - PATTERN: See DESIGN_DOCUMENT.md section 4.3

Task 5: Add Contour Classification and Ordering
ADD to gcode_generator.py:
  - ADD classify_contours(contours) function
    - Use signed area to determine inner vs outer
    - Return list of classified contours

  - ADD order_contours(contours) function
    - CRITICAL: Inner holes before outer boundaries
    - Left-to-right ordering (sort by min X)
    - PATTERN: inner + outer (inner first)

Task 6: Implement DXF File Loader
CREATE cad_to_gcode.py (begin GUI app):
  - PATTERN: Use tkinter for GUI framework
  - ADD load_dxf(filename) method
    - Use ezdxf.readfile(filename)
    - Iterate modelspace entities
    - Handle LINE: extract start, end points
    - Handle CIRCLE: extract center, radius
    - Handle ARC: extract start, end, center, angles
    - Handle LWPOLYLINE:
      - CRITICAL: Use entity.get_points('xyb') to get x, y, bulge
      - Bulge at index 2 (when using 'xyb' format)
      - Convert bulge to arc segments using ezdxf.math.bulge_to_arc()
      - Store as polyline with arc segments
    - Return list of Shape objects

Task 7: Implement SVG and JSON File Loaders
ADD to cad_to_gcode.py:
  - ADD load_svg(filename) method
    - Use svg.path library to parse paths
    - Convert paths to polylines
    - PATTERN: Similar to DXF loader structure

  - ADD load_json(filename) method
    - Parse JSON with standard library
    - Expect format: {"shapes": [{"type": "line", "points": [[x,y], ...]}]}
    - PATTERN: Simple dict parsing

Task 8: Create Tkinter GUI Framework
MODIFY cad_to_gcode.py:
  - CREATE CADToGCodeConverter class
    - PATTERN: Follow existing cad_to_gcode.py structure
    - __init__(root): Initialize Tkinter root window
    - setup_ui(): Create UI layout
      - Left panel: File loading, canvas, edit controls
      - Right panel: G-code settings
    - Create canvas with scrollbars (400x300 default)
    - Create input fields for all MachiningParameters
    - Create "Load CAD File", "Generate G-code", "Save G-code" buttons

Task 9: Implement Canvas Rendering with Coordinate Conversion
ADD to CADToGCodeConverter class:
  - ADD canvas_to_cad(canvas_x, canvas_y) method
    - CRITICAL: Y-axis flip: cad_y = (canvas_height - canvas_y - offset_y) / scale
    - Also convert X: cad_x = (canvas_x - offset_x) / scale

  - ADD cad_to_canvas(cad_x, cad_y) method
    - CRITICAL: Reverse conversion: canvas_y = canvas_height - (cad_y * scale + offset_y)
    - canvas_x = cad_x * scale + offset_x

  - ADD update_shapes_list() method
    - Auto-scale shapes to fit canvas
    - Center shapes on canvas
    - Iterate shapes and render based on type:
      - LINE: canvas.create_line()
      - CIRCLE: canvas.create_oval()
      - ARC: canvas.create_arc() with angle adjustment
      - POLYLINE: canvas.create_line() with multiple points
    - Apply coordinate conversion to all points

Task 10: Implement Interactive Editing with Corner Snapping
ADD to CADToGCodeConverter class:
  - ADD toggle_edit_mode() method
    - Set self.edit_mode = True/False
    - Update UI to show edit mode active

  - ADD on_canvas_click(event) method
    - CRITICAL: Convert click coordinates to CAD first
    - cad_click = canvas_to_cad(event.x, event.y)
    - CRITICAL: Snap threshold is 50 CAD units (not pixels)
    - For each shape:
      - Check vertex proximity: distance < 50 CAD units
      - Check line segment proximity
    - If snap found:
      - Set self.selected_shape_index
      - Update UI dropdowns
      - Redraw canvas with selection highlighted

Task 11: Add Visual Feedback (Markers and Arrows)
ADD to CADToGCodeConverter class:
  - ADD draw_path_arrows(points, scale, offset_x, offset_y, canvas_height, shape) method
    - Calculate total path length
    - Determine arrow spacing (e.g., every 20mm)
    - For each arrow position:
      - Calculate tangent direction
      - Draw small green arrow in cutting direction
    - CRITICAL: Respect start_index and direction settings
    - Reorder points based on start_index before drawing

  - ADD draw_point_markers(shape) method
    - START point: Green circle with "START" label
    - ENTRY point: Blue circle with "ENTRY" label
    - EXIT point: Red circle with "EXIT" label
    - CRITICAL: Convert CAD coordinates to canvas for drawing

Task 12: Implement Start/Entry/Exit Point Configuration
ADD to CADToGCodeConverter class:
  - ADD on_start_point_changed(event) method
    - Update shape.start_index from dropdown
    - Redraw canvas with updated markers

  - ADD on_entry_point_changed(event) method
    - Update shape.entry_index from dropdown
    - Redraw canvas

  - ADD on_exit_point_changed(event) method
    - Update shape.exit_index from dropdown
    - Redraw canvas

  - ADD on_direction_changed(event) method
    - Update shape.clockwise from dropdown
    - Redraw arrows in new direction

Task 13: Integrate G-code Generation with GUI
ADD to CADToGCodeConverter class:
  - ADD generate_gcode() method
    - Read parameters from UI inputs
    - Create GCodeGenerator instance
    - Set all parameters (feed rate, tool radius, etc.)
    - For each shape:
      - Apply tool radius offsetting
      - Classify as inner/outer
    - Order contours (inner first, then outer, left-to-right)
    - For each ordered contour:
      - Add lead-in segment
      - Cut contour path
      - Add lead-out segment
      - Add linking move to next contour
    - Display G-code in preview text area

  - ADD save_gcode() method
    - Open file dialog
    - Write self.gcode_lines to file

Task 14: Create Comprehensive Test Suite
CREATE tests/test_gcode_generator.py:
  - PATTERN: Use pytest framework (as per CLAUDE.md)
  - test_header_generation(): Verify G21, G90, G17, M3 present
  - test_footer_generation(): Verify M5, M30, return to origin
  - test_linear_move(): Verify G1 with correct coordinates
  - test_arc_move(): Verify G2/G3 with I, J offsets
  - test_rapid_move(): Verify G0 commands

CREATE tests/test_offsetting.py:
  - test_signed_area_ccw(): Verify CCW polygon has positive area
  - test_signed_area_cw(): Verify CW polygon has negative area
  - test_offset_outer_contour(): Verify offset goes outward
  - test_offset_inner_contour(): Verify offset goes inward
  - test_collapsed_contour_detection(): Verify None returned when tool radius too large

CREATE tests/test_coordinate_conversion.py:
  - test_canvas_to_cad_conversion(): Verify Y-axis flip
  - test_cad_to_canvas_conversion(): Verify reverse conversion
  - test_conversion_round_trip(): Verify accuracy

CREATE tests/test_cad_loader.py:
  - test_load_dxf_line(): Verify LINE entity loaded correctly
  - test_load_dxf_circle(): Verify CIRCLE entity
  - test_load_dxf_lwpolyline_with_bulge(): CRITICAL test for bulge handling
  - test_load_json(): Verify JSON parsing
  - test_load_svg(): Verify SVG parsing

Task 15: Add Documentation
UPDATE README.md:
  - PATTERN: Follow existing README structure
  - Add installation instructions
  - Add usage examples
  - Add screenshots/diagrams

VERIFY DESIGN_DOCUMENT.md is complete:
  - Architecture overview
  - Algorithm descriptions
  - Data structures
  - UI workflow
```

### Per-Task Pseudocode (Key Tasks Only)

```python
# ========================================
# Task 4: Tool Radius Offsetting (CRITICAL)
# ========================================

def calculate_signed_area(points: List[Point2D]) -> float:
    """
    Calculate signed area using shoelace formula.
    Positive = CCW = outer contour
    Negative = CW = inner hole
    """
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return area / 2.0

def offset_polygon(points: List[Point2D], tool_radius: float,
                   is_outer: bool) -> Optional[List[Point2D]]:
    """
    Offset polygon by tool radius.
    CRITICAL: Outer offsets outward, inner offsets inward.
    """
    if len(points) < 3:
        return None

    offset_distance = tool_radius
    # CRITICAL: Direction based on contour type
    offset_direction = 1.0 if is_outer else -1.0

    offset_points = []
    n = len(points)

    for i in range(n):
        prev = points[(i - 1) % n]
        curr = points[i]
        next_pt = points[(i + 1) % n]

        # Edge vectors
        edge1 = normalize(vector_subtract(curr, prev))
        edge2 = normalize(vector_subtract(next_pt, curr))

        # Perpendicular vectors (rotate 90° CCW)
        perp1 = (-edge1[1], edge1[0])
        perp2 = (-edge2[1], edge2[0])

        # Average perpendicular direction
        perp_avg_x = (perp1[0] + perp2[0]) / 2
        perp_avg_y = (perp1[1] + perp2[1]) / 2
        perp_avg = normalize((perp_avg_x, perp_avg_y))

        # Offset point
        offset_x = curr[0] + perp_avg[0] * offset_distance * offset_direction
        offset_y = curr[1] + perp_avg[1] * offset_distance * offset_direction
        offset_points.append((offset_x, offset_y))

    # CRITICAL: Check for collapsed contour
    # If any adjacent points too close, contour collapsed
    for i in range(len(offset_points)):
        j = (i + 1) % len(offset_points)
        dist = distance(offset_points[i], offset_points[j])
        if dist < tool_radius * 0.1:  # Threshold for collapse
            return None  # Collapsed contour

    return offset_points

# ========================================
# Task 9: Coordinate Conversion (CRITICAL)
# ========================================

def canvas_to_cad(self, canvas_x: float, canvas_y: float) -> Point2D:
    """
    Convert canvas coordinates to CAD coordinates.
    CRITICAL: Y-axis is inverted between systems.
    """
    # Get canvas dimensions
    canvas_height = self.canvas.winfo_height()

    # Convert with Y-axis flip
    cad_x = (canvas_x - self.canvas_offset_x) / self.canvas_scale
    cad_y = (canvas_height - canvas_y - self.canvas_offset_y) / self.canvas_scale

    return (cad_x, cad_y)

def cad_to_canvas(self, cad_x: float, cad_y: float) -> Point2D:
    """
    Convert CAD coordinates to canvas coordinates.
    CRITICAL: Reverse Y-axis conversion.
    """
    canvas_height = self.canvas.winfo_height()

    # Convert with Y-axis flip
    canvas_x = cad_x * self.canvas_scale + self.canvas_offset_x
    canvas_y = canvas_height - (cad_y * self.canvas_scale + self.canvas_offset_y)

    return (canvas_x, canvas_y)

# ========================================
# Task 10: Corner Snapping (CRITICAL)
# ========================================

def on_canvas_click(self, event):
    """
    Handle canvas click for shape selection.
    CRITICAL: Snap threshold is 50 CAD units, not pixels.
    """
    if not self.edit_mode:
        return  # Only process in edit mode

    # CRITICAL: Convert click to CAD coordinates FIRST
    click_cad = self.canvas_to_cad(event.x, event.y)

    # Visual feedback: draw yellow circle at click location
    canvas_click = (event.x, event.y)
    self.canvas.create_oval(
        canvas_click[0] - 5, canvas_click[1] - 5,
        canvas_click[0] + 5, canvas_click[1] + 5,
        fill='yellow', outline='yellow', tags='click_feedback'
    )
    # Remove after 500ms
    self.root.after(500, lambda: self.canvas.delete('click_feedback'))

    # CRITICAL: Snap threshold in CAD units
    snap_threshold = 50.0  # CAD units, NOT pixels

    closest_shape_idx = None
    closest_vertex_idx = None
    closest_dist = float('inf')

    # Check all shapes
    for shape_idx, shape in enumerate(self.shapes):
        points = shape['points']

        # Check vertex proximity
        for vertex_idx, point in enumerate(points):
            dist = distance(click_cad, point)
            if dist < snap_threshold and dist < closest_dist:
                closest_dist = dist
                closest_shape_idx = shape_idx
                closest_vertex_idx = vertex_idx

        # Also check line segment proximity
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            dist = point_to_line_distance(click_cad, p1, p2)
            if dist < snap_threshold and dist < closest_dist:
                # Snap to nearest endpoint
                dist1 = distance(click_cad, p1)
                dist2 = distance(click_cad, p2)
                closest_dist = min(dist1, dist2)
                closest_shape_idx = shape_idx
                closest_vertex_idx = i if dist1 < dist2 else i + 1

    if closest_shape_idx is not None:
        # Shape selected!
        self.selected_shape_index = closest_shape_idx
        selected_shape = self.shapes[closest_shape_idx]

        # Update start_index if not set
        if selected_shape.get('start_index') is None:
            selected_shape['start_index'] = closest_vertex_idx

        # Update UI controls
        self.update_selection_ui()

        # Redraw with selection highlighted
        self.update_shapes_list()

# ========================================
# Task 6: DXF LWPOLYLINE Bulge Handling (CRITICAL)
# ========================================

def load_dxf(self, filename: str) -> List[dict]:
    """
    Load DXF file and extract shapes.
    CRITICAL: Handle LWPOLYLINE bulge values correctly.
    """
    if not HAS_EZDXF:
        raise ImportError("ezdxf library required for DXF support")

    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    shapes = []

    for entity in msp:
        if entity.dxftype() == 'LINE':
            # Simple line
            start = (entity.dxf.start.x, entity.dxf.start.y)
            end = (entity.dxf.end.x, entity.dxf.end.y)
            shapes.append({
                'type': 'line',
                'points': [start, end]
            })

        elif entity.dxftype() == 'CIRCLE':
            # Circle
            center = (entity.dxf.center.x, entity.dxf.center.y)
            radius = entity.dxf.radius
            shapes.append({
                'type': 'circle',
                'center': center,
                'radius': radius
            })

        elif entity.dxftype() == 'LWPOLYLINE':
            # CRITICAL: Handle bulge values
            points = []

            # CRITICAL: Use get_points() which returns (x, y, start_width, end_width, bulge)
            for x, y, start_width, end_width, bulge in entity.get_points('xyseb'):
                points.append((x, y))

                # CRITICAL: Bulge represents arc segment to NEXT point
                if abs(bulge) > 0.0001 and len(points) > 1:
                    # This segment is an arc, not a line
                    # Convert bulge to arc parameters
                    start_point = points[-2]
                    end_point = points[-1]

                    # Use ezdxf helper to convert bulge to arc
                    from ezdxf.math import bulge_to_arc
                    center, start_angle, end_angle, radius = bulge_to_arc(
                        start_point, end_point, bulge
                    )

                    # Store arc information with the segment
                    # For rendering, interpolate arc into small line segments
                    arc_points = interpolate_arc(
                        start_point, end_point, center,
                        start_angle, end_angle, radius,
                        tolerance=self.curve_tolerance
                    )

                    # Replace last point with arc points
                    points = points[:-1] + arc_points

            shapes.append({
                'type': 'polyline',
                'points': points,
                'closed': entity.closed
            })

    return shapes
```

### Integration Points
```yaml
DEPENDENCIES:
  requirements.txt:
    - ezdxf>=1.0.0  # DXF file support
    - fontTools>=4.0.0  # Font rendering (optional, for sign generation)
    - svg.path>=1.5.0  # SVG file support (optional)
    # Note: tkinter included with Python

ENVIRONMENT:
  - Python 3.7+ required
  - Tkinter display support (built-in on macOS, Linux, Windows)

CONFIGURATION:
  Default parameters:
    - units: mm
    - feed_rate: 100 mm/min
    - plunge_rate: 50 mm/min
    - tool_radius: 0 mm (no offsetting by default)
    - safety_height: 10 mm
    - cut_depth: 0 mm
    - curve_tolerance: 0.1 mm
    - lead_in_length: 2.0 mm

FILE_FORMATS:
  DXF:
    - Support LINE, CIRCLE, ARC, LWPOLYLINE entities
    - CRITICAL: Handle LWPOLYLINE bulge values for arc segments
  SVG:
    - Parse path elements
    - Convert to polylines
  JSON:
    - Format: {"shapes": [{"type": "line", "points": [[x,y], ...]}]}
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
# Note: No ruff/mypy mentioned in existing codebase, but use if available
python3 -m py_compile gcode_generator.py
python3 -m py_compile cad_to_gcode.py

# Check for syntax errors
# Expected: No errors. If errors, READ and fix.
```

### Level 2: Unit Tests
```python
# test_gcode_generator.py - Core G-code generation tests
def test_header_generation():
    """Test G-code header includes required commands"""
    gen = GCodeGenerator()
    gen.header("Test")
    gcode = "\n".join(gen.lines)
    assert "G21" in gcode  # Units
    assert "G90" in gcode  # Absolute positioning
    assert "G17" in gcode  # XY plane
    assert "M3" in gcode   # Spindle on
    assert f"G0 Z{gen.safety_height}" in gcode

def test_footer_generation():
    """Test G-code footer includes required commands"""
    gen = GCodeGenerator()
    gen.footer()
    gcode = "\n".join(gen.lines)
    assert "M5" in gcode   # Spindle off
    assert "M30" in gcode  # Program end
    assert "G0 X0 Y0" in gcode  # Return to origin

def test_tool_radius_offsetting():
    """Test tool radius offsetting direction"""
    # Outer contour (CCW square)
    outer = [(0, 0), (10, 0), (10, 10), (0, 10)]
    area = calculate_signed_area(outer)
    assert area > 0, "CCW square should have positive area"

    # Offset outward
    offset = offset_polygon(outer, tool_radius=1.0, is_outer=True)
    assert offset is not None
    # Check that offset points are outside original
    assert offset[0][0] < 0  # Left side moved left
    assert offset[1][0] > 10  # Right side moved right

# test_coordinate_conversion.py - Canvas ↔ CAD conversion
def test_canvas_to_cad_y_flip():
    """Test Y-axis flip in coordinate conversion"""
    app = CADToGCodeConverter(tk.Tk())
    app.canvas_scale = 1.0
    app.canvas_offset_x = 0
    app.canvas_offset_y = 0
    canvas_height = 300

    # Canvas (0, 0) = top-left should map to CAD (0, 300)
    cad_x, cad_y = app.canvas_to_cad(0, 0)
    assert cad_y == canvas_height, "Top of canvas should be max Y in CAD"

    # Canvas (0, 300) = bottom-left should map to CAD (0, 0)
    cad_x, cad_y = app.canvas_to_cad(0, canvas_height)
    assert cad_y == 0, "Bottom of canvas should be Y=0 in CAD"

# test_cad_loader.py - File loading tests
def test_load_dxf_lwpolyline_with_bulge():
    """Test DXF LWPOLYLINE with bulge values (CRITICAL)"""
    # Create test DXF with LWPOLYLINE containing arc
    doc = ezdxf.new()
    msp = doc.modelspace()
    # Add LWPOLYLINE with bulge
    polyline = msp.add_lwpolyline([(0, 0), (10, 0), (10, 10)])
    polyline.bulges = [0.5, 0, 0]  # Arc on first segment
    doc.saveas('test_bulge.dxf')

    # Load and verify
    app = CADToGCodeConverter(tk.Tk())
    shapes = app.load_dxf('test_bulge.dxf')
    assert len(shapes) > 0
    # Should have interpolated arc into multiple points
    assert len(shapes[0]['points']) > 3
```

```bash
# Run tests iteratively until passing:
# Note: Use pytest if available (per CLAUDE.md), otherwise unittest
pytest tests/ -v
# OR
python3 -m pytest tests/ -v

# If failing: Debug specific test, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test GUI application
python3 cad_to_gcode.py

# Manual test steps:
# 1. Click "Load CAD File"
# 2. Select sample_sign.dxf
# 3. Verify shapes render on canvas
# 4. Enable "Edit Mode"
# 5. Click on a shape corner - should snap and highlight
# 6. Select start point from dropdown
# 7. Verify green "START" marker appears
# 8. Set tool radius to 1.0
# 9. Click "Generate G-code"
# 10. Verify G-code appears in preview
# 11. Check G-code contains:
#     - G21, G90, G17, M3 in header
#     - G1 moves for cutting
#     - G0 moves for linking with safe Z
#     - M5, M30 in footer
# 12. Click "Save G-code File"
# 13. Verify file saved

# Expected: All steps work without errors
```

## Final Validation Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] GUI launches without errors: `python3 cad_to_gcode.py`
- [ ] DXF files with bulge values load correctly
- [ ] Canvas rendering shows shapes accurately
- [ ] Coordinate conversion works (click accuracy)
- [ ] Corner snapping works within 50 CAD units
- [ ] Tool radius offsetting generates correct paths
- [ ] Inner/outer contour classification correct
- [ ] G-code header contains G21, G90, G17, M3
- [ ] G-code footer contains M5, M30
- [ ] Safe retraction between contours (G0 Z at safe height)
- [ ] Manual test of full workflow successful
- [ ] DESIGN_DOCUMENT.md accurately describes implementation
- [ ] README.md provides clear usage instructions

---

## Anti-Patterns to Avoid
- ❌ Don't use entity.bulge_values() - it doesn't exist, use get_points()[4]
- ❌ Don't forget Y-axis flip in coordinate conversion
- ❌ Don't use pixel-based snap threshold - use CAD units
- ❌ Don't apply font transforms in wrong order (scale then translate)
- ❌ Don't offset inner and outer contours in same direction
- ❌ Don't skip safe retraction between contours - safety critical
- ❌ Don't forget to check for collapsed contours after offsetting
- ❌ Don't hard-code canvas dimensions - use winfo_height()
- ❌ Don't process clicks when edit_mode is False
- ❌ Don't skip validation of start/entry/exit indices bounds

## Confidence Score: 9/10

**High confidence** due to:
- Comprehensive existing documentation (DESIGN_DOCUMENT.md, INITIAL.md)
- Clear implementation already exists to reference
- Well-documented external libraries (ezdxf, fontTools)
- All critical gotchas identified and documented
- Established patterns from working codebase
- Detailed algorithms in DESIGN_DOCUMENT.md
- Extensive research on polygon offsetting, G-code standards, coordinate conversion

**Minor uncertainty** on:
- Test coverage achieving 80%+ without existing test infrastructure
- Edge cases in polygon offsetting for very complex shapes with self-intersections
- Performance with very large DXF files (1000+ entities)

**Mitigations**:
- Start with simple test cases and expand coverage iteratively
- Use validation loop to catch and fix edge cases
- Implement error handling for collapsed contours and invalid geometry
- Follow DESIGN_DOCUMENT.md algorithms closely - they're proven to work
