#!/usr/bin/env python3
"""
Create a "devFoam" sign DXF file with bold block letters using polylines
Requires: pip install ezdxf
"""

try:
    import ezdxf
    import math
    HAS_EZDXF = True
except ImportError:
    print("Error: ezdxf library required.")
    print("Install with: pip install ezdxf")
    exit(1)

def create_devfoam_sign(filename="devfoam_sign.dxf"):
    """Create a devFoam sign with bold block letters using polylines"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Letter dimensions - bold block letters
    letter_height = 100
    letter_width = 70
    letter_spacing = 78
    stroke_width = 12   # Width of letter strokes for block effect
    bridge_height = 8   # Height of connecting bridges

    # Text with proper capitalization
    text = "devFoam"

    # Calculate total dimensions
    total_width = len(text) * letter_spacing + 60
    total_height = letter_height + 100

    # Starting position
    start_x = 40
    start_y = 60

    # Draw bounding box using polyline
    border_padding = 20
    msp.add_lwpolyline([
        (border_padding, border_padding),
        (total_width - border_padding, border_padding),
        (total_width - border_padding, total_height - border_padding),
        (border_padding, total_height - border_padding),
        (border_padding, border_padding)
    ], close=True)

    # Draw each letter
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y, letter))
        draw_block_letter_polyline(msp, letter, x, y, letter_width, letter_height, stroke_width)

    # Draw connecting bridges between letters at the baseline using polylines
    bridge_y = start_y + 5  # Just above the baseline
    for i in range(len(letter_positions) - 1):
        x1, _, letter1 = letter_positions[i]
        x2, _, letter2 = letter_positions[i + 1]

        # Calculate bridge endpoints based on letter widths
        bridge_x1 = x1 + letter_width - stroke_width/2
        bridge_x2 = x2 + stroke_width/2

        # Draw bridge as a closed polyline rectangle
        msp.add_lwpolyline([
            (bridge_x1, bridge_y),
            (bridge_x2, bridge_y),
            (bridge_x2, bridge_y + bridge_height),
            (bridge_x1, bridge_y + bridge_height),
            (bridge_x1, bridge_y)
        ], close=True)

    doc.saveas(filename)
    print(f"✅ Created devFoam sign DXF: {filename}")
    print(f"   Size: {total_width:.1f} x {total_height:.1f} units")
    print(f"   Block letter style with {stroke_width}mm stroke width (polyline-based)")

def draw_block_letter_polyline(msp, letter, x, y, width, height, stroke):
    """Draw bold block-style letters using polylines - suitable for foam cutting"""
    letter = letter.upper()

    if letter == 'D':
        # D: vertical bar + curved right side using polylines
        # Left vertical stroke (polyline rectangle)
        msp.add_lwpolyline([
            (x, y),
            (x + stroke, y),
            (x + stroke, y + height),
            (x, y + height),
            (x, y)
        ], close=True)
        
        # Top horizontal
        msp.add_lwpolyline([
            (x, y + height - stroke),
            (x + width * 0.6, y + height - stroke),
            (x + width * 0.6, y + height),
            (x, y + height),
            (x, y + height - stroke)
        ], close=True)
        
        # Bottom horizontal
        msp.add_lwpolyline([
            (x, y),
            (x + width * 0.6, y),
            (x + width * 0.6, y + stroke),
            (x, y + stroke),
            (x, y)
        ], close=True)
        
        # Right curved part (arc)
        center_x = x + width * 0.35
        center_y = y + height/2
        radius = height/2 - stroke
        msp.add_arc((center_x, center_y), radius, 270, 90)

    elif letter == 'E':
        # E: vertical bar + three horizontals using polylines
        # Left vertical
        msp.add_lwpolyline([
            (x, y),
            (x + stroke, y),
            (x + stroke, y + height),
            (x, y + height),
            (x, y)
        ], close=True)
        
        # Top horizontal
        msp.add_lwpolyline([
            (x, y + height - stroke),
            (x + width * 0.85, y + height - stroke),
            (x + width * 0.85, y + height),
            (x, y + height),
            (x, y + height - stroke)
        ], close=True)
        
        # Middle horizontal
        mid_y = y + height/2 - stroke/2
        msp.add_lwpolyline([
            (x, mid_y),
            (x + width * 0.75, mid_y),
            (x + width * 0.75, mid_y + stroke),
            (x, mid_y + stroke),
            (x, mid_y)
        ], close=True)
        
        # Bottom horizontal
        msp.add_lwpolyline([
            (x, y),
            (x + width * 0.85, y),
            (x + width * 0.85, y + stroke),
            (x, y + stroke),
            (x, y)
        ], close=True)

    elif letter == 'V':
        # V: two diagonal strokes meeting at bottom using polylines
        # Left diagonal
        left_top = (x + stroke, y + height)
        left_bottom = (x + width/2, y)
        # Calculate perpendicular for thickness
        dx = left_bottom[0] - left_top[0]
        dy = left_bottom[1] - left_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (left_top[0] - px, left_top[1] - py),
                (left_top[0] + px, left_top[1] + py),
                (left_bottom[0] + px, left_bottom[1] + py),
                (left_bottom[0] - px, left_bottom[1] - py),
                (left_top[0] - px, left_top[1] - py)
            ], close=True)
        
        # Right diagonal
        right_top = (x + width - stroke, y + height)
        right_bottom = (x + width/2, y)
        dx = right_bottom[0] - right_top[0]
        dy = right_bottom[1] - right_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (right_top[0] - px, right_top[1] - py),
                (right_top[0] + px, right_top[1] + py),
                (right_bottom[0] + px, right_bottom[1] + py),
                (right_bottom[0] - px, right_bottom[1] - py),
                (right_top[0] - px, right_top[1] - py)
            ], close=True)

    elif letter == 'F':
        # F: vertical bar + two horizontals using polylines
        # Left vertical
        msp.add_lwpolyline([
            (x, y),
            (x + stroke, y),
            (x + stroke, y + height),
            (x, y + height),
            (x, y)
        ], close=True)
        
        # Top horizontal
        msp.add_lwpolyline([
            (x, y + height - stroke),
            (x + width * 0.85, y + height - stroke),
            (x + width * 0.85, y + height),
            (x, y + height),
            (x, y + height - stroke)
        ], close=True)
        
        # Middle horizontal
        mid_y = y + height/2 - stroke/2
        msp.add_lwpolyline([
            (x, mid_y),
            (x + width * 0.7, mid_y),
            (x + width * 0.7, mid_y + stroke),
            (x, mid_y + stroke),
            (x, mid_y)
        ], close=True)

    elif letter == 'O':
        # O: outer and inner octagons using polylines
        offset = width * 0.15
        h_offset = height * 0.15
        # Outer octagon
        outer_points = [
            (x + offset, y + height),
            (x + width - offset, y + height),
            (x + width, y + height - h_offset),
            (x + width, y + h_offset),
            (x + width - offset, y),
            (x + offset, y),
            (x, y + h_offset),
            (x, y + height - h_offset),
            (x + offset, y + height)
        ]
        msp.add_lwpolyline(outer_points, close=True)

        # Inner hole (smaller octagon)
        inner_offset = offset + stroke + 2
        inner_h_offset = h_offset + stroke + 2
        inner_points = [
            (x + inner_offset, y + height - stroke),
            (x + width - inner_offset, y + height - stroke),
            (x + width - stroke, y + height - inner_h_offset),
            (x + width - stroke, y + inner_h_offset),
            (x + width - inner_offset, y + stroke),
            (x + inner_offset, y + stroke),
            (x + stroke, y + inner_h_offset),
            (x + stroke, y + height - inner_h_offset),
            (x + inner_offset, y + height - stroke)
        ]
        msp.add_lwpolyline(inner_points, close=True)

    elif letter == 'A':
        # A: two diagonal strokes + horizontal crossbar using polylines
        # Left diagonal
        left_top = (x + stroke/2, y)
        left_bottom = (x + width/2 - stroke/2, y + height)
        dx = left_bottom[0] - left_top[0]
        dy = left_bottom[1] - left_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (left_top[0] - px, left_top[1] - py),
                (left_top[0] + px, left_top[1] + py),
                (left_bottom[0] + px, left_bottom[1] + py),
                (left_bottom[0] - px, left_bottom[1] - py),
                (left_top[0] - px, left_top[1] - py)
            ], close=True)
        
        # Right diagonal
        right_top = (x + width/2 + stroke/2, y + height)
        right_bottom = (x + width - stroke/2, y)
        dx = right_bottom[0] - right_top[0]
        dy = right_bottom[1] - right_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (right_top[0] - px, right_top[1] - py),
                (right_top[0] + px, right_top[1] + py),
                (right_bottom[0] + px, right_bottom[1] + py),
                (right_bottom[0] - px, right_bottom[1] - py),
                (right_top[0] - px, right_top[1] - py)
            ], close=True)
        
        # Crossbar
        crossbar_y = y + height * 0.4
        msp.add_lwpolyline([
            (x + width * 0.25, crossbar_y),
            (x + width * 0.75, crossbar_y),
            (x + width * 0.75, crossbar_y + stroke),
            (x + width * 0.25, crossbar_y + stroke),
            (x + width * 0.25, crossbar_y)
        ], close=True)

    elif letter == 'M':
        # M: four verticals connected at top with diagonals using polylines
        # Left vertical
        msp.add_lwpolyline([
            (x, y),
            (x + stroke, y),
            (x + stroke, y + height),
            (x, y + height),
            (x, y)
        ], close=True)
        
        # Right vertical
        msp.add_lwpolyline([
            (x + width - stroke, y),
            (x + width, y),
            (x + width, y + height),
            (x + width - stroke, y + height),
            (x + width - stroke, y)
        ], close=True)
        
        # Left diagonal (from top left to middle)
        left_diag_top = (x + stroke, y + height)
        left_diag_bottom = (x + width/2 - stroke/2, y + height * 0.5)
        dx = left_diag_bottom[0] - left_diag_top[0]
        dy = left_diag_bottom[1] - left_diag_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (left_diag_top[0] - px, left_diag_top[1] - py),
                (left_diag_top[0] + px, left_diag_top[1] + py),
                (left_diag_bottom[0] + px, left_diag_bottom[1] + py),
                (left_diag_bottom[0] - px, left_diag_bottom[1] - py),
                (left_diag_top[0] - px, left_diag_top[1] - py)
            ], close=True)
        
        # Right diagonal (from middle to top right)
        right_diag_top = (x + width - stroke, y + height)
        right_diag_bottom = (x + width/2 + stroke/2, y + height * 0.5)
        dx = right_diag_bottom[0] - right_diag_top[0]
        dy = right_diag_bottom[1] - right_diag_top[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            px = -dy / length * stroke/2
            py = dx / length * stroke/2
            msp.add_lwpolyline([
                (right_diag_top[0] - px, right_diag_top[1] - py),
                (right_diag_top[0] + px, right_diag_top[1] + py),
                (right_diag_bottom[0] + px, right_diag_bottom[1] + py),
                (right_diag_bottom[0] - px, right_diag_bottom[1] - py),
                (right_diag_top[0] - px, right_diag_top[1] - py)
            ], close=True)

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created! Open in CAD viewer to see the result.")

