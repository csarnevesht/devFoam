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
        
        # Visual canvas for shapes
        ttk.Label(left_panel, text="Preview:").pack(anchor=tk.W, pady=(10, 5))
        canvas_frame = ttk.Frame(left_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=400, height=300)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Shape count label
        self.shape_count_label = ttk.Label(left_panel, text="Shapes: 0")
        self.shape_count_label.pack(pady=5)
        
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
                # Force canvas to update after file load
                self.root.update_idletasks()
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
        """Update the visual canvas with shapes"""
        self.canvas.delete("all")
        
        if not self.shapes:
            self.shape_count_label.config(text="Shapes: 0")
            return
            
        # Calculate bounding box for auto-fit
        all_x = []
        all_y = []
        for shape in self.shapes:
            if shape["type"] == "line":
                all_x.extend([shape["x1"], shape["x2"]])
                all_y.extend([shape["y1"], shape["y2"]])
            elif shape["type"] == "circle":
                all_x.extend([shape["cx"] - shape["radius"], shape["cx"] + shape["radius"]])
                all_y.extend([shape["cy"] - shape["radius"], shape["cy"] + shape["radius"]])
            elif shape["type"] == "rectangle":
                all_x.extend([shape["x1"], shape["x2"]])
                all_y.extend([shape["y1"], shape["y2"]])
            elif shape["type"] == "arc":
                all_x.extend([shape["cx"] - shape["radius"], shape["cx"] + shape["radius"]])
                all_y.extend([shape["cy"] - shape["radius"], shape["cy"] + shape["radius"]])
            elif shape["type"] == "polyline":
                for x, y in shape["points"]:
                    all_x.append(x)
                    all_y.append(y)
                    
        if all_x and all_y:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            width = max_x - min_x
            height = max_y - min_y
            
            # Add padding
            padding = max(width, height) * 0.1
            min_x -= padding
            min_y -= padding
            width += 2 * padding
            height += 2 * padding
            
            # Calculate scale to fit canvas
            canvas_width = self.canvas.winfo_width() or 400
            canvas_height = self.canvas.winfo_height() or 300
            
            if width > 0 and height > 0:
                scale_x = (canvas_width - 20) / width
                scale_y = (canvas_height - 20) / height
                scale = min(scale_x, scale_y, 1.0)  # Don't scale up
                
                offset_x = -min_x * scale + (canvas_width - width * scale) / 2
                offset_y = -min_y * scale + (canvas_height - height * scale) / 2
            else:
                scale = 1.0
                offset_x = 0
                offset_y = 0
        else:
            scale = 1.0
            offset_x = 0
            offset_y = 0
            
        # Draw shapes (flip Y-axis to match CAD coordinate system)
        for shape in self.shapes:
            if shape["type"] == "line":
                x1 = shape["x1"] * scale + offset_x
                y1 = canvas_height - (shape["y1"] * scale + offset_y)
                x2 = shape["x2"] * scale + offset_x
                y2 = canvas_height - (shape["y2"] * scale + offset_y)
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

            elif shape["type"] == "circle":
                cx = shape["cx"] * scale + offset_x
                cy = canvas_height - (shape["cy"] * scale + offset_y)
                r = shape["radius"] * scale
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                       outline="black", width=2)

            elif shape["type"] == "rectangle":
                x1 = shape["x1"] * scale + offset_x
                y1 = canvas_height - (shape["y1"] * scale + offset_y)
                x2 = shape["x2"] * scale + offset_x
                y2 = canvas_height - (shape["y2"] * scale + offset_y)
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                           outline="black", width=2)

            elif shape["type"] == "arc":
                cx = shape["cx"] * scale + offset_x
                cy = canvas_height - (shape["cy"] * scale + offset_y)
                r = shape["radius"] * scale
                start_angle = shape.get("start_angle", 0)
                end_angle = shape.get("end_angle", 180)
                extent = end_angle - start_angle
                # Flip arc angles for inverted Y-axis
                self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                      start=180-end_angle, extent=extent,
                                      outline="black", width=2, style=tk.ARC)

            elif shape["type"] == "polyline":
                points = []
                for x, y in shape["points"]:
                    points.extend([x * scale + offset_x, canvas_height - (y * scale + offset_y)])
                if len(points) >= 4:
                    self.canvas.create_line(*points, fill="black", width=2)
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Update shape count
        self.shape_count_label.config(text=f"Shapes: {len(self.shapes)}")
            
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

