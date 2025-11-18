# G-Code Generator Design Document

## 1. Overview

### 1.1 Goal
Generate G-code that cuts text letters from a sheet of material, with correctly offset toolpaths, inner/outer contours, and safe linking moves between letters.

### 1.2 High-Level Pipeline
The system follows a sequential processing pipeline:

1. **Geometry Import** – Extract vector outlines for each glyph from font files
2. **Polygonization** – Convert Bezier curves to polylines
3. **Offsetting** – Compensate for tool radius (inside/outside)
4. **Contour Classification & Ordering** – Identify outer vs holes, determine cut order
5. **Path Planning** – Select start points, direction, lead-in/out, linking moves
6. **G-code Emission** – Transform paths into G0/G1 commands (and optional arcs)

### 1.3 Use Cases
- Cutting text letters from foam sheets
- Creating signs with multiple letters
- Precision cutting with tool radius compensation
- Safe machining with proper retraction and linking moves

---

## 2. System Architecture

### 2.1 Component Diagram
```
┌─────────────────────────────────────────────────────────┐
│                  G-Code Generator                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Font Loader   │───▶│ Polygonizer  │                │
│  └──────────────┘    └──────────────┘                │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Contour      │───▶│ Tool Offset  │                │
│  │ Extractor    │    │ Calculator   │                │
│  └──────────────┘    └──────────────┘                │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Contour      │───▶│ Path Planner │                │
│  │ Classifier   │    │              │                │
│  └──────────────┘    └──────────────┘                │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Contour      │───▶│ G-code       │                │
│  │ Orderer      │    │ Emitter      │                │
│  └──────────────┘    └──────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Visual UI (CAD to G-code Converter)       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐                │
│  │ File Loader   │───▶│ Canvas       │                │
│  │ (DXF/SVG/JSON)│    │ Renderer     │                │
│  └──────────────┘    └──────────────┘                │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Edit Mode    │───▶│ Visual        │                │
│  │ Controller   │    │ Feedback      │                │
│  └──────────────┘    └──────────────┘                │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Path Config  │───▶│ Arrow        │                │
│  │ UI           │    │ Renderer     │                │
│  └──────────────┘    └──────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow
```
Text Input → Font Glyphs → Bezier Curves → Polygons → 
Offset Polygons → Ordered Contours → Planned Paths → G-code
         │
         ▼
CAD File (DXF) → Shapes → Visual Canvas → User Interaction →
Path Configuration → G-code Generation
```

---

## 2.3 User Interface Architecture

### 2.3.1 UI Components
The system includes a graphical user interface built with Tkinter that provides:

1. **CAD File Loading Panel**
   - File browser for DXF, SVG, JSON formats
   - File status display
   - Shape count indicator

2. **Visual Canvas**
   - Interactive drawing area with scrollbars
   - Auto-scaling and centering of shapes
   - Real-time shape rendering
   - Click detection with coordinate conversion

3. **Path Control Panel (Edit Mode)**
   - Edit mode toggle
   - Shape selection display
   - Start point selector (dropdown)
   - Direction selector (Clockwise/Counter-clockwise)
   - Entry point selector
   - Exit point selector

4. **G-code Settings Panel**
   - Cutting feed rate input
   - Plunge feed rate input
   - Tool radius input
   - Cut depth input
   - Safety height input
   - Curve tolerance input
   - Lead-in/out length input
   - Units selector (mm/inches)
   - Wire temperature input
   - Generate button
   - G-code preview text area
   - Save button

### 2.3.2 Visual Feedback Features
- **Shape Highlighting**: Selected shapes shown in blue
- **Start Point Markers**: Green circles with "START" label
- **Entry Point Markers**: Blue circles with "ENTRY" label
- **Exit Point Markers**: Red circles with "EXIT" label
- **Directional Arrows**: Green arrows along paths showing cutting direction
- **Click Feedback**: Yellow circles appear at click locations
- **Edit Mode Indicator**: Blue text overlay when edit mode is active

### 2.3.3 Interactive Features
- **Corner Snapping**: Click detection snaps to nearest vertex (50 CAD unit threshold)
- **Line Segment Detection**: Clicks on line segments select the shape and nearest vertex
- **Real-time Updates**: Canvas redraws immediately when settings change
- **Coordinate Conversion**: Accurate conversion between canvas and CAD coordinates

---

## 3. Data Structures

### 3.1 Core Data Types

#### Point2D
```python
Point2D {
    x: float
    y: float
}
```

#### Segment
```python
Segment {
    type: enum {LINE, QUADRATIC_BEZIER, CUBIC_BEZIER}
    points: [Point2D]  # 2 for line, 3 for quadratic, 4 for cubic
}
```

#### Contour
```python
Contour {
    segments: [Segment]
    closed: bool
}
```

#### Glyph
```python
Glyph {
    char: str
    contours: [Contour]
    bounding_box: (min_x, min_y, max_x, max_y)
    advance_width: float
}
```

#### PolyContour
```python
PolyContour {
    points: [Point2D]  # p0..pn, where p0 = pn for closed contours
    closed: bool
    is_outer: bool  # Determined later
    parent_glyph: str  # Character this contour belongs to
}
```

#### OffsetContour
```python
OffsetContour {
    points: [Point2D]  # Tool center path
    is_outer: bool
    parent_glyph: str
    original_contour: PolyContour
}
```

#### CutJob
```python
CutJob {
    contours: [OffsetContour]  # Ordered for cutting
    parameters: MachiningParameters
}
```

#### MachiningParameters
```python
MachiningParameters {
    text: str
    font_name: str
    font_size: float
    tool_radius: float
    cut_depth: float
    safe_height: float
    cut_feed_rate: float
    plunge_feed_rate: float
    curve_tolerance: float
    lead_in_length: float
    units: str  # "mm" or "inches"
    origin_x: float
    origin_y: float
}
```

---

## 3.2 UI Data Structures

#### ShapeMetadata
```python
ShapeMetadata {
    shape_index: int
    start_index: Optional[int]  # Vertex index for start point
    entry_index: Optional[int]  # Vertex index for entry point
    exit_index: Optional[int]   # Vertex index for exit point
    clockwise: Optional[bool]    # Direction override
    original_shape: dict         # Reference to shape data
}
```

#### CanvasState
```python
CanvasState {
    shapes: [dict]              # Loaded CAD shapes
    selected_shape_index: Optional[int]
    edit_mode: bool
    canvas_scale: float         # Current zoom scale
    canvas_offset_x: float      # X offset for centering
    canvas_offset_y: float      # Y offset for centering
    snap_to_corner: bool        # Corner snapping enabled
}
```

---

## 4. Component Design

### 4.1 Geometry Import Module

#### Responsibilities
- Load font files (TrueType/OpenType)
- Extract glyph outlines as Bezier curves
- Transform glyphs to common coordinate system
- Layout text left-to-right on baseline

#### Key Functions
```python
def load_font(font_path: str) -> Font:
    """Load font file and return font object"""
    
def get_glyph_outlines(font: Font, char: str) -> [Contour]:
    """Extract Bezier curve outlines for a character"""
    
def layout_text(text: str, font: Font, size: float, 
                spacing: float) -> [Glyph]:
    """Position glyphs left-to-right on baseline Y=0"""
```

#### Coordinate System
- Baseline at Y=0
- Left-most letter starts at X=0
- Positive Y upward
- Letters positioned with proper spacing

---

### 4.2 Polygonization Module

#### Responsibilities
- Convert Bezier curves to line segments
- Ensure deviation stays within tolerance
- Maintain contour closure

#### Algorithm: Recursive Subdivision
```
function polygonize_segment(segment, tolerance):
    if segment.type == LINE:
        return [segment.points[0], segment.points[1]]
    
    if segment.type == QUADRATIC_BEZIER:
        flatness = calculate_flatness(segment)
        if flatness < tolerance:
            return [segment.points[0], segment.points[2]]
        else:
            mid = split_quadratic_bezier(segment)
            left = polygonize_segment(mid.left, tolerance)
            right = polygonize_segment(mid.right, tolerance)
            return merge(left, right)
    
    if segment.type == CUBIC_BEZIER:
        flatness = calculate_flatness(segment)
        if flatness < tolerance:
            return [segment.points[0], segment.points[3]]
        else:
            mid = split_cubic_bezier(segment)
            left = polygonize_segment(mid.left, tolerance)
            right = polygonize_segment(mid.right, tolerance)
            return merge(left, right)
```

#### Flatness Calculation
For a Bezier curve, flatness is the maximum distance from the curve to the chord connecting endpoints.

#### Key Functions
```python
def polygonize_contour(contour: Contour, tolerance: float) -> PolyContour:
    """Convert Bezier contour to polyline"""
    
def calculate_flatness(segment: Segment) -> float:
    """Calculate how flat a Bezier segment is"""
    
def split_bezier(segment: Segment) -> (Segment, Segment):
    """Split Bezier segment at midpoint using de Casteljau's algorithm"""
```

---

### 4.3 Tool Radius Compensation Module

#### Responsibilities
- Determine contour orientation (CW/CCW)
- Classify as outer or inner (hole)
- Offset contours by tool radius
- Detect and handle collapsed contours

#### Orientation Detection
```python
def signed_area(points: [Point2D]) -> float:
    """Calculate signed area using shoelace formula"""
    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    return area / 2.0
```

**Convention:**
- Positive area (CCW) = Outer contour
- Negative area (CW) = Inner hole

#### Offset Algorithm
```
function offset_contour(polygon: PolyContour, tool_radius: float, 
                       is_outer: bool) -> OffsetContour:
    offset_distance = tool_radius
    offset_direction = 1 if is_outer else -1
    
    offset_points = []
    for i in range(len(polygon.points)):
        prev_point = polygon.points[(i-1) % len(polygon.points)]
        curr_point = polygon.points[i]
        next_point = polygon.points[(i+1) % len(polygon.points)]
        
        # Calculate edge vectors
        edge1 = normalize(curr_point - prev_point)
        edge2 = normalize(next_point - curr_point)
        
        # Calculate perpendicular vectors
        perp1 = rotate_90_ccw(edge1)
        perp2 = rotate_90_ccw(edge2)
        
        # Average perpendicular direction
        perp_avg = normalize((perp1 + perp2) / 2)
        
        # Offset point
        offset_point = curr_point + perp_avg * offset_distance * offset_direction
        offset_points.append(offset_point)
    
    # Clean up: remove self-intersections, tiny loops
    offset_points = cleanup_offset(offset_points)
    
    return OffsetContour(offset_points, is_outer, polygon.parent_glyph)
```

#### Error Handling
- **Collapsed Contour**: If offset causes contour to collapse (points too close), skip and report warning
- **Self-Intersection**: Detect and resolve self-intersections in offset contour
- **Tiny Loops**: Remove loops smaller than tool radius

#### Key Functions
```python
def offset_polygon(polygon: PolyContour, tool_radius: float) -> OffsetContour:
    """Offset polygon by tool radius"""
    
def determine_contour_type(polygon: PolyContour) -> bool:
    """Return True if inner hole, False if outer"""
    
def cleanup_offset(points: [Point2D]) -> [Point2D]:
    """Remove self-intersections and tiny loops"""
```

---

### 4.4 Contour Classification & Ordering Module

#### Responsibilities
- Classify contours as inner or outer
- Order contours for safe cutting
- Group contours by glyph

#### Classification Rules
1. Calculate signed area
2. Negative area (CW) = Inner hole
3. Positive area (CCW) = Outer boundary

#### Ordering Rules
1. **Inside before outside**: Cut all inner holes before outer boundaries
2. **Left-to-right**: Process letters in reading order
3. **Optional optimization**: Nearest-neighbor heuristic to minimize travel

#### Ordering Algorithm
```python
def order_contours(offset_contours: [OffsetContour]) -> [OffsetContour]:
    # Separate inner and outer
    inner = [c for c in offset_contours if c.is_outer == False]
    outer = [c for c in offset_contours if c.is_outer == True]
    
    # Sort by X position (left-to-right)
    inner.sort(key=lambda c: min(p.x for p in c.points))
    outer.sort(key=lambda c: min(p.x for p in c.points))
    
    # Order: inner first, then outer
    return inner + outer
```

#### Key Functions
```python
def classify_contours(polygons: [PolyContour]) -> [OffsetContour]:
    """Classify and offset all contours"""
    
def order_for_cutting(contours: [OffsetContour]) -> [OffsetContour]:
    """Order contours: inner before outer, left-to-right"""
```

---

### 4.5 Path Planning Module

#### Responsibilities
- Select start points for each contour
- Determine cutting direction
- Add lead-in/lead-out segments
- Plan linking moves between contours

#### 4.5.1 Start Point Selection

**Criteria:**
- On a straight section if possible
- Not too close to sharp corners
- Prefer lowest-Y point or point closest to previous end-point

```python
def choose_start_point(contour: OffsetContour, 
                      prev_end: Point2D = None) -> int:
    """Return index of best start point"""
    if prev_end:
        # Choose point closest to previous end
        min_dist = float('inf')
        best_idx = 0
        for i, point in enumerate(contour.points):
            dist = distance(point, prev_end)
            if dist < min_dist:
                min_dist = dist
                best_idx = i
        return best_idx
    else:
        # Choose lowest Y point
        min_y = min(p.y for p in contour.points)
        for i, point in enumerate(contour.points):
            if abs(point.y - min_y) < 0.01:
                return i
        return 0
```

#### 4.5.2 Direction Control

**Convention:**
- Outer contours: Counter-clockwise (CCW)
- Inner holes: Clockwise (CW)

```python
def orient_contour(contour: OffsetContour, start_idx: int) -> [Point2D]:
    """Reorder points to start at start_idx and follow correct direction"""
    points = contour.points[start_idx:] + contour.points[:start_idx]
    
    # Check current direction
    area = signed_area(points)
    is_ccw = area > 0
    
    # Reverse if needed
    if contour.is_outer and not is_ccw:
        points = [points[0]] + list(reversed(points[1:]))
    elif not contour.is_outer and is_ccw:
        points = [points[0]] + list(reversed(points[1:]))
    
    return points
```

#### 4.5.3 Lead-in/Lead-out

**Lead-in:**
1. Rapid to start point above material (G0 at safe Z)
2. Plunge to cut depth
3. Move small distance onto contour at cutting feed

**Lead-out:**
1. Move small distance off contour
2. Retract to safe Z

```python
def add_lead_in_out(points: [Point2D], lead_length: float) -> [Point2D]:
    """Add lead-in and lead-out segments"""
    if len(points) < 2:
        return points
    
    # Lead-in: extend backward from first point
    p0 = points[0]
    p1 = points[1]
    direction = normalize(p1 - p0)
    lead_in_point = p0 - direction * lead_length
    
    # Lead-out: extend forward from last point
    p_last = points[-1]
    p_prev = points[-2]
    direction = normalize(p_last - p_prev)
    lead_out_point = p_last + direction * lead_length
    
    return [lead_in_point] + points + [lead_out_point]
```

#### 4.5.4 Linking Moves

Between contours:
1. Retract Z to safe height
2. Rapid move (G0) to next contour's lead-in start point
3. Repeat for each contour

```python
def plan_linking_moves(contours: [OffsetContour], 
                      paths: [[Point2D]]) -> [Move]:
    """Generate rapid linking moves between contours"""
    moves = []
    for i in range(len(paths) - 1):
        current_end = paths[i][-1]
        next_start = paths[i+1][0]
        
        moves.append(RapidMove(
            from_point=current_end,
            to_point=next_start,
            z=safe_height
        ))
    return moves
```

---

### 4.6 G-code Emission Module

#### Responsibilities
- Generate G-code header
- Emit contour cutting commands
- Generate linking moves
- Generate footer

#### 4.6.1 Program Header
```gcode
%
(Program: Text devFoam)
G21            ; units in mm
G90            ; absolute positioning
G17            ; XY plane
G0 Z5.000      ; move to safe height
M3 S10000      ; spindle/hotwire on (if applicable)
F800           ; default feed rate
```

#### 4.6.2 Contour Cutting
```gcode
; --- New contour (glyph=F, outer=true) ---
G0 Z5.000           ; retract to safe Z
G0 X[P0.x] Y[P0.y]  ; rapid to start
G1 Z[cut_z] F[plunge_feed]   ; plunge

; Follow contour at cutting feed
F[cut_feed]
G1 X[P1.x] Y[P1.y]
G1 X[P2.x] Y[P2.y]
...
G1 X[Pn.x] Y[Pn.y]  ; should close back to lead-out
```

#### 4.6.3 Program Footer
```gcode
G0 Z5.000      ; retract
M5             ; spindle/hotwire off
G0 X0 Y0       ; return to origin
M30            ; end program
%
```

#### Key Functions
```python
def emit_header(params: MachiningParameters) -> [str]:
    """Generate G-code header"""
    
def emit_contour(contour: OffsetContour, path: [Point2D], 
                params: MachiningParameters) -> [str]:
    """Generate G-code for one contour"""
    
def emit_linking_move(move: RapidMove) -> [str]:
    """Generate rapid linking move"""
    
def emit_footer() -> [str]:
    """Generate G-code footer"""
```

---

### 4.7 Visual User Interface Module

#### Responsibilities
- Load and display CAD files (DXF, SVG, JSON)
- Provide interactive shape selection and configuration
- Render visual feedback (arrows, markers, highlights)
- Coordinate user input with G-code generation

#### 4.7.1 File Loading
```python
def load_cad_file(self, filename: str):
    """Load CAD file and extract shapes"""
    # Supports: DXF (via ezdxf), SVG, JSON
    # Extracts: lines, circles, arcs, polylines
    # Handles: bulge values, closed polylines, arc segments
```

#### 4.7.2 Canvas Rendering
```python
def update_shapes_list(self):
    """Render all shapes on canvas with visual feedback"""
    # Auto-scale and center shapes
    # Draw shapes with appropriate colors
    # Add markers for start/entry/exit points
    # Draw directional arrows along paths
    # Highlight selected shapes
```

#### 4.7.3 Interactive Editing
```python
def on_canvas_click(self, event):
    """Handle user clicks for shape/point selection"""
    # Convert canvas coordinates to CAD coordinates
    # Find nearest vertex or line segment
    # Select shape and update UI controls
    # Enable corner snapping (50 CAD unit threshold)
```

#### 4.7.4 Visual Feedback Rendering
```python
def draw_path_arrows(self, cad_points, scale, offset_x, offset_y, 
                    canvas_height, shape, is_selected):
    """Draw green directional arrows along cutting paths"""
    # Calculate arrow spacing based on path length
    # Draw arrows showing cutting direction
    # Respect start point and direction settings
    # Use green color matching reference image
```

#### Key UI Functions
```python
def toggle_edit_mode(self):
    """Enable/disable interactive editing mode"""
    
def on_start_point_changed(self, event):
    """Update start point when user selects from dropdown"""
    
def on_entry_point_changed(self, event):
    """Update entry point for shape connections"""
    
def on_exit_point_changed(self, event):
    """Update exit point for shape connections"""
    
def on_direction_changed(self, event):
    """Update cutting direction (clockwise/counter-clockwise)"""
```

#### UI Layout Structure
```
┌─────────────────────────────────────────────────────┐
│  Main Window (1000x700)                            │
├──────────────────────┬──────────────────────────────┤
│  Left Panel          │  Right Panel                 │
│  (CAD File)          │  (G-code Settings)            │
├──────────────────────┼──────────────────────────────┤
│  - Load File Button  │  - Feed Rate Input           │
│  - File Status       │  - Plunge Rate Input          │
│  - Canvas (400x300)  │  - Tool Radius Input         │
│    with scrollbars   │  - Cut Depth Input           │
│  - Shape Count       │  - Safety Height Input       │
│  - Edit Mode Toggle  │  - Curve Tolerance Input     │
│  - Selected Label    │  - Lead-in Length Input     │
│  - Start Point Combo │  - Units Selector           │
│  - Direction Combo   │  - Wire Temp Input           │
│  - Entry Point Combo │  - Generate Button           │
│  - Exit Point Combo  │  - G-code Preview (Text)    │
│                      │  - Save Button               │
└──────────────────────┴──────────────────────────────┘
```

---

## 5. Main Algorithm

### 5.1 High-Level Pseudocode
```python
function generate_text_gcode(text: str, params: MachiningParameters) -> str:
    # 1. Geometry Import
    glyphs = layout_text(text, params.font_name, params.font_size)
    
    # 2. Polygonization
    polyContours = []
    for glyph in glyphs:
        for contour in glyph.contours:
            polyContour = polygonize_contour(contour, params.curve_tolerance)
            polyContour.parent_glyph = glyph.char
            polyContours.append(polyContour)
    
    # 3. Tool Radius Compensation
    offsetContours = []
    for pc in polyContours:
        is_outer = (signed_area(pc.points) > 0)
        offsetContour = offset_polygon(pc, params.tool_radius, is_outer)
        if offsetContour is not None:  # Check for collapsed contour
            offsetContour.is_outer = is_outer
            offsetContours.append(offsetContour)
        else:
            log_warning(f"Contour collapsed during offsetting: {pc.parent_glyph}")
    
    # 4. Contour Classification & Ordering
    orderedContours = order_contours(offsetContours)
    
    # 5. Path Planning
    paths = []
    prev_end = None
    for contour in orderedContours:
        start_idx = choose_start_point(contour, prev_end)
        oriented_points = orient_contour(contour, start_idx)
        path_with_leads = add_lead_in_out(oriented_points, params.lead_in_length)
        paths.append(path_with_leads)
        prev_end = path_with_leads[-1]
    
    # 6. G-code Emission
    gcode_lines = []
    gcode_lines.extend(emit_header(params))
    
    for i, (contour, path) in enumerate(zip(orderedContours, paths)):
        gcode_lines.append(f"; Contour {i+1}: {contour.parent_glyph} ({'outer' if contour.is_outer else 'inner'})")
        gcode_lines.extend(emit_contour(contour, path, params))
        
        # Add linking move to next contour
        if i < len(paths) - 1:
            next_start = paths[i+1][0]
            gcode_lines.extend(emit_linking_move(prev_end, next_start, params))
    
    gcode_lines.extend(emit_footer())
    
    return "\n".join(gcode_lines)
```

---

## 6. Error Handling

### 6.1 Error Types

#### Font Loading Errors
- **Invalid font file**: Report error, suggest valid font path
- **Missing glyph**: Use fallback character or skip

#### Polygonization Errors
- **Invalid Bezier data**: Skip malformed segments, log warning
- **Tolerance too small**: Warn if recursion depth exceeds limit

#### Offsetting Errors
- **Collapsed contour**: Skip contour, log warning with glyph identifier
- **Self-intersection**: Attempt to resolve, or skip if resolution fails
- **Tool radius too large**: Warn if tool radius > contour size

#### Path Planning Errors
- **No valid start point**: Use first point as fallback
- **Invalid direction**: Use default direction based on contour type

### 6.2 Error Reporting
All errors should be:
- Logged with context (glyph, contour index, etc.)
- Reported in G-code as comments (e.g., `; WARNING: ...`)
- Non-fatal when possible (skip problematic contours, continue processing)

---

## 7. API Specification

### 7.1 Public Interface

#### G-code Generator API
```python
class GCodeGenerator:
    def __init__(self):
        """Initialize generator with default parameters"""
        
    def set_parameters(self, params: MachiningParameters):
        """Set machining parameters"""
        
    def generate(self, text: str) -> str:
        """Generate G-code for text string"""
        
    def generate_to_file(self, text: str, filename: str):
        """Generate G-code and save to file"""
```

#### UI Application API
```python
class CADToGCodeConverter:
    def __init__(self, root: tk.Tk):
        """Initialize UI application"""
        
    def load_cad_file(self):
        """Open file dialog and load CAD file"""
        
    def generate_gcode(self):
        """Generate G-code from loaded shapes"""
        
    def save_gcode(self):
        """Save generated G-code to file"""
        
    def toggle_edit_mode(self):
        """Enable/disable interactive editing"""
        
    def on_canvas_click(self, event):
        """Handle canvas click events"""
```

### 7.2 Configuration Interface

```python
class MachiningParameters:
    def __init__(self):
        self.text = ""
        self.font_name = "Arial"
        self.font_size = 100.0
        self.tool_radius = 0.0
        self.cut_depth = 0.0
        self.safe_height = 10.0
        self.cut_feed_rate = 800.0
        self.plunge_feed_rate = 400.0
        self.curve_tolerance = 0.05
        self.lead_in_length = 2.0
        self.units = "mm"
        self.origin_x = 0.0
        self.origin_y = 0.0
```

---

## 8. Implementation Considerations

### 8.1 Performance
- **Font loading**: Cache loaded fonts
- **Polygonization**: Use iterative approach for deep recursion
- **Offsetting**: Consider using library (e.g., Clipper) for complex cases
- **Ordering**: O(n log n) sort is acceptable for typical text lengths
- **Canvas rendering**: Redraw only on changes, use efficient drawing primitives
- **Click detection**: Optimize with spatial indexing for large numbers of shapes

### 8.2 Accuracy
- **Curve tolerance**: Default 0.05mm provides good balance
- **Floating point**: Use double precision for coordinates
- **Coordinate system**: Maintain consistent units throughout
- **Coordinate conversion**: Accurate canvas-to-CAD conversion with Y-axis flip
- **Corner snapping**: 50 CAD unit threshold balances precision and usability

### 8.3 Extensibility
- **Arc support**: Can add G2/G3 emission for circular segments
- **Optimization**: Can add TSP solver for travel minimization
- **Multiple fonts**: Support font mixing in same text
- **Kerning**: Support advanced typography features
- **UI themes**: Support custom color schemes and themes
- **Export formats**: Add support for additional CAD formats

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Font loading and glyph extraction
- Polygonization accuracy (flatness check)
- Offset calculation correctness
- Contour classification (inner vs outer)
- Start point selection
- Direction orientation
- Coordinate conversion (canvas ↔ CAD)
- Corner snapping accuracy
- Arrow rendering calculations

### 9.2 Integration Tests
- End-to-end G-code generation
- Multi-letter text processing
- Complex fonts with holes (e, a, o, etc.)
- Error handling scenarios
- UI file loading (DXF, SVG, JSON)
- Interactive shape selection
- Path configuration updates
- G-code preview generation

### 9.3 Validation Tests
- G-code syntax validation
- Coordinate range checking
- Feed rate validation
- Safety height verification
- Visual feedback accuracy (markers, arrows)
- Click detection precision
- Edit mode functionality

---

## 10. Future Enhancements

### 10.1 Short-term
- Support for arc commands (G2/G3)
- Improved offsetting algorithm (handle sharp corners better)
- Enhanced visual preview with toolpath simulation
- Undo/redo for path configuration changes
- Keyboard shortcuts for common operations

### 10.2 Medium-term
- Travel optimization (nearest-neighbor, TSP)
- Support for multiple tool sizes
- Kerning and advanced typography
- Multi-select for batch configuration
- Export/import path configurations
- Zoom and pan controls for canvas
- Measurement tools (distance, angle)

### 10.3 Long-term
- 3D text cutting (beveled edges)
- Material thickness compensation
- Multi-pass cutting strategies
- Simulation and verification tools
- Real-time G-code validation
- Collaborative editing features
- Plugin system for custom tools

---

## 11. Dependencies

### 11.1 Required Libraries
- **fontTools**: Font file parsing and glyph extraction
- **ezdxf**: DXF file reading and writing
- **tkinter**: GUI framework (included with Python)
- **numpy** (optional): Numerical operations for offsetting
- **shapely** (optional): Advanced polygon operations

### 11.2 System Requirements
- Python 3.7+
- Font files (TrueType/OpenType)
- Sufficient memory for large text strings
- Display capable of 1000x700 minimum resolution
- Graphics support for canvas rendering

---

## 12. User Interface Workflow

### 12.1 Typical User Workflow

1. **Load CAD File**
   - Click "Load CAD File" button
   - Select DXF, SVG, or JSON file
   - Shapes are automatically loaded and displayed on canvas
   - Shape count is updated

2. **Configure Paths (Optional)**
   - Enable "Edit Mode" checkbox
   - Click on shapes or points to select them
   - Use dropdowns to set:
     - Start point (which vertex to begin cutting)
     - Direction (clockwise/counter-clockwise)
     - Entry point (where tool enters from previous shape)
     - Exit point (where tool exits to next shape)
   - Visual feedback shows selections with colored markers

3. **Set Machining Parameters**
   - Enter cutting feed rate
   - Enter plunge feed rate
   - Set tool radius (for offsetting)
   - Set cut depth
   - Set safety height
   - Configure curve tolerance
   - Set lead-in/out length
   - Select units (mm/inches)

4. **Generate G-code**
   - Click "Generate G-code" button
   - Preview appears in text area
   - Review generated code

5. **Save G-code**
   - Click "Save G-code File" button
   - Choose filename and location
   - G-code is saved to file

### 12.2 Visual Feedback Legend
- **Black lines**: Normal shape outlines
- **Blue lines**: Selected shape (in edit mode)
- **Green circle + "START"**: Start point for cutting
- **Blue circle + "ENTRY"**: Entry point (connects from previous shape)
- **Red circle + "EXIT"**: Exit point (connects to next shape)
- **Green arrows**: Cutting direction along paths
- **Yellow circle**: Click location feedback (temporary)

### 12.3 Edit Mode Features
- **Corner Snapping**: Clicking near a vertex (within 50 CAD units) snaps to that corner
- **Line Selection**: Clicking on a line segment selects the shape and nearest vertex
- **Real-time Updates**: Changes to start/entry/exit points update immediately
- **Direction Visualization**: Arrows update to show selected direction

---

## 13. Glossary

- **Glyph**: Visual representation of a character
- **Contour**: Closed curve defining a shape boundary
- **Bezier Curve**: Parametric curve defined by control points
- **Polygonization**: Converting curves to line segments
- **Tool Radius Compensation**: Offsetting path by tool radius
- **Lead-in/Lead-out**: Approach and departure segments
- **Linking Move**: Rapid move between cutting operations
- **Signed Area**: Method to determine polygon orientation
- **Corner Snapping**: Automatic selection of nearest vertex when clicking
- **Edit Mode**: Interactive mode for configuring path parameters
- **Entry Point**: Vertex where tool enters a shape (from previous shape)
- **Exit Point**: Vertex where tool exits a shape (to next shape)

---

## Document Version
- **Version**: 1.0
- **Date**: 2024
- **Author**: G-Code Generator Design Team

