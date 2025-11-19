# Start Point Controls Guide

Start point controls allow you to specify where the cutting tool begins following a polyline path. This feature is essential for optimizing tool paths, connecting multiple shapes efficiently, and planning the cutting sequence.

## What is a Start Point?

The **start point** is the vertex (corner) where the cutting tool begins following the polyline path. By default, cutting starts at the first point in the polyline, but you can select any vertex as the starting point.

## Why Use Start Points?

### 1. **Path Optimization**
Starting at a specific corner allows you to optimize the cutting path, reducing travel time and improving efficiency.

### 2. **Connecting Shapes**
When cutting multiple shapes, you can set the start point of the next shape to match the end point of the previous shape, creating a continuous cutting path.

### 3. **Material Efficiency**
By carefully choosing start points, you can minimize non-cutting moves (rapid movements) between shapes, saving time and reducing wire wear.

### 4. **Visual Planning**
The directional arrows show you exactly how the cutting will proceed, helping you plan the optimal sequence before generating G-code.

## How to Use Start Point Controls

### Method 1: Visual Selection (Recommended)

**Desktop Application:**
1. Enable **Edit Mode** (check the "✏️ Edit Mode" checkbox)
2. Click on a polyline shape to select it
3. Click directly on a vertex (corner) - the system will snap to the nearest corner within 50 CAD units
4. Or click on a line segment - it will snap to the nearest endpoint
5. The selected point becomes the start point and displays a green "START" marker

**Web Application:**
1. Enable **Edit Mode** (check the "Edit Mode" checkbox)
2. Click on a polyline shape to select it
3. Click directly on a vertex or line segment
4. The selected point becomes the start point and displays a green "START" marker

### Method 2: Dropdown Selection

**Desktop Application:**
1. Select a polyline shape (in Edit Mode)
2. In the **Path Control** panel, find the "Start Point" dropdown
3. Choose from:
   - **"Auto"** - Uses the first point (default behavior)
   - **"Point 1"**, **"Point 2"**, etc. - Specific vertex numbers

**Web Application:**
1. Select a polyline shape (in Edit Mode)
2. In the **Path Control** section, find the "Start Point" dropdown
3. Choose from the same options as desktop

## What Happens When You Set a Start Point?

### 1. **Points Are Reordered**
The selected point becomes the first point in the cutting sequence. The points array is reordered so that:
- The selected point becomes index 0
- All subsequent points follow in order
- For closed shapes, the path wraps around back to the start

### 2. **Visual Feedback**
- **Green "START" marker**: A green circle with "START" label appears at the selected vertex
- **Directional arrows**: Green arrows show the cutting direction along the path
- **Path preview**: The canvas updates to show the new cutting sequence

### 3. **G-code Generation**
When you generate G-code:
- The tool first performs a rapid move (G0) to the start point
- Then plunges to cutting depth
- Follows the reordered path with linear moves (G1)
- For closed shapes, completes the loop back to the start point

## Example

Consider a rectangular polyline with these points:

```
Point 0: (0, 0)      ┌─────────┐
Point 1: (100, 0)    │         │
Point 2: (100, 50)   │         │
Point 3: (0, 50)     └─────────┘
```

### Default Behavior (start_index = None or "Auto")
- **Cutting sequence**: (0, 0) → (100, 0) → (100, 50) → (0, 50) → (0, 0)
- **G-code**: Starts at bottom-left corner

### With start_index = 2 (Point 2)
- **Points reordered**: [Point 2, Point 3, Point 0, Point 1]
- **Cutting sequence**: (100, 50) → (0, 50) → (0, 0) → (100, 0) → (100, 50)
- **G-code**: Starts at top-right corner

### Generated G-code (with start_index = 2):
```gcode
G0 X100.000 Y50.000    ; Rapid move to start point (top-right)
G0 Z0.000              ; Plunge to cutting depth
G1 X0.000 Y50.000 F100 ; Cut to top-left
G1 X0.000 Y0.000 F100  ; Cut to bottom-left
G1 X100.000 Y0.000 F100 ; Cut to bottom-right
G1 X100.000 Y50.000 F100 ; Complete the rectangle
G0 Z10.000             ; Retract to safety height
```

## Technical Details

### Data Storage
- The `start_index` is stored directly on the shape object: `poly.start_index = 2`
- This value persists when saving/loading CAD files
- It's included in the shape data sent to the G-code generator

### Point Reordering Algorithm
```python
# If start_index is 2 and we have 4 points [0, 1, 2, 3]:
# Reordered becomes: [2, 3, 0, 1]
reordered = points[start_index:] + points[:start_index]
```

### G-code Generation
The `cut_contour()` method in `GCodeGenerator`:
1. Receives the `start_index` parameter
2. Reorders the points array
3. Generates G-code starting from the reordered first point
4. Maintains the correct cutting sequence

### Visual Rendering
- The `getReorderedPoints()` function reorders points for display
- Arrows are drawn along the reordered path
- The START marker is drawn at the original point index (before reordering)

## Corner Snapping

When clicking on a shape, the system uses **corner snapping** to help you select vertices:

- **Vertex threshold**: 50 CAD units (not screen pixels)
- **Line segment threshold**: 30 CAD units
- If you click near a vertex, it snaps to that vertex
- If you click on a line segment, it snaps to the nearest endpoint

This makes it easy to select precise start points even when zoomed out.

## Best Practices

### 1. **Start at Corners**
Corners are easier to position accurately and provide better visual reference points.

### 2. **Minimize Travel Distance**
When cutting multiple shapes, set the start point of the next shape near where the previous shape ended to minimize rapid moves.

### 3. **Consider Material Properties**
- Start at points that won't cause material shift
- For thin materials, start at a stable corner
- Consider the material's grain or structure

### 4. **Visualize First**
Use the directional arrows to preview the cutting path before generating G-code. This helps identify potential issues early.

### 5. **Plan the Sequence**
Think about the overall cutting sequence:
- Which shape should be cut first?
- Where should each shape start?
- How can you minimize non-cutting moves?

## Desktop vs Web Application

Both implementations provide identical functionality:

| Feature | Desktop | Web |
|---------|---------|-----|
| Visual selection | ✅ Click shapes in Edit Mode | ✅ Click shapes in Edit Mode |
| Dropdown selection | ✅ Path Control panel | ✅ Path Control section |
| Corner snapping | ✅ 50-unit threshold | ✅ 50-unit threshold |
| START marker | ✅ Green circle with label | ✅ Green circle with label |
| Directional arrows | ✅ Green arrows | ✅ Green arrows |
| Persistence | ✅ Saved with shape | ✅ Saved with shape |

## Troubleshooting

### Start Point Not Showing
- **Check Edit Mode**: Make sure Edit Mode is enabled
- **Select the shape**: Click on the polyline shape first
- **Check start_index**: Verify the shape has a valid `start_index` value

### Start Point Not Working in G-code
- **Verify shape data**: Check that `start_index` is saved on the shape object
- **Check G-code generator**: Ensure `cut_contour()` receives the `start_index` parameter
- **Review generated G-code**: The first move should be to your selected start point

### Can't Click on Vertices
- **Zoom in**: Get closer to the shape for better precision
- **Check threshold**: The 50-unit threshold is in CAD units, not pixels
- **Try dropdown**: Use the dropdown menu as an alternative

## Related Features

- **Direction Control**: For closed shapes, you can also control clockwise/counter-clockwise direction
- **Entry/Exit Points**: Advanced feature for connecting multiple shapes with bridges
- **Path Planning**: The system automatically optimizes the path based on your start point selection

## Summary

Start point controls give you precise control over where cutting begins on each polyline shape. This simple but powerful feature helps you:
- Optimize cutting paths
- Connect shapes efficiently
- Plan the cutting sequence
- Minimize non-cutting moves

By combining visual selection with dropdown controls, you can quickly set start points for all your shapes, ensuring the generated G-code follows your intended cutting sequence.

