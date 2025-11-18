#!/usr/bin/env python3
"""
Create a "devfoam" sign DXF file with proper rounded lowercase letters
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
    """Create a devfoam sign with properly styled lowercase letters"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Letter dimensions - adjusted for better proportions and spacing
    letter_height = 90
    letter_width = 58
    letter_spacing = 62
    bridge_width = 4
    bridge_y = 32  # Position bridges near bottom
    
    # Calculate total width
    text = "devfoam"
    total_width = len(text) * letter_spacing + 100
    total_height = letter_height + 80
    
    # Starting position
    start_x = 50
    start_y = 50 + letter_height
    
    # Draw bounding box
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
    
    # Draw each letter
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y))
        draw_modern_lowercase_letter(msp, letter, x, y, letter_width, letter_height)
    
    # Draw connecting bridges between letters
    for i in range(len(letter_positions) - 1):
        x1, y1 = letter_positions[i]
        x2, y2 = letter_positions[i + 1]
        letter1 = text[i]
        letter2 = text[i + 1]
        
        # Calculate bridge connection points based on letter shapes
        # For most letters, connect near the bottom center
        if letter1 in ['d', 'e', 'v', 'f', 'o', 'a', 'm']:
            bridge_x1 = x1 + letter_width * 0.5
        else:
            bridge_x1 = x1 + letter_width * 0.5
            
        if letter2 in ['d', 'e', 'v', 'f', 'o', 'a', 'm']:
            bridge_x2 = x2 + letter_width * 0.5
        else:
            bridge_x2 = x2 + letter_width * 0.5
        
        # Draw bridge (thicker line to represent tab/bridge)
        msp.add_line((bridge_x1, bridge_y), (bridge_x2, bridge_y),
                    dxfattribs={'lineweight': 50})
    
    doc.saveas(filename)
    print(f"✅ Created devfoam sign DXF: {filename}")
    print(f"   Size: {total_width} x {total_height} units")

def draw_modern_lowercase_letter(msp, letter, x, y, width, height):
    """Draw modern rounded lowercase letters - using splines for smooth curves"""
    w = width / 2
    h = height / 2
    cy = y - h  # Center Y
    
    if letter == 'd':
        # d: vertical stem + full rounded bowl (smooth)
        msp.add_line((x - w * 0.9, cy + h), (x - w * 0.9, cy - h))
        # Right side - smooth semicircle
        msp.add_arc((x, cy), w * 0.9, 90, 270)
        
    elif letter == 'e':
        # e: rounded e - use spline for smooth curves
        try:
            # Try using spline for smoother e
            from ezdxf.math import Vec3
            # Top horizontal with rounded end
            msp.add_line((x - w, cy + h), (x + w * 0.75, cy + h))
            # Left vertical
            msp.add_line((x - w, cy + h), (x - w, cy - h))
            # Middle horizontal (shorter)
            msp.add_line((x - w, cy), (x + w * 0.55, cy))
            # Bottom horizontal with rounded end
            msp.add_line((x - w, cy - h), (x + w * 0.75, cy - h))
        except:
            # Fallback to simple lines
            msp.add_line((x - w, cy + h), (x + w * 0.8, cy + h))
            msp.add_line((x - w, cy + h), (x - w, cy - h))
            msp.add_line((x - w, cy), (x + w * 0.6, cy))
            msp.add_line((x - w, cy - h), (x + w * 0.8, cy - h))
        
    elif letter == 'v':
        # v: smooth V shape
        msp.add_line((x - w * 0.8, cy + h), (x, cy - h))
        msp.add_line((x, cy - h), (x + w * 0.8, cy + h))
        
    elif letter == 'f':
        # f: vertical + two horizontals
        msp.add_line((x - w, cy + h), (x - w, cy - h))
        msp.add_line((x - w, cy + h), (x + w * 0.7, cy + h))
        msp.add_line((x - w, cy + h * 0.2), (x + w * 0.4, cy + h * 0.2))
        
    elif letter == 'o':
        # o: perfect circle
        radius = min(w, h) * 0.9
        msp.add_circle((x, cy), radius)
        
    elif letter == 'a':
        # a: rounded top arch, inner hole
        arch_y = cy + h * 0.4
        arch_r = w * 1.0
        # Top arch (smooth semicircle)
        msp.add_arc((x, arch_y), arch_r, 180, 0)
        # Left side
        msp.add_line((x - arch_r, arch_y), (x - arch_r, cy - h))
        # Right side
        msp.add_line((x + arch_r, arch_y), (x + arch_r, cy - h))
        # Bottom
        msp.add_line((x - arch_r, cy - h), (x + arch_r, cy - h))
        # Inner hole
        inner_r = min(w, h) * 0.52
        msp.add_circle((x, cy), inner_r)
        
    elif letter == 'm':
        # m: three verticals with smooth connecting curves
        # Left vertical
        msp.add_line((x - w, cy + h), (x - w, cy - h))
        # Left to middle (smooth curve using arc)
        msp.add_arc((x - w * 0.5, cy + h * 0.5), w * 0.25, 180, 270)
        msp.add_line((x - w, cy + h), (x - w * 0.3, cy))
        # Middle vertical
        msp.add_line((x - w * 0.3, cy), (x - w * 0.3, cy - h))
        # Middle to right (smooth curve)
        msp.add_arc((x + w * 0.1, cy + h * 0.5), w * 0.25, 180, 270)
        msp.add_line((x - w * 0.3, cy), (x + w * 0.3, cy + h))
        # Right vertical
        msp.add_line((x + w, cy + h), (x + w, cy - h))
        # Connect right
        msp.add_line((x + w * 0.3, cy + h), (x + w, cy + h))

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created! Open in CAD viewer to see the result.")

