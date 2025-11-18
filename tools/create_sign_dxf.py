#!/usr/bin/env python3
"""
Create a sample DXF file with text letters for a sign
Requires: pip install ezdxf
"""

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    print("Error: ezdxf library required.")
    print("Install with: pip install ezdxf")
    exit(1)

def create_sign_dxf(filename="sample_sign.dxf", text="FOAM CUT"):
    """Create a DXF file with text letters for a sign"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Add a border/frame around the sign
    border_width = len(text) * 50 + 100
    border_height = 150
    border_x = 0
    border_y = 0
    
    # Draw border rectangle
    msp.add_line((border_x, border_y), (border_x + border_width, border_y))
    msp.add_line((border_x + border_width, border_y), (border_x + border_width, border_y + border_height))
    msp.add_line((border_x + border_width, border_y + border_height), (border_x, border_y + border_height))
    msp.add_line((border_x, border_y + border_height), (border_x, border_y))
    
    # Add corner decorations (small circles)
    corner_radius = 5
    msp.add_circle((border_x + 20, border_y + 20), corner_radius)
    msp.add_circle((border_x + border_width - 20, border_y + 20), corner_radius)
    msp.add_circle((border_x + 20, border_y + border_height - 20), corner_radius)
    msp.add_circle((border_x + border_width - 20, border_y + border_height - 20), corner_radius)
    
    # Add text letters
    # Position text in center of border
    start_x = border_x + 50
    start_y = border_y + border_height / 2
    letter_spacing = 50
    letter_height = 60
    
    # Add each letter as text
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        
        # Add text entity
        msp.add_text(
            letter,
            height=letter_height,
            dxfattribs={
                'style': 'STANDARD',
                'layer': 'TEXT'
            }
        ).set_placement((x, y))
        
        # Optional: Add outline around each letter (for cutting)
        # This creates a rectangle around each letter
        letter_width = letter_height * 0.6
        msp.add_line((x - letter_width/2, y - letter_height/2), 
                    (x + letter_width/2, y - letter_height/2))
        msp.add_line((x + letter_width/2, y - letter_height/2), 
                    (x + letter_width/2, y + letter_height/2))
        msp.add_line((x + letter_width/2, y + letter_height/2), 
                    (x - letter_width/2, y + letter_height/2))
        msp.add_line((x - letter_width/2, y + letter_height/2), 
                    (x - letter_width/2, y - letter_height/2))
    
    # Add decorative line below text
    line_y = start_y - letter_height - 20
    msp.add_line((start_x - 20, line_y), (start_x + len(text) * letter_spacing - 30, line_y))
    
    # Save
    doc.saveas(filename)
    print(f"✅ Created sign DXF file: {filename}")
    print(f"   Text: '{text}'")
    print(f"   Size: {border_width} x {border_height} units")

def create_sign_with_outline_letters(filename="sample_sign_outline.dxf", text="SIGN"):
    """Create a DXF file with outlined letters (better for cutting)"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Calculate dimensions
    letter_count = len(text)
    letter_width = 80
    letter_height = 100
    letter_spacing = 90
    border_padding = 50
    
    total_width = letter_count * letter_spacing + border_padding * 2
    total_height = letter_height + border_padding * 2
    
    # Draw outer border
    msp.add_line((0, 0), (total_width, 0))
    msp.add_line((total_width, 0), (total_width, total_height))
    msp.add_line((total_width, total_height), (0, total_height))
    msp.add_line((0, total_height), (0, 0))
    
    # Draw inner border (offset)
    offset = 20
    msp.add_line((offset, offset), (total_width - offset, offset))
    msp.add_line((total_width - offset, offset), (total_width - offset, total_height - offset))
    msp.add_line((total_width - offset, total_height - offset), (offset, total_height - offset))
    msp.add_line((offset, total_height - offset), (offset, offset))
    
    # Create letter outlines (simplified block letters)
    start_x = border_padding
    start_y = border_padding + letter_height / 2
    
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        
        # Draw letter outline based on letter
        draw_letter_outline(msp, letter, x, y, letter_width, letter_height)
    
    # Save
    doc.saveas(filename)
    print(f"✅ Created sign DXF file with outlined letters: {filename}")
    print(f"   Text: '{text}'")
    print(f"   Size: {total_width} x {total_height} units")

def draw_letter_outline(msp, letter, x, y, width, height):
    """Draw a simple outline of a letter using lines"""
    letter = letter.upper()
    w = width / 2
    h = height / 2
    
    if letter == 'S':
        # Letter S outline
        msp.add_line((x - w, y + h), (x + w, y + h))  # Top
        msp.add_line((x - w, y + h), (x - w, y))      # Left top
        msp.add_line((x - w, y), (x + w, y))          # Middle
        msp.add_line((x + w, y), (x + w, y - h))      # Right middle
        msp.add_line((x - w, y - h), (x + w, y - h))  # Bottom
        
    elif letter == 'I':
        # Letter I outline
        msp.add_line((x - w, y + h), (x + w, y + h))  # Top
        msp.add_line((x, y + h), (x, y - h))          # Vertical
        msp.add_line((x - w, y - h), (x + w, y - h))  # Bottom
        
    elif letter == 'G':
        # Letter G outline
        msp.add_line((x - w, y + h), (x + w, y + h))  # Top
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y - h), (x + w, y - h))  # Bottom
        msp.add_line((x + w, y - h), (x + w, y))      # Right bottom
        msp.add_line((x, y), (x + w, y))              # Middle right
        
    elif letter == 'N':
        # Letter N outline
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y + h), (x + w, y - h))  # Diagonal
        msp.add_line((x + w, y + h), (x + w, y - h))  # Right
        
    elif letter == 'F':
        # Letter F outline
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y + h), (x + w, y + h))  # Top
        msp.add_line((x - w, y), (x + w/2, y))        # Middle
        
    elif letter == 'O':
        # Letter O outline (circle/oval)
        msp.add_circle((x, y), min(w, h) * 0.8)
        
    elif letter == 'A':
        # Letter A outline
        msp.add_line((x, y + h), (x - w, y - h))      # Left
        msp.add_line((x, y + h), (x + w, y - h))      # Right
        msp.add_line((x - w/2, y), (x + w/2, y))      # Middle
        
    elif letter == 'M':
        # Letter M outline
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y + h), (x, y))          # Left to middle
        msp.add_line((x, y), (x + w, y + h))          # Middle to right top
        msp.add_line((x + w, y + h), (x + w, y - h))  # Right
        
    elif letter == 'C':
        # Letter C outline
        msp.add_line((x + w, y + h), (x - w, y + h))  # Top
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y - h), (x + w, y - h))  # Bottom
        
    elif letter == 'U':
        # Letter U outline
        msp.add_line((x - w, y + h), (x - w, y - h))  # Left
        msp.add_line((x - w, y - h), (x + w, y - h))  # Bottom
        msp.add_line((x + w, y - h), (x + w, y + h))  # Right
        
    elif letter == 'T':
        # Letter T outline
        msp.add_line((x - w, y + h), (x + w, y + h))  # Top
        msp.add_line((x, y + h), (x, y - h))          # Vertical
        
    else:
        # Default: simple rectangle for unknown letters
        msp.add_line((x - w, y + h), (x + w, y + h))
        msp.add_line((x + w, y + h), (x + w, y - h))
        msp.add_line((x + w, y - h), (x - w, y - h))
        msp.add_line((x - w, y - h), (x - w, y + h))

if __name__ == "__main__":
    import sys
    
    # Create simple text sign
    create_sign_dxf("sample_sign.dxf", "FOAM CUT")
    
    # Create sign with outlined letters (better for cutting)
    create_sign_with_outline_letters("sample_sign_outline.dxf", "SIGN")
    
    print("\n✅ Created two sample sign DXF files:")
    print("   1. sample_sign.dxf - Text with borders")
    print("   2. sample_sign_outline.dxf - Outlined letters (better for cutting)")

