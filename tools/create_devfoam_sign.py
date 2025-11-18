#!/usr/bin/env python3
"""
Create a "devFoam" sign DXF file using font rendering for proper letter shapes
Requires: pip install ezdxf fonttools
"""

try:
    import ezdxf
    import math
    HAS_EZDXF = True
except ImportError:
    print("Error: ezdxf library required.")
    print("Install with: pip install ezdxf")
    exit(1)

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen
    from fontTools.pens.transformPen import TransformPen
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False
    print("Warning: fonttools not available. Install with: pip install fonttools")
    print("Falling back to manual letter drawing...")

class DXFPathPen(BasePen):
    """Pen to convert font paths to DXF entities"""
    def __init__(self, msp):
        BasePen.__init__(self, None)
        self.msp = msp
        self.current_path = []
        self.paths = []
        
    def _moveTo(self, pt):
        if self.current_path:
            self.paths.append(self.current_path)
        self.current_path = [pt]
        
    def _lineTo(self, pt):
        self.current_path.append(pt)
        
    def _curveToOne(self, pt1, pt2, pt3):
        # Convert cubic bezier to polyline approximation
        start = self.current_path[-1] if self.current_path else (0, 0)
        
        # Approximate curve with line segments
        for t in range(1, 21):
            t_norm = t / 20.0
            x = (1-t_norm)**3 * start[0] + 3*(1-t_norm)**2*t_norm * pt1[0] + 3*(1-t_norm)*t_norm**2 * pt2[0] + t_norm**3 * pt3[0]
            y = (1-t_norm)**3 * start[1] + 3*(1-t_norm)**2*t_norm * pt1[1] + 3*(1-t_norm)*t_norm**2 * pt2[1] + t_norm**3 * pt3[1]
            self.current_path.append((x, y))
            
    def _qCurveToOne(self, pt1, pt2):
        # Quadratic bezier approximation
        start = self.current_path[-1] if self.current_path else (0, 0)
        for t in range(1, 21):
            t_norm = t / 20.0
            x = (1-t_norm)**2 * start[0] + 2*(1-t_norm)*t_norm * pt1[0] + t_norm**2 * pt2[0]
            y = (1-t_norm)**2 * start[1] + 2*(1-t_norm)*t_norm * pt1[1] + t_norm**2 * pt2[1]
            self.current_path.append((x, y))
            
    def _closePath(self):
        if self.current_path and len(self.current_path) > 1:
            self.current_path.append(self.current_path[0])
            self.paths.append(self.current_path)
            self.current_path = []
            
    def _endPath(self):
        if self.current_path:
            self.paths.append(self.current_path)
            self.current_path = []
        
    def draw(self):
        """Draw all collected paths as polylines"""
        for path in self.paths:
            if len(path) > 1:
                self.msp.add_lwpolyline(path, close=True)

def create_devfoam_sign(filename="devfoam_sign.dxf"):
    """Create a devFoam sign using font rendering"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Letter dimensions
    letter_height = 100
    letter_width = 70
    letter_spacing = 75

    text = "devFoam"

    # Calculate total dimensions
    total_width = len(text) * letter_spacing + 80
    total_height = letter_height + 120

    # Starting position
    start_x = 50
    start_y = 80

    # Draw bounding box
    border_padding = 25
    msp.add_lwpolyline([
        (border_padding, border_padding),
        (total_width - border_padding, border_padding),
        (total_width - border_padding, total_height - border_padding),
        (border_padding, total_height - border_padding),
        (border_padding, border_padding)
    ], close=True)

    # Try to use system font, fallback to manual if not available
    if HAS_FONTTOOLS:
        try:
            # Try to use a system font (Arial, Helvetica, or similar)
            import os
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/arial.ttf",
            ]
            
            font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
                # Handle TTC files (TrueType Collection)
                if font_path.endswith('.ttc'):
                    # TTC files need a font index
                    from fontTools.ttLib import TTFont
                    font = TTFont(font_path, fontNumber=0)
                else:
                    font = TTFont(font_path)
                glyph_set = font.getGlyphSet()
                
                # Get character map
                cmap = font.getBestCmap()
                units_per_em = font['head'].unitsPerEm
                scale = letter_height / units_per_em
                
                # Get font metrics
                from fontTools.misc.transform import Transform
                if 'OS/2' in font:
                    ascender = font['OS/2'].sTypoAscender
                    descender = abs(font['OS/2'].sTypoDescender)
                elif 'hhea' in font:
                    ascender = font['hhea'].ascent
                    descender = abs(font['hhea'].descent)
                else:
                    ascender = units_per_em * 0.8
                    descender = units_per_em * 0.2
                
                # Draw each letter using font
                for i, letter in enumerate(text):
                    # Use fixed X position for each letter
                    x = start_x + i * letter_spacing
                    # Position Y so baseline is at start_y, accounting for descender
                    y = start_y + descender * scale
                    
                    # Get glyph name from character code
                    char_code = ord(letter)
                    glyph_name = cmap.get(char_code)
                    
                    # Try alternatives if not found
                    if not glyph_name:
                        glyph_name = cmap.get(ord(letter.upper()))
                    if not glyph_name:
                        glyph_name = cmap.get(ord(letter.lower()))
                    
                    if glyph_name and glyph_name in glyph_set:
                        glyph = glyph_set[glyph_name]
                        
                        # Scale and position transform
                        # Font: (0,0) at baseline, Y up
                        # DXF: (x, y) at bottom-left, Y up
                        # Use TransformPen to apply transform correctly
                        from fontTools.misc.transform import Transform
                        # Transform operations are applied right-to-left in matrix multiplication
                        # So translate().scale() means: scale first, then translate
                        transform = Transform().translate(x, y).scale(scale, scale)
                        
                        # Create base pen and wrap with transform pen
                        base_pen = DXFPathPen(msp)
                        pen = TransformPen(base_pen, transform)
                        glyph.draw(pen)
                        base_pen.draw()
                    else:
                        # Fallback to manual drawing
                        draw_letter_manual(msp, letter, x, start_y, letter_width, letter_height)
                
                # Draw bridges
                bridge_y = start_y + 12
                for i in range(len(text) - 1):
                    x1 = start_x + i * letter_spacing
                    x2 = start_x + (i + 1) * letter_spacing
                    msp.add_line((x1 + letter_width/2, bridge_y), (x2 + letter_width/2, bridge_y),
                                dxfattribs={'lineweight': 50})
                
                doc.saveas(filename)
                print(f"✅ Created devFoam sign DXF using font: {filename}")
                print(f"   Size: {total_width:.1f} x {total_height:.1f} units")
                return
        except Exception as e:
            print(f"Font rendering failed: {e}")
            print("Falling back to manual letter drawing...")
    
    # Fallback: manual letter drawing
    letter_positions = []
    for i, letter in enumerate(text):
        x = start_x + i * letter_spacing
        y = start_y
        letter_positions.append((x, y, letter))
        draw_letter_manual(msp, letter, x, y, letter_width, letter_height)

    # Draw connecting bridges
    bridge_y = start_y + 12
    for i in range(len(letter_positions) - 1):
        x1, _, _ = letter_positions[i]
        x2, _, _ = letter_positions[i + 1]
        msp.add_line((x1 + letter_width/2, bridge_y), (x2 + letter_width/2, bridge_y),
                    dxfattribs={'lineweight': 50})

    doc.saveas(filename)
    print(f"✅ Created devFoam sign DXF: {filename}")
    print(f"   Size: {total_width:.1f} x {total_height:.1f} units")

def draw_letter_manual(msp, letter, x, y, width, height):
    """Manual letter drawing fallback"""
    cx = x + width / 2
    cy = y + height / 2
    letter_lower = letter.lower()
    
    if letter_lower == 'd':
        stem_x = x + width * 0.25
        arc_cx = x + width * 0.6
        arc_cy = cy
        arc_r = height / 2 * 0.8
        
        points = [(stem_x, y), (stem_x, y + height)]
        for angle in range(90, 271, 2):
            rad = math.radians(angle)
            points.append((arc_cx + arc_r * math.cos(rad), arc_cy + arc_r * math.sin(rad)))
        points.append((stem_x, y))
        msp.add_lwpolyline(points, close=True)
        msp.add_circle((arc_cx * 0.96, arc_cy), height * 0.25)
        
    elif letter_lower == 'e':
        left = x + width * 0.25
        points = [
            (left, y), (left, y + height),
            (x + width * 0.75, y + height), (x + width * 0.75, y + height * 0.95),
            (x + width * 0.65, y + height * 0.95), (x + width * 0.65, y + height * 0.55),
            (x + width * 0.60, y + height * 0.55), (x + width * 0.60, y + height * 0.45),
            (x + width * 0.75, y + height * 0.45), (x + width * 0.75, y), (left, y)
        ]
        msp.add_lwpolyline(points, close=True)
        msp.add_circle((x + width * 0.45, cy), height * 0.20)
        
    elif letter_lower == 'v':
        msp.add_lwpolyline([
            (x + width * 0.2, y + height),
            (cx, y),
            (x + width * 0.8, y + height),
            (x + width * 0.2, y + height)
        ], close=True)
        
    elif letter == 'F':
        left = x + width * 0.25
        msp.add_lwpolyline([
            (left, y), (left, y + height),
            (x + width * 0.75, y + height), (x + width * 0.75, y + height * 0.95),
            (x + width * 0.62, y + height * 0.95), (x + width * 0.62, y + height * 0.58),
            (x + width * 0.58, y + height * 0.58), (x + width * 0.58, y + height * 0.52),
            (left, y + height * 0.52), (left, y)
        ], close=True)
        
    elif letter_lower == 'o':
        r = min(width, height) / 2 * 0.82
        msp.add_circle((cx, cy), r)
        msp.add_circle((cx, cy), r * 0.50)
        
    elif letter_lower == 'a':
        left = x + width * 0.25
        right = x + width * 0.75
        arch_cx = cx
        arch_cy = y + height * 0.70
        arch_r = width * 0.30
        
        arch_pts = []
        for angle in range(180, 361, 2):
            rad = math.radians(angle)
            arch_pts.append((arch_cx + arch_r * math.cos(rad), arch_cy + arch_r * math.sin(rad)))
        
        points = [(left, y), (left, y + height * 0.44)] + arch_pts + [(right, y + height * 0.44), (right, y), (left, y)]
        msp.add_lwpolyline(points, close=True)
        msp.add_circle((arch_cx, cy), height * 0.22)
        
    elif letter_lower == 'm':
        left = x + width * 0.25
        right = x + width * 0.75
        mid_l = x + width * 0.42
        mid_r = x + width * 0.58
        
        msp.add_lwpolyline([
            (left, y), (left, y + height),
            (x + width * 0.32, y + height), (mid_l, y + height * 0.48),
            (mid_l, y), (mid_r, y), (mid_r, y + height * 0.48),
            (x + width * 0.68, y + height), (right, y + height), (right, y), (left, y)
        ], close=True)

if __name__ == "__main__":
    create_devfoam_sign("devfoam_sign.dxf")
    print("\n✅ Sign created! Open in cad_to_gcode.py to view and generate G-code.")
