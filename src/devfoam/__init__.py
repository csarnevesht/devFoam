"""
DevFoam - CAD to G-code Converter for Hot-Wire Foam Cutting

A comprehensive toolchain for converting CAD files (DXF, SVG, JSON) into G-code
for hot-wire foam cutting machines.
"""

__version__ = "1.0.0"

from .gcode_generator import GCodeGenerator

# Only import desktop GUI if tkinter is available (not on web servers)
try:
    import tkinter
    from .cad_to_gcode import CADToGCodeConverter
    __all__ = [
        "GCodeGenerator",
        "CADToGCodeConverter",
    ]
except ImportError:
    # tkinter not available (e.g., on web servers)
    __all__ = [
        "GCodeGenerator",
    ]
