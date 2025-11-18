#!/usr/bin/env python3
"""
CAD to G-code Converter
Integrates CAD viewer with G-code generator for foam cutting
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from gcode_generator import GCodeGenerator

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


class CADToGCodeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("CAD to G-code Converter - Foam Cutting")
        self.root.geometry("1000x700")
        
        self.shapes = []
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - CAD file info
        left_panel = ttk.LabelFrame(main_frame, text="CAD File", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Button(left_panel, text="Load CAD File", 
                  command=self.load_cad_file).pack(pady=5)
        
        self.file_label = ttk.Label(left_panel, text="No file loaded")
        self.file_label.pack(pady=5)
        
        # Shapes list
        ttk.Label(left_panel, text="Shapes:").pack(anchor=tk.W, pady=(10, 5))
        self.shapes_listbox = tk.Listbox(left_panel, height=10)
        self.shapes_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right panel - G-code settings
        right_panel = ttk.LabelFrame(main_frame, text="G-code Settings", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Feed rate
        ttk.Label(right_panel, text="Feed Rate (mm/min):").pack(anchor=tk.W, pady=5)
        self.feed_rate_var = tk.StringVar(value="100")
        ttk.Entry(right_panel, textvariable=self.feed_rate_var, width=15).pack(anchor=tk.W, pady=5)
        
        # Cut depth
        ttk.Label(right_panel, text="Cut Depth (mm):").pack(anchor=tk.W, pady=5)
        self.depth_var = tk.StringVar(value="0")
        ttk.Entry(right_panel, textvariable=self.depth_var, width=15).pack(anchor=tk.W, pady=5)
        
        # Safety height
        ttk.Label(right_panel, text="Safety Height (mm):").pack(anchor=tk.W, pady=5)
        self.safety_height_var = tk.StringVar(value="10")
        ttk.Entry(right_panel, textvariable=self.safety_height_var, width=15).pack(anchor=tk.W, pady=5)
        
        # Units
        ttk.Label(right_panel, text="Units:").pack(anchor=tk.W, pady=5)
        self.units_var = tk.StringVar(value="mm")
        units_frame = ttk.Frame(right_panel)
        units_frame.pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(units_frame, text="mm", variable=self.units_var, 
                       value="mm").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(units_frame, text="inches", variable=self.units_var, 
                       value="inches").pack(side=tk.LEFT, padx=5)
        
        # Wire temperature (optional)
        ttk.Label(right_panel, text="Wire Temp (optional):").pack(anchor=tk.W, pady=5)
        self.temp_var = tk.StringVar(value="200")
        ttk.Entry(right_panel, textvariable=self.temp_var, width=15).pack(anchor=tk.W, pady=5)
        
        # Generate button
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Button(right_panel, text="Generate G-code", 
                  command=self.generate_gcode).pack(pady=10)
        
        # Preview area
        ttk.Label(right_panel, text="G-code Preview:").pack(anchor=tk.W, pady=(10, 5))
        preview_frame = ttk.Frame(right_panel)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=10, width=40, wrap=tk.NONE)
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, 
                                 command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        ttk.Button(right_panel, text="Save G-code File", 
                  command=self.save_gcode).pack(pady=10)
        
    def load_cad_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("All CAD", "*.dxf *.svg *.json"), 
                      ("DXF", "*.dxf"), 
                      ("SVG", "*.svg"),
                      ("JSON", "*.json")]
        )
        if filename:
            try:
                ext = os.path.splitext(filename)[1].lower()
                
                if ext == ".json":
                    with open(filename, "r") as f:
                        data = json.load(f)
                        self.shapes = data.get("shapes", [])
                elif ext == ".dxf" and HAS_EZDXF:
                    self.load_dxf(filename)
                else:
                    messagebox.showerror("Error", 
                        f"Cannot load {ext} files. Install ezdxf for DXF support.")
                    return
                    
                self.file_label.config(text=f"Loaded: {os.path.basename(filename)}")
                self.update_shapes_list()
                messagebox.showinfo("Success", f"Loaded {len(self.shapes)} shapes")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def load_dxf(self, filename):
        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()
        self.shapes = []
        
        for entity in msp:
            if entity.dxftype() == "LINE":
                self.shapes.append({
                    "type": "line",
                    "x1": entity.dxf.start.x, "y1": entity.dxf.start.y,
                    "x2": entity.dxf.end.x, "y2": entity.dxf.end.y
                })
            elif entity.dxftype() == "CIRCLE":
                self.shapes.append({
                    "type": "circle",
                    "cx": entity.dxf.center.x, "cy": entity.dxf.center.y,
                    "radius": entity.dxf.radius
                })
            elif entity.dxftype() == "ARC":
                import math
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = math.degrees(entity.dxf.start_angle)
                end_angle = math.degrees(entity.dxf.end_angle)
                self.shapes.append({
                    "type": "arc",
                    "cx": center.x, "cy": center.y,
                    "radius": radius,
                    "start_angle": start_angle,
                    "end_angle": end_angle
                })
            elif entity.dxftype() == "LWPOLYLINE":
                points = []
                for point in entity.get_points():
                    points.append((point[0], point[1]))
                if len(points) > 1:
                    self.shapes.append({
                        "type": "polyline",
                        "points": points
                    })
                    
    def update_shapes_list(self):
        self.shapes_listbox.delete(0, tk.END)
        for i, shape in enumerate(self.shapes):
            shape_type = shape.get("type", "unknown")
            self.shapes_listbox.insert(tk.END, f"{i+1}. {shape_type}")
            
    def generate_gcode(self):
        if not self.shapes:
            messagebox.showwarning("Warning", "No shapes loaded. Please load a CAD file first.")
            return
            
        try:
            # Get settings
            feed_rate = float(self.feed_rate_var.get())
            depth = float(self.depth_var.get())
            safety_height = float(self.safety_height_var.get())
            units = self.units_var.get()
            temp = float(self.temp_var.get())
            
            # Create generator
            gen = GCodeGenerator()
            gen.set_units(units)
            gen.set_feed_rate(feed_rate)
            gen.set_safety_height(safety_height)
            gen.set_wire_temp(temp)
            
            # Generate G-code
            gen.header("Foam Cutting from CAD File")
            gen.generate_from_shapes(self.shapes, depth=depth)
            gen.footer()
            
            # Show preview
            gcode = gen.get_gcode()
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, gcode)
            
            # Store for saving
            self.current_gcode = gcode
            self.current_generator = gen
            
            messagebox.showinfo("Success", "G-code generated successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input value: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate G-code: {str(e)}")
            
    def save_gcode(self):
        if not hasattr(self, 'current_gcode'):
            messagebox.showwarning("Warning", "Please generate G-code first.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".nc",
            filetypes=[("G-code", "*.nc *.gcode *.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.current_generator.save(filename)
                messagebox.showinfo("Success", f"G-code saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")


def main():
    root = tk.Tk()
    app = CADToGCodeConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

