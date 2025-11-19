"""
DevFoam - CAD to G-code Converter for Hot-Wire Foam Cutting

A comprehensive toolchain for converting CAD files (DXF, SVG, JSON) into G-code
for hot-wire foam cutting machines.
"""

__version__ = "1.0.0"

from .gcode_generator import GCodeGenerator

# Only import desktop GUI if tkinter is available (not on web servers)
# On web servers, tkinter may exist but _tkinter C extension is missing
try:
    import tkinter
    # Test if tkinter actually works (not just if the module exists)
    try:
        import _tkinter
        # If we got here, tkinter should work, so import the GUI
        from .cad_to_gcode import CADToGCodeConverter
        __all__ = [
            "GCodeGenerator",
            "CADToGCodeConverter",
        ]
    except (ImportError, ModuleNotFoundError):
        # _tkinter not available, skip GUI import
        __all__ = [
            "GCodeGenerator",
        ]
except (ImportError, ModuleNotFoundError, Exception):
    # tkinter not available or any other error (e.g., on web servers)
    __all__ = [
        "GCodeGenerator",
    ]
