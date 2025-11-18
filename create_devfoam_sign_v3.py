#!/usr/bin/env python3
"""
Create a "devfoam" sign DXF with truly rounded, modern lowercase letters
Uses multiple arcs to create smooth curves instead of straight lines
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
    """Create a devfoam sign with rounded lowercase letters"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Letter dimensions
    letter_height = 90
    letter_width = 58
    letter_spacing = 62
    bridge_y = 32
    
    text = "devfoam"
    total_width = len(text) * letter_spacing + 100
    total_height = letter_height + 80
    
    start_x = 50
    start_y = 50 + letter_height
    
    # Bounding box
    border_padding = 25
    msp.add_line((border_padding, border_padding), 
                (total_width - border_padding, border_padding))
    msp.add_line((total_width - border_padding, border_padding), 
                (total_width - border_padding, total_height - border_padding))
    msp.add_line((total_width - border_padding, total_height - border_padding), 
                (border_padding, total_height - border_padding))
    msp.add_line((border_padding, total_height - border_padding), 
                (border_padding, border_padding))
    
    # Reference lines
    msp.add_line((start_x - 35, border_padding), 
                (start_x - 35, total_height - border_padding), 
                dxfattribs={'linetype': 'DASHED'})
    msp.add_line((border_padding, border_padding + 15), 
                (total_width - border_padding, border_padding + 15),
                dxfattribs={'linetype': 'DASHED'})
    
    # Draw letters
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y))
        draw_rounded_letter(msp, letter, x, y, letter_width, letter_height)
    
    # Connecting bridges
    for i in range(len(letter_positions) - 1):
        x1, y1 = letter_positions[i]
        x2, y2 = letter_positions[i + 1]
        bridge_x1 = x1 + letter_width * 0.5
        bridge_x2 = x2 + letter_width * 0.5
        msp.add_line((bridge_x1, bridge_y), (bridge_x2, bridge_y),
                    dxfattribs={'lineweight': 50})
    
    doc.saveas(filename)
    print(f"✅ Created devfoam sign DXF: {filename}")
    print(f"   Size: {total_width} x {total_height} units")

def draw_rounded_letter(msp, letter, x, y, width, height):
    """Draw rounded lowercase letters using curves instead of straight lines"""
    w = width / 2
    h = height / 2
    cy = y - h
    
    if letter == 'd':
        # d: vertical + full rounded bowl
        msp.add_line((x - w * 0.88, cy + h), (x - w * 0.88, cy - h))
        msp.add_arc((x, cy), w * 0.88, 90, 270)
        
    elif letter == 'e':
        # e: rounded e - use arcs for rounded ends
        # Top horizontal with rounded right end
        msp.add_line((x - w, cy + h), (x + w * 0.7, cy + h))
        msp.add_arc((x + w * 0.7, cy + h), w * 0.08, 180, 0)
        # Left vertical
        msp.add_line((x - w, cy + h), (x - w, cy - h))
        # Middle horizontal with rounded right end
        msp.add_line((x - w, cy), (x + w * 0.5, cy))
        msp.add_arc((x + w * 0.5, cy), w * 0.06, 180, 0)
        # Bottom horizontal with rounded right end
        msp.add_line((x - w, cy - h), (x + w * 0.7, cy - h))
        msp.add_arc((x + w * 0.7, cy - h), w * 0.08, 180, 0)
        
    elif letter == 'v':
        # v: smooth V with rounded bottom
        # Use arc for smooth curve at bottom
        bottom_y = cy - h * 0.95
        msp.add_line((x - w * 0.8, cy + h), (x, bottom_y))
        # Small arc at bottom for smoothness
        msp.add_arc((x, bottom_y), w * 0.1, 180, 0)
        msp.add_line((x, bottom_y), (x + w * 0.8, cy + h))
        
    elif letter == 'f':
        # f: vertical + two horizontals with rounded ends
        msp.add_line((x - w, cy + h), (x - w, cy - h))
        # Top horizontal with rounded end
        msp.add_line((x - w, cy + h), (x + w * 0.65, cy + h))
        msp.add_arc((x + w * 0.65, cy + h), w * 0.05, 180, 0)
        # Middle horizontal with rounded end
        msp.add_line((x - w, cy + h * 0.2), (x + w * 0.4, cy + h * 0.2))
        msp.add_arc((x + w * 0.4, cy + h * 0.2), w * 0.04, 180, 0)
        
    elif letter == 'o':
        # o: perfect circle
        radius = min(w, h) * 0.9
        msp.add_circle((x, cy), radius)
        
    elif letter == 'a':
        # a: rounded top, slightly rounded sides, inner hole
        arch_y = cy + h * 0.38
        arch_r = w * 1.0
        # Top arch
        msp.add_arc((x, arch_y), arch_r, 180, 0)
        # Left side with slight curve
        msp.add_arc((x - arch_r * 0.6, cy - h * 0.2), h * 0.15, 90, 180)
        msp.add_line((x - arch_r, arch_y), (x - arch_r, cy - h))
        # Right side with slight curve
        msp.add_arc((x + arch_r * 0.6, cy - h * 0.2), h * 0.15, 0, 90)
        msp.add_line((x + arch_r, arch_y), (x + arch_r, cy - h))
        # Bottom with slight curve
        msp.add_arc((x, cy - h), arch_r * 0.95, 180, 0)
        # Inner hole
        inner_r = min(w, h) * 0.5
        msp.add_circle((x, cy), inner_r)
        
    elif letter == 'm':
        # m: three verticals with smooth connecting curves
        # Left vertical
        msp.add_line((x - w, cy + h), (x - w, cy - h))
        # Left to middle - smooth curve
        curve_center_x = x - w * 0.4
        curve_center_y = cy + h * 0.3
        msp.add_arc((curve_center_x, curve_center_y), w * 0.3, 180, 270)
        msp.add_line((x - w, cy + h), (x - w * 0.3, cy))
        # Middle vertical
        msp.add_line((x - w * 0.3, cy), (x - w * 0.3, cy - h))
        # Middle to right - smooth curve
        curve_center_x2 = x + w * 0.1
        msp.add_arc((curve_center_x2, curve_center_y), w * 0.3, 180, 270)
        msp.add_line((x - w * 0.3, cy), (x + w * 0.3, cy + h))
        # Right vertical
        msp.add_line((x + w, cy + h), (x + w, cy - h))
        # Connect right
        msp.add_line((x + w * 0.3, cy + h), (x + w, cy + h))

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created with rounded letters! Open in CAD viewer.")

