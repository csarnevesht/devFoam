#!/usr/bin/env python3
"""
CAD File Viewer/Editor for macOS
Supports DXF, SVG, and simple shape editing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import json
import os

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False

try:
    from svg.path import parse_path
    import xml.etree.ElementTree as ET
    HAS_SVG = True
except ImportError:
    HAS_SVG = False


class CADViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("CAD Viewer/Editor - macOS")
        self.root.geometry("1200x800")
        
        # Drawing data
        self.shapes = []
        self.current_file = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.selected_shape = None
        self.drawing_mode = None
        self.start_x = 0
        self.start_y = 0
        
        self.setup_ui()
        self.setup_canvas()
        
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export DXF...", command=self.export_dxf)
        file_menu.add_command(label="Export SVG...", command=self.export_svg)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Zoom In", command=self.zoom_in)
        tools_menu.add_command(label="Zoom Out", command=self.zoom_out)
        tools_menu.add_command(label="Fit to Window", command=self.fit_to_window)
        tools_menu.add_command(label="Reset View", command=self.reset_view)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Line", command=lambda: self.set_drawing_mode("line")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Circle", command=lambda: self.set_drawing_mode("circle")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Rectangle", command=lambda: self.set_drawing_mode("rectangle")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Arc", command=lambda: self.set_drawing_mode("arc")).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="Select", command=lambda: self.set_drawing_mode("select")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Pan", command=lambda: self.set_drawing_mode("pan")).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_canvas(self):
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
    def set_drawing_mode(self, mode):
        self.drawing_mode = mode
        self.status_bar.config(text=f"Mode: {mode.title()}")
        
    def on_canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.drawing_mode == "select":
            self.select_shape_at(x, y)
        elif self.drawing_mode == "pan":
            self.start_x = x
            self.start_y = y
        elif self.drawing_mode in ["line", "circle", "rectangle", "arc"]:
            self.start_x = x
            self.start_y = y
            
    def on_canvas_drag(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.drawing_mode == "pan":
            dx = x - self.start_x
            dy = y - self.start_y
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.start_x = x
            self.start_y = y
        elif self.drawing_mode in ["line", "circle", "rectangle", "arc"]:
            self.draw_preview(x, y)
            
    def on_canvas_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.drawing_mode == "line":
            self.create_line(self.start_x, self.start_y, x, y)
        elif self.drawing_mode == "circle":
            radius = math.sqrt((x - self.start_x)**2 + (y - self.start_y)**2)
            self.create_circle(self.start_x, self.start_y, radius)
        elif self.drawing_mode == "rectangle":
            self.create_rectangle(self.start_x, self.start_y, x, y)
        elif self.drawing_mode == "arc":
            self.create_arc(self.start_x, self.start_y, x, y)
            
        self.canvas.delete("preview")
        
    def on_canvas_motion(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.status_bar.config(text=f"X: {x:.2f}, Y: {y:.2f}")
        
    def on_mousewheel(self, event):
        # Zoom with mouse wheel
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def draw_preview(self, x, y):
        self.canvas.delete("preview")
        
        if self.drawing_mode == "line":
            self.canvas.create_line(self.start_x, self.start_y, x, y, 
                                   tags="preview", fill="gray", dash=(4, 4))
        elif self.drawing_mode == "circle":
            radius = math.sqrt((x - self.start_x)**2 + (y - self.start_y)**2)
            self.canvas.create_oval(self.start_x - radius, self.start_y - radius,
                                   self.start_x + radius, self.start_y + radius,
                                   tags="preview", outline="gray", dash=(4, 4))
        elif self.drawing_mode == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, x, y,
                                        tags="preview", outline="gray", dash=(4, 4))
        elif self.drawing_mode == "arc":
            # Simple arc preview
            self.canvas.create_line(self.start_x, self.start_y, x, y,
                                   tags="preview", fill="gray", dash=(4, 4))
            
    def create_line(self, x1, y1, x2, y2):
        shape = {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2}
        self.shapes.append(shape)
        self.redraw()
        
    def create_circle(self, cx, cy, radius):
        shape = {"type": "circle", "cx": cx, "cy": cy, "radius": radius}
        self.shapes.append(shape)
        self.redraw()
        
    def create_rectangle(self, x1, y1, x2, y2):
        shape = {"type": "rectangle", "x1": x1, "y1": y1, "x2": x2, "y2": y2}
        self.shapes.append(shape)
        self.redraw()
        
    def create_arc(self, x1, y1, x2, y2):
        # Simple arc implementation
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 2
        shape = {"type": "arc", "cx": mid_x, "cy": mid_y, "radius": radius, 
                "start_angle": 0, "end_angle": 180}
        self.shapes.append(shape)
        self.redraw()
        
    def select_shape_at(self, x, y):
        # Simple selection - find closest shape
        min_dist = float('inf')
        selected = None
        
        for i, shape in enumerate(self.shapes):
            dist = self.distance_to_shape(shape, x, y)
            if dist < min_dist and dist < 10:  # 10 pixel threshold
                min_dist = dist
                selected = i
                
        if selected is not None:
            self.selected_shape = selected
            self.redraw()
            self.status_bar.config(text=f"Selected: {self.shapes[selected]['type']}")
        else:
            self.selected_shape = None
            self.redraw()
            
    def distance_to_shape(self, shape, x, y):
        if shape["type"] == "line":
            x1, y1, x2, y2 = shape["x1"], shape["y1"], shape["x2"], shape["y2"]
            # Distance to line segment
            A = x - x1
            B = y - y1
            C = x2 - x1
            D = y2 - y1
            dot = A * C + B * D
            len_sq = C * C + D * D
            if len_sq == 0:
                return math.sqrt(A * A + B * B)
            param = dot / len_sq
            if param < 0:
                xx, yy = x1, y1
            elif param > 1:
                xx, yy = x2, y2
            else:
                xx, yy = x1 + param * C, y1 + param * D
            return math.sqrt((x - xx)**2 + (y - yy)**2)
        elif shape["type"] == "circle":
            cx, cy, r = shape["cx"], shape["cy"], shape["radius"]
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            return abs(dist - r)
        elif shape["type"] == "rectangle":
            x1, y1, x2, y2 = shape["x1"], shape["y1"], shape["x2"], shape["y2"]
            # Distance to rectangle edges
            if x1 <= x <= x2 and y1 <= y <= y2:
                return 0
            dx = max(x1 - x, 0, x - x2)
            dy = max(y1 - y, 0, y - y2)
            return math.sqrt(dx*dx + dy*dy)
        elif shape["type"] == "polyline":
            # Distance to polyline: find min distance to all segments
            points = shape["points"]
            min_dist = float('inf')
            for i in range(len(points) - 1):
                x1, y1 = points[i]["x"], points[i]["y"]
                x2, y2 = points[i + 1]["x"], points[i + 1]["y"]
                # Distance to line segment (same logic as line)
                A = x - x1
                B = y - y1
                C = x2 - x1
                D = y2 - y1
                dot = A * C + B * D
                len_sq = C * C + D * D
                if len_sq == 0:
                    dist = math.sqrt(A * A + B * B)
                else:
                    param = dot / len_sq
                    if param < 0:
                        xx, yy = x1, y1
                    elif param > 1:
                        xx, yy = x2, y2
                    else:
                        xx, yy = x1 + param * C, y1 + param * D
                    dist = math.sqrt((x - xx)**2 + (y - yy)**2)
                min_dist = min(min_dist, dist)
            return min_dist
        return float('inf')
        
    def redraw(self):
        self.canvas.delete("all")

        for i, shape in enumerate(self.shapes):
            color = "red" if i == self.selected_shape else "black"
            width = 3 if i == self.selected_shape else 1

            if shape["type"] == "line":
                self.canvas.create_line(shape["x1"], shape["y1"],
                                       shape["x2"], shape["y2"],
                                       fill=color, width=width)
            elif shape["type"] == "circle":
                cx, cy, r = shape["cx"], shape["cy"], shape["radius"]
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                       outline=color, width=width)
            elif shape["type"] == "rectangle":
                self.canvas.create_rectangle(shape["x1"], shape["y1"],
                                            shape["x2"], shape["y2"],
                                            outline=color, width=width)
            elif shape["type"] == "arc":
                cx, cy, r = shape["cx"], shape["cy"], shape["radius"]
                # Simple arc drawing
                self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                      start=shape["start_angle"], extent=180,
                                      outline=color, width=width, style=tk.ARC)
            elif shape["type"] == "polyline":
                # Draw polyline as connected line segments
                points = shape["points"]
                if len(points) >= 2:
                    # Flatten points for tkinter
                    coords = []
                    for pt in points:
                        coords.extend([pt["x"], pt["y"]])
                    self.canvas.create_line(*coords, fill=color, width=width)

        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
    def new_file(self):
        if self.shapes and not messagebox.askyesno("New File", "Clear current drawing?"):
            return
        self.shapes = []
        self.current_file = None
        self.redraw()
        self.status_bar.config(text="New file")
        
    def open_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("All CAD", "*.dxf *.svg *.json"), 
                      ("DXF", "*.dxf"), 
                      ("SVG", "*.svg"),
                      ("JSON", "*.json")]
        )
        if filename:
            self.load_file(filename)
            
    def load_file(self, filename):
        try:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == ".dxf" and HAS_EZDXF:
                self.load_dxf(filename)
            elif ext == ".svg" and HAS_SVG:
                self.load_svg(filename)
            elif ext == ".json":
                self.load_json(filename)
            else:
                messagebox.showerror("Error", 
                    f"Cannot load {ext} files. Install required libraries:\n"
                    "pip install ezdxf (for DXF)\n"
                    "pip install svg.path (for SVG)")
                return
                
            self.current_file = filename
            self.redraw()
            self.status_bar.config(text=f"Loaded: {os.path.basename(filename)}")
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
                # Convert ARC to our arc format
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
                # Convert polyline to points
                points = []
                for point in entity.get_points():
                    points.append({"x": point[0], "y": point[1]})
                if len(points) > 1:
                    self.shapes.append({
                        "type": "polyline",
                        "points": points,
                        "closed": entity.closed
                    })
                
    def load_svg(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        self.shapes = []
        
        # Simple SVG parsing
        for elem in root.iter():
            if elem.tag.endswith("line"):
                x1 = float(elem.get("x1", 0))
                y1 = float(elem.get("y1", 0))
                x2 = float(elem.get("x2", 0))
                y2 = float(elem.get("y2", 0))
                self.shapes.append({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2})
            elif elem.tag.endswith("circle"):
                cx = float(elem.get("cx", 0))
                cy = float(elem.get("cy", 0))
                r = float(elem.get("r", 0))
                self.shapes.append({"type": "circle", "cx": cx, "cy": cy, "radius": r})
            elif elem.tag.endswith("rect"):
                x = float(elem.get("x", 0))
                y = float(elem.get("y", 0))
                width = float(elem.get("width", 0))
                height = float(elem.get("height", 0))
                self.shapes.append({
                    "type": "rectangle",
                    "x1": x, "y1": y,
                    "x2": x + width, "y2": y + height
                })
                
    def load_json(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            self.shapes = data.get("shapes", [])
            
    def save_file(self):
        if self.current_file:
            self.save_json(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.save_json(filename)
            self.current_file = filename
            
    def save_json(self, filename):
        data = {"shapes": self.shapes}
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        self.status_bar.config(text=f"Saved: {os.path.basename(filename)}")
        
    def export_dxf(self):
        if not HAS_EZDXF:
            messagebox.showerror("Error", "ezdxf library not installed.\nInstall with: pip install ezdxf")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF", "*.dxf")]
        )
        if filename:
            try:
                doc = ezdxf.new("R2010")
                msp = doc.modelspace()
                
                for shape in self.shapes:
                    if shape["type"] == "line":
                        msp.add_line((shape["x1"], shape["y1"]), (shape["x2"], shape["y2"]))
                    elif shape["type"] == "circle":
                        msp.add_circle((shape["cx"], shape["cy"]), shape["radius"])
                    elif shape["type"] == "rectangle":
                        # Convert rectangle to lines
                        x1, y1, x2, y2 = shape["x1"], shape["y1"], shape["x2"], shape["y2"]
                        msp.add_line((x1, y1), (x2, y1))
                        msp.add_line((x2, y1), (x2, y2))
                        msp.add_line((x2, y2), (x1, y2))
                        msp.add_line((x1, y2), (x1, y1))
                        
                doc.saveas(filename)
                self.status_bar.config(text=f"Exported DXF: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export DXF: {str(e)}")
                
    def export_svg(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG", "*.svg")]
        )
        if filename:
            try:
                svg = ['<?xml version="1.0"?>', '<svg xmlns="http://www.w3.org/2000/svg">']
                
                for shape in self.shapes:
                    if shape["type"] == "line":
                        svg.append(f'<line x1="{shape["x1"]}" y1="{shape["y1"]}" '
                                  f'x2="{shape["x2"]}" y2="{shape["y2"]}" stroke="black"/>')
                    elif shape["type"] == "circle":
                        svg.append(f'<circle cx="{shape["cx"]}" cy="{shape["cy"]}" '
                                  f'r="{shape["radius"]}" fill="none" stroke="black"/>')
                    elif shape["type"] == "rectangle":
                        x1, y1, x2, y2 = shape["x1"], shape["y1"], shape["x2"], shape["y2"]
                        width = abs(x2 - x1)
                        height = abs(y2 - y1)
                        svg.append(f'<rect x="{min(x1,x2)}" y="{min(y1,y2)}" '
                                  f'width="{width}" height="{height}" fill="none" stroke="black"/>')
                        
                svg.append('</svg>')
                with open(filename, "w") as f:
                    f.write("\n".join(svg))
                self.status_bar.config(text=f"Exported SVG: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export SVG: {str(e)}")
                
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Clear all shapes?"):
            self.shapes = []
            self.redraw()
            
    def delete_selected(self):
        if self.selected_shape is not None:
            del self.shapes[self.selected_shape]
            self.selected_shape = None
            self.redraw()
            
    def zoom_in(self):
        self.scale *= 1.2
        self.redraw()
        
    def zoom_out(self):
        self.scale /= 1.2
        self.redraw()
        
    def fit_to_window(self):
        if not self.shapes:
            return
        # Calculate bounding box
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
            elif shape["type"] == "polyline":
                for pt in shape["points"]:
                    all_x.append(pt["x"])
                    all_y.append(pt["y"])

        if all_x and all_y:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            width = max_x - min_x
            height = max_y - min_y

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if width > 0 and height > 0:
                scale_x = canvas_width / width * 0.9
                scale_y = canvas_height / height * 0.9
                self.scale = min(scale_x, scale_y)
                self.offset_x = -min_x * self.scale + (canvas_width - width * self.scale) / 2
                self.offset_y = -min_y * self.scale + (canvas_height - height * self.scale) / 2
                self.redraw()
                
    def reset_view(self):
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.redraw()


def main():
    root = tk.Tk()
    app = CADViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

