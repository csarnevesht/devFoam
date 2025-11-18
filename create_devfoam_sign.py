#!/usr/bin/env python3
"""
Create a "devfoam" sign DXF file matching the design style
Requires: pip install ezdxf
"""

try:
    import ezdxf
    from ezdxf.math import Vec3
    HAS_EZDXF = True
except ImportError:
    print("Error: ezdxf library required.")
    print("Install with: pip install ezdxf")
    exit(1)

def create_devfoam_sign(filename="devfoam_sign.dxf"):
    """Create a devfoam sign with outlined letters and connecting bridges"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Letter dimensions
    letter_height = 60
    letter_width = 45
    letter_spacing = 50
    bridge_width = 3
    bridge_y_offset = -5  # Position bridges at bottom of letters
    
    # Calculate total width
    text = "devfoam"
    total_width = len(text) * letter_spacing + 100  # Extra space for borders
    total_height = letter_height + 100
    
    # Starting position (centered)
    start_x = 50
    start_y = 50 + letter_height
    
    # Draw bounding box
    border_padding = 20
    msp.add_line((border_padding, border_padding), 
                (total_width - border_padding, border_padding))
    msp.add_line((total_width - border_padding, border_padding), 
                (total_width - border_padding, total_height - border_padding))
    msp.add_line((total_width - border_padding, total_height - border_padding), 
                (border_padding, total_height - border_padding))
    msp.add_line((border_padding, total_height - border_padding), 
                (border_padding, border_padding))
    
    # Draw reference lines (dashed)
    # Vertical reference line on left
    msp.add_line((start_x - 30, border_padding), 
                (start_x - 30, total_height - border_padding), 
                dxfattribs={'linetype': 'DASHED'})
    
    # Horizontal reference line at bottom
    msp.add_line((border_padding, border_padding + 10), 
                (total_width - border_padding, border_padding + 10),
                dxfattribs={'linetype': 'DASHED'})
    
    # Draw each letter with outlines
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y))
        draw_lowercase_letter(msp, letter, x, y, letter_width, letter_height)
    
    # Draw connecting bridges between letters
    for i in range(len(letter_positions) - 1):
        x1, y1 = letter_positions[i]
        x2, y2 = letter_positions[i + 1]
        
        # Bridge connects at bottom of letters
        bridge_y = y1 - letter_height + bridge_y_offset
        
        # Calculate connection points on letter edges
        if i == 0:  # After 'd'
            connect_x1 = x1 + letter_width * 0.7
        else:
            connect_x1 = x1 + letter_width * 0.5
            
        if i + 1 == len(letter_positions) - 1:  # Before 'm'
            connect_x2 = x2 + letter_width * 0.3
        else:
            connect_x2 = x2 + letter_width * 0.5
        
        # Draw bridge line
        msp.add_line((connect_x1, bridge_y), (connect_x2, bridge_y),
                    dxfattribs={'lineweight': 50})  # Thicker line for bridge
    
    # Add toolpath direction indicators (small arrows using lines)
    # Outer perimeters: clockwise
    # Inner perimeters: counter-clockwise
    add_toolpath_indicators(msp, letter_positions, letter_width, letter_height, text)
    
    # Save
    doc.saveas(filename)
    print(f"✅ Created devfoam sign DXF: {filename}")
    print(f"   Size: {total_width} x {total_height} units")
    print(f"   Letters: {text}")

def draw_lowercase_letter(msp, letter, x, y, width, height):
    """Draw a lowercase letter outline with rounded, modern style using polylines"""
    w = width / 2
    h = height / 2
    center_y = y - h
    
    if letter == 'd':
        # Letter d: vertical stem + rounded bowl
        # Create polyline for d
        points = [
            (x - w * 0.85, center_y + h),  # Top left
            (x - w * 0.85, center_y - h),  # Bottom left
        ]
        polyline = msp.add_lwpolyline(points, format='xy')
        # Add rounded right side using arc segments
        # Top arc
        msp.add_arc((x, center_y), w * 0.85, 90, 180)
        # Bottom arc  
        msp.add_arc((x, center_y), w * 0.85, 180, 270)
        # Connect arcs
        msp.add_line((x + w * 0.85, center_y + h), (x + w * 0.85, center_y - h))
        
    elif letter == 'e':
        # Letter e: create as closed polyline
        points = [
            (x - w, center_y + h),      # Top left
            (x + w * 0.7, center_y + h), # Top right
            (x + w * 0.7, center_y + h * 0.1), # Top right down
            (x - w, center_y),          # Middle left
            (x + w * 0.5, center_y),    # Middle right
            (x + w * 0.5, center_y - h * 0.1), # Middle right down
            (x - w, center_y - h),      # Bottom left
            (x + w * 0.7, center_y - h), # Bottom right
            (x + w * 0.7, center_y - h * 0.1), # Bottom right up
            (x - w, center_y - h * 0.1), # Back to start
        ]
        msp.add_lwpolyline(points, format='xy', close=True)
        
    elif letter == 'v':
        # Letter v: simple V shape
        msp.add_line((x - w * 0.75, center_y + h), (x, center_y - h))
        msp.add_line((x, center_y - h), (x + w * 0.75, center_y + h))
        
    elif letter == 'f':
        # Letter f: vertical with two horizontals
        msp.add_line((x - w, center_y + h), (x - w, center_y - h))
        msp.add_line((x - w, center_y + h), (x + w * 0.6, center_y + h))
        msp.add_line((x - w, center_y + h * 0.25), (x + w * 0.4, center_y + h * 0.25))
        
    elif letter == 'o':
        # Letter o: perfect circle
        radius = min(w, h) * 0.85
        msp.add_circle((x, center_y), radius)
        
    elif letter == 'a':
        # Letter a: rounded top with inner loop
        # Outer shape using polyline
        outer_points = [
            (x - w * 0.9, center_y - h),     # Bottom left
            (x - w * 0.9, center_y + h * 0.35), # Left up
            (x, center_y + h),               # Top center
            (x + w * 0.9, center_y + h * 0.35), # Right up
            (x + w * 0.9, center_y - h),     # Bottom right
            (x - w * 0.9, center_y - h),     # Close
        ]
        msp.add_lwpolyline(outer_points, format='xy', close=True)
        # Inner loop (hole)
        inner_radius = min(w, h) * 0.5
        msp.add_circle((x, center_y), inner_radius)
        
    elif letter == 'm':
        # Letter m: create as polyline
        points = [
            (x - w, center_y + h),      # Top left
            (x - w, center_y - h),      # Bottom left
            (x - w * 0.25, center_y),   # Left to middle
            (x - w * 0.25, center_y - h), # Middle down
            (x - w * 0.25, center_y),   # Middle up
            (x + w * 0.25, center_y + h), # Middle to right top
            (x + w, center_y + h),      # Top right
            (x + w, center_y - h),      # Bottom right
        ]
        msp.add_lwpolyline(points, format='xy')
        
    else:
        # Default: simple rectangle
        msp.add_line((x - w, center_y + h), (x + w, center_y + h))
        msp.add_line((x + w, center_y + h), (x + w, center_y - h))
        msp.add_line((x + w, center_y - h), (x - w, center_y - h))
        msp.add_line((x - w, center_y - h), (x - w, center_y + h))

def add_toolpath_indicators(msp, letter_positions, letter_width, letter_height, text):
    """Add toolpath direction indicators (simplified as direction lines)"""
    # Add small direction markers along paths
    # For outer perimeters: clockwise (right direction)
    # For inner perimeters: counter-clockwise (left direction)
    
    for i, (x, y) in enumerate(letter_positions):
        center_y = y - letter_height / 2
        w = letter_width / 2
        h = letter_height / 2
        
        # Add direction markers at key points
        # Top right corner (clockwise)
        marker_size = 3
        msp.add_line((x + w - marker_size, center_y + h), 
                    (x + w, center_y + h + marker_size))
        msp.add_line((x + w, center_y + h + marker_size), 
                    (x + w + marker_size, center_y + h))
        
        # Bottom right corner (clockwise)
        msp.add_line((x + w - marker_size, center_y - h), 
                    (x + w, center_y - h - marker_size))
        msp.add_line((x + w, center_y - h - marker_size), 
                    (x + w + marker_size, center_y - h))
        
        # For letters with inner cutouts (d, e, o, a), add counter-clockwise markers
        letter = text[i]
        if letter in ['d', 'e', 'o', 'a']:
            # Inner markers (counter-clockwise)
            inner_w = w * 0.5
            inner_h = h * 0.5
            msp.add_line((x - inner_w + marker_size, center_y + inner_h), 
                        (x - inner_w, center_y + inner_h + marker_size))
            msp.add_line((x - inner_w, center_y + inner_h + marker_size), 
                        (x - inner_w - marker_size, center_y + inner_h))

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created! Open in CAD viewer or convert to G-code.")

