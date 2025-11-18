#!/usr/bin/env python3
"""
Create a sample DXF file for testing
Requires: pip install ezdxf
"""

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    print("Error: ezdxf library required.")
    print("Install with: pip install ezdxf")
    exit(1)

def create_sample_dxf(filename="sample_foam_cutting.dxf"):
    """Create a sample DXF file with various shapes"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Add title
    msp.add_text("Sample Foam Cutting Template", height=10).set_placement((0, 200))
    
    # Rectangle
    msp.add_line((0, 0), (200, 0))
    msp.add_line((200, 0), (200, 100))
    msp.add_line((200, 100), (0, 100))
    msp.add_line((0, 100), (0, 0))
    
    # Circle
    msp.add_circle((100, 50), 30)
    
    # Arc
    msp.add_arc((50, 50), 20, 0, 180)
    
    # Lines
    msp.add_line((10, 10), (190, 90))
    msp.add_line((190, 10), (10, 90))
    
    # Small circles
    msp.add_circle((50, 25), 10)
    msp.add_circle((150, 75), 10)
    
    # Save
    doc.saveas(filename)
    print(f"✅ Created sample DXF file: {filename}")

if __name__ == "__main__":
    create_sample_dxf()

