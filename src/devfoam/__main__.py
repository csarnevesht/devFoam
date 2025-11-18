#!/usr/bin/env python3
"""
Main entry point for devfoam package.
Allows running as: python -m devfoam
"""

import sys
import tkinter as tk
from .cad_to_gcode import CADToGCodeConverter


def main():
    """Launch the CAD to G-code converter GUI."""
    root = tk.Tk()
    app = CADToGCodeConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
