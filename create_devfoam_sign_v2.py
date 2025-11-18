#!/usr/bin/env python3
"""
Create a "devFoam" sign DXF file with bold block letters
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
    """Create a devFoam sign with bold block letters"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Letter dimensions - bold block letters need more space
    letter_height = 100
    letter_width = 70
    letter_spacing = 78  # Space between letters
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

    # Draw bounding box
    border_padding = 20
    msp.add_lwpolyline([
        (border_padding, border_padding),
        (total_width - border_padding, border_padding),
        (total_width - border_padding, total_height - border_padding),
        (border_padding, total_height - border_padding),
        (border_padding, border_padding)
    ])

    # Draw each letter
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y, letter))
        draw_block_letter(msp, letter, x, y, letter_width, letter_height, stroke_width)

    # Draw connecting bridges between letters at the baseline
    bridge_y = start_y + 5  # Just above the baseline
    for i in range(len(letter_positions) - 1):
        x1, _, letter1 = letter_positions[i]
        x2, _, letter2 = letter_positions[i + 1]

        # Calculate bridge endpoints based on letter widths
        bridge_x1 = x1 + letter_width - stroke_width/2
        bridge_x2 = x2 + stroke_width/2

        # Draw bridge as a rectangle
        msp.add_lwpolyline([
            (bridge_x1, bridge_y),
            (bridge_x2, bridge_y),
            (bridge_x2, bridge_y + bridge_height),
            (bridge_x1, bridge_y + bridge_height),
            (bridge_x1, bridge_y)
        ])

    doc.saveas(filename)
    print(f"✅ Created devFoam sign DXF: {filename}")
    print(f"   Size: {total_width:.1f} x {total_height:.1f} units")
    print(f"   Block letter style with {stroke_width}mm stroke width")

def draw_block_letter(msp, letter, x, y, width, height, stroke):
    """Draw bold block-style letters suitable for foam cutting"""
    # Helper function to create thick strokes using rectangles
    def draw_vert_stroke(x_pos, y_start, y_end):
        """Draw a vertical stroke"""
        msp.add_lwpolyline([
            (x_pos, y_start),
            (x_pos + stroke, y_start),
            (x_pos + stroke, y_end),
            (x_pos, y_end),
            (x_pos, y_start)
        ])

    def draw_horiz_stroke(x_start, x_end, y_pos):
        """Draw a horizontal stroke"""
        msp.add_lwpolyline([
            (x_start, y_pos),
            (x_end, y_pos),
            (x_end, y_pos + stroke),
            (x_start, y_pos + stroke),
            (x_start, y_pos)
        ])

    def draw_diagonal_stroke(x1, y1, x2, y2, width_offset=0):
        """Draw a diagonal stroke with thickness"""
        # Calculate perpendicular offset for thickness
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
        # Perpendicular unit vector
        px = -dy / length * (stroke/2 + width_offset)
        py = dx / length * (stroke/2 + width_offset)

        msp.add_lwpolyline([
            (x1 - px, y1 - py),
            (x1 + px, y1 + py),
            (x2 + px, y2 + py),
            (x2 - px, y2 - py),
            (x1 - px, y1 - py)
        ])

    letter = letter.upper()

    if letter == 'D':
        # D: vertical bar + curved right side
        draw_vert_stroke(x, y, y + height)
        # Top horizontal
        draw_horiz_stroke(x, x + width * 0.6, y + height - stroke)
        # Bottom horizontal
        draw_horiz_stroke(x, x + width * 0.6, y)
        # Right curved part (approximate with arc)
        msp.add_arc((x + width * 0.35, y + height/2), height/2 - stroke, 270, 90,
                   dxfattribs={'lineweight': int(stroke * 10)})

    elif letter == 'E':
        # E: vertical bar + three horizontals
        draw_vert_stroke(x, y, y + height)
        draw_horiz_stroke(x, x + width * 0.85, y + height - stroke)  # Top
        draw_horiz_stroke(x, x + width * 0.75, y + height/2 - stroke/2)  # Middle
        draw_horiz_stroke(x, x + width * 0.85, y)  # Bottom

    elif letter == 'V':
        # V: two diagonal strokes meeting at bottom
        draw_diagonal_stroke(x + stroke, y + height, x + width/2, y)
        draw_diagonal_stroke(x + width/2, y, x + width - stroke, y + height)

    elif letter == 'F':
        # F: vertical bar + two horizontals (top and middle)
        draw_vert_stroke(x, y, y + height)
        draw_horiz_stroke(x, x + width * 0.85, y + height - stroke)  # Top
        draw_horiz_stroke(x, x + width * 0.7, y + height/2 - stroke/2)  # Middle

    elif letter == 'O':
        # O: outline rectangle with rounded corners or octagon for better cutting
        # Using octagon for cleaner foam cutting
        offset = width * 0.15
        h_offset = height * 0.15
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
        msp.add_lwpolyline(outer_points)

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
        msp.add_lwpolyline(inner_points)

    elif letter == 'A':
        # A: two diagonal strokes + horizontal crossbar
        draw_diagonal_stroke(x + stroke/2, y, x + width/2 - stroke/2, y + height)
        draw_diagonal_stroke(x + width/2 + stroke/2, y + height, x + width - stroke/2, y)
        # Crossbar
        crossbar_y = y + height * 0.4
        draw_horiz_stroke(x + width * 0.25, x + width * 0.75, crossbar_y)

    elif letter == 'M':
        # M: four verticals connected at top with diagonals
        draw_vert_stroke(x, y, y + height)  # Left
        draw_vert_stroke(x + width - stroke, y, y + height)  # Right
        # Diagonals from top
        draw_diagonal_stroke(x + stroke, y + height, x + width/2 - stroke/2, y + height * 0.5)
        draw_diagonal_stroke(x + width/2 + stroke/2, y + height * 0.5, x + width - stroke, y + height)

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created! Open in CAD viewer to see the result.")

