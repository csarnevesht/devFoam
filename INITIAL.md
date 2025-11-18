## FEATURE:

**CAD to G-code Converter for Hot-Wire Foam Cutting**

A comprehensive toolchain for converting CAD files (DXF, SVG, JSON) into G-code for hot-wire foam cutting machines. The system includes:

1. **G-code Generator** (`gcode_generator.py`) - Core engine for generating G-code with tool radius compensation, contour ordering, and path planning
2. **CAD to G-code Converter** (`cad_to_gcode.py`) - GUI application with integrated CAD viewer that loads CAD files, provides visual preview, interactive path configuration, and G-code generation

Key features:
- Interactive visual editing with corner snapping
- Tool radius compensation (offsetting)
- Inner/outer contour classification and ordering
- Lead-in/lead-out moves
- Directional path visualization with arrows
- Start point, entry point, and exit point configuration
- Support for DXF (with LWPOLYLINE and bulge values), SVG, and JSON formats

## EXAMPLES:

The project includes several example files:

1. **`sample_simple_shape.json`** - Basic shapes (rectangle, circle, lines) for testing
2. **`sample_foam_wing.json`** - Foam wing template example
3. **`sample_foam_fuselage.json`** - Foam fuselage template example
4. **`sample_wing_template.json`** - Complex wing template
5. **`sample_simple.svg`** - SVG format example
6. **`sample_sign.dxf`** - DXF sign example with text
7. **`sample_sign_outline.dxf`** - DXF sign with outlined letters
8. **`devfoam_sign.dxf`** - Generated "devFoam" sign with font-rendered text

**Usage Examples:**
- Load any of the sample files in `cad_to_gcode.py` to see the visual preview
- Use `create_devfoam_sign_v2.py` to generate custom text signs
- Test G-code generation with different tool radii and feed rates

## DOCUMENTATION:

**Primary Documentation:**
- `DESIGN_DOCUMENT.md` - Comprehensive design document covering architecture, algorithms, data structures, UI workflow, and implementation details
- `README.md` - Project overview and quick start guide
- `README_GCODE.md` - G-code generator documentation
- `Gcode_Generator_Requirements.md` - Detailed requirements specification for G-code generation

**Key Technical References:**
- **ezdxf library**: For DXF file reading/writing - handles LWPOLYLINE entities with bulge values
- **fontTools library**: For font rendering and glyph extraction (used in sign generation)
- **Tkinter**: GUI framework for the visual interface
- **G-code standards**: G21 (mm), G90 (absolute), G17 (XY plane), M3/M5 (spindle control), M30 (end program)

**Coordinate System:**
- CAD coordinates: Y-axis positive upward, origin at bottom-left
- Canvas coordinates: Y-axis positive downward (Tkinter standard)
- Conversion required: `cad_y = (canvas_height - canvas_y - offset_y) / scale`

## OTHER CONSIDERATIONS:

**Critical Gotchas:**

1. **DXF LWPOLYLINE Bulge Values**: 
   - Use `entity.get_points()` which returns tuples `(x, y, start_width, end_width, bulge)`
   - Bulge is at index 4, NOT `entity.bulge_values()` (that method doesn't exist)
   - Bulge values represent arc segments between consecutive points

2. **Coordinate System Conversion**:
   - Canvas Y-axis is inverted (top-down) vs CAD Y-axis (bottom-up)
   - Must flip Y when converting: `cad_y = (canvas_height - canvas_y - offset_y) / scale`
   - This was a major bug source - clicks weren't registering correctly

3. **Corner Snapping**:
   - Threshold is 50 CAD units (not pixels) - must convert click coordinates first
   - Check both vertex proximity AND line segment proximity
   - Snap to nearest endpoint when clicking on line segments

4. **Font Rendering Transform Order**:
   - `fontTools.misc.transform.Transform` applies transformations right-to-left
   - Correct: `Transform().translate(x, y).scale(scale, scale)` (scale first, then translate)
   - Wrong: `Transform().scale(scale, scale).translate(x, y)` (would translate first, then scale)

5. **Arc Rendering in Tkinter**:
   - Tkinter's `create_arc` uses different angle conventions than CAD
   - Must flip angles: `start=180-end_angle` for proper display
   - Extent must be normalized to -360 to 360 range

6. **Tool Radius Offsetting**:
   - Outer contours offset outward, inner holes offset inward
   - Use signed area to determine contour type (positive = CCW = outer)
   - Collapsed contours (tool radius too large) must be detected and skipped

7. **Path Direction**:
   - Outer contours should be CCW, inner holes should be CW
   - Arrows must respect start_index and clockwise settings
   - Reorder points array based on start_index before drawing arrows

8. **Edit Mode State Management**:
   - Edit mode must be explicitly toggled via checkbox
   - Canvas click handler always bound, but only processes when edit_mode is True
   - Selected shape index must be tracked separately from edit mode state

9. **Shape Metadata Storage**:
   - Start/entry/exit indices stored directly in shape dict
   - Must validate indices are within bounds before accessing
   - Dropdowns must be populated with valid vertex indices only

10. **G-code Generation**:
    - Always retract to safe height between contours
    - Lead-in/lead-out must be added to path points, not just G-code
    - Linking moves use G0 (rapid) at safe height
    - Plunge uses separate plunge_feed_rate, cutting uses cut_feed_rate
