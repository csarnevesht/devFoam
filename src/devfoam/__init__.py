"""
DevFoam - CAD to G-code Converter for Hot-Wire Foam Cutting

A comprehensive toolchain for converting CAD files (DXF, SVG, JSON) into G-code
for hot-wire foam cutting machines.
"""

__version__ = "1.0.0"

from .gcode_generator import GCodeGenerator
from .cad_to_gcode import CADToGCodeConverter

__all__ = [
    "GCodeGenerator",
    "CADToGCodeConverter",
]
