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
        self.selected_shape_index = None
        self.edit_mode = False
        self.canvas_scale = 1.0
        self.canvas_offset_x = 0.0
        self.canvas_offset_y = 0.0
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
        
        # Edit mode controls
        edit_frame = ttk.LabelFrame(left_panel, text="Path Control", padding="5")
        edit_frame.pack(fill=tk.X, pady=5)
        
        self.edit_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(edit_frame, text="Edit Mode (Click shapes to configure)", 
                       variable=self.edit_mode_var,
                       command=self.toggle_edit_mode).pack(anchor=tk.W, pady=2)
        
        self.selected_label = ttk.Label(edit_frame, text="Selected: None")
        self.selected_label.pack(anchor=tk.W, pady=2)
        
        # Start point controls
        start_frame = ttk.Frame(edit_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Point:").pack(side=tk.LEFT, padx=5)
        self.start_point_var = tk.StringVar(value="Auto")
        start_combo = ttk.Combobox(start_frame, textvariable=self.start_point_var, 
                                  state="readonly", width=15)
        start_combo.pack(side=tk.LEFT, padx=5)
        self.start_point_combo = start_combo
        
        # Direction controls
        dir_frame = ttk.Frame(edit_frame)
        dir_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dir_frame, text="Direction:").pack(side=tk.LEFT, padx=5)
        self.direction_var = tk.StringVar(value="Auto")
        dir_combo = ttk.Combobox(dir_frame, textvariable=self.direction_var,
                                values=["Auto", "Clockwise", "Counter-Clockwise"],
                                state="readonly", width=15)
        dir_combo.pack(side=tk.LEFT, padx=5)
        dir_combo.bind("<<ComboboxSelected>>", self.on_direction_changed)
        
        # Entry/Exit point controls
        entry_frame = ttk.Frame(edit_frame)
        entry_frame.pack(fill=tk.X, pady=2)
        ttk.Label(entry_frame, text="Entry Point:").pack(side=tk.LEFT, padx=5)
        self.entry_point_var = tk.StringVar(value="Auto")
        entry_combo = ttk.Combobox(entry_frame, textvariable=self.entry_point_var,
                                  state="readonly", width=15)
        entry_combo.pack(side=tk.LEFT, padx=5)
        self.entry_point_combo = entry_combo
        entry_combo.bind("<<ComboboxSelected>>", self.on_entry_point_changed)
        
        exit_frame = ttk.Frame(edit_frame)
        exit_frame.pack(fill=tk.X, pady=2)
        ttk.Label(exit_frame, text="Exit Point:").pack(side=tk.LEFT, padx=5)
        self.exit_point_var = tk.StringVar(value="Auto")
        exit_combo = ttk.Combobox(exit_frame, textvariable=self.exit_point_var,
                                 state="readonly", width=15)
        exit_combo.pack(side=tk.LEFT, padx=5)
        self.exit_point_combo = exit_combo
        exit_combo.bind("<<ComboboxSelected>>", self.on_exit_point_changed)
        
        # Bind canvas click - but only when edit mode is enabled
        # Don't bind here, bind it when edit mode is toggled on
        self.snap_to_corner = True  # Enable corner snapping
        
        # Test click handler - always bind for testing
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
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
                # Convert polyline to points, handling arc segments
                import math
                points = []
                # get_points() returns tuples: (x, y, start_width, end_width, bulge)
                pl_points = list(entity.get_points())
                
                for i, point_data in enumerate(pl_points):
                    # Extract x, y from tuple (may be numpy types)
                    x = float(point_data[0])
                    y = float(point_data[1])
                    bulge = float(point_data[4]) if len(point_data) > 4 else 0.0
                    points.append((x, y))
                    
                    # Check if this segment is an arc (has bulge)
                    if bulge != 0:
                        next_idx = (i + 1) % len(pl_points) if entity.closed else i + 1
                        if next_idx < len(pl_points):
                            p1 = points[i]
                            next_point_data = pl_points[next_idx]
                            p2 = (float(next_point_data[0]), float(next_point_data[1]))
                            
                            # Calculate arc from bulge
                            # Bulge = tan(arc_angle / 4)
                            arc_angle = 4 * math.atan(abs(bulge))
                            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                            if dist > 0 and arc_angle > 0:
                                radius = dist / (2 * math.sin(arc_angle / 2))
                                # Calculate arc center (perpendicular to chord midpoint)
                                mid_x = (p1[0] + p2[0]) / 2
                                mid_y = (p1[1] + p2[1]) / 2
                                # Direction perpendicular to chord
                                dx = p2[0] - p1[0]
                                dy = p2[1] - p1[1]
                                perp_dist = radius * math.cos(arc_angle / 2)
                                if abs(dx) > abs(dy):
                                    center_x = mid_x
                                    center_y = mid_y + (perp_dist * (1 if bulge > 0 else -1))
                                else:
                                    center_x = mid_x + (perp_dist * (1 if bulge > 0 else -1))
                                    center_y = mid_y
                                
                                # Add as separate arc shape
                                self.shapes.append({
                                    "type": "arc",
                                    "cx": center_x,
                                    "cy": center_y,
                                    "radius": radius,
                                    "start_angle": math.degrees(math.atan2(p1[1] - center_y, p1[0] - center_x)),
                                    "end_angle": math.degrees(math.atan2(p2[1] - center_y, p2[0] - center_x))
                                })
                
                if len(points) > 1:
                    self.shapes.append({
                        "type": "polyline",
                        "points": points,
                        "closed": entity.closed
                    })
                    
    def update_shapes_list(self):
        """Update the visual canvas with shapes"""
        self.canvas.delete("all")
        
        # Show edit mode instruction if active
        if self.edit_mode:
            self.canvas.create_text(10, 10, anchor=tk.NW, 
                                  text="Edit Mode: Click on shapes or points to configure",
                                  fill="blue", font=("Arial", 10, "bold"))
        
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
                # Normalize extent to be between -360 and 360
                if extent > 360:
                    extent = extent % 360
                elif extent < -360:
                    extent = extent % -360
                # Flip arc angles for inverted Y-axis (tkinter Y is top-down)
                self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                      start=180-end_angle, extent=extent,
                                      outline="black", width=2, style=tk.ARC)

            elif shape["type"] == "polyline":
                points = []
                cad_points = []  # Store CAD coordinates for arrow drawing
                for x, y in shape["points"]:
                    canvas_x = x * scale + offset_x
                    canvas_y = canvas_height - (y * scale + offset_y)
                    points.extend([canvas_x, canvas_y])
                    cad_points.append((x, y))
                if len(points) >= 4:
                    # Check if this shape is selected
                    shape_idx = self.shapes.index(shape)
                    is_selected = (self.edit_mode and shape_idx == self.selected_shape_index)
                    color = "blue" if is_selected else "black"
                    width = 3 if is_selected else 2
                    self.canvas.create_line(*points, fill=color, width=width)
                    
                    # Draw directional arrows along the path
                    self.draw_path_arrows(cad_points, scale, offset_x, offset_y, canvas_height, 
                                         shape, is_selected)
                    
                    # Draw start point marker if specified
                    start_idx = shape.get("start_index")
                    if start_idx is not None and 0 <= start_idx < len(shape["points"]):
                        start_pt = shape["points"][start_idx]
                        sx = start_pt[0] * scale + offset_x
                        sy = canvas_height - (start_pt[1] * scale + offset_y)
                        # Draw green circle for start point
                        self.canvas.create_oval(sx - 6, sy - 6, sx + 6, sy + 6,
                                              fill="green", outline="darkgreen", width=2)
                        self.canvas.create_text(sx, sy - 10, text="START", fill="green", font=("Arial", 8, "bold"))
                    
                    # Draw entry point marker (blue)
                    entry_idx = shape.get("entry_index")
                    if entry_idx is not None and 0 <= entry_idx < len(shape["points"]):
                        entry_pt = shape["points"][entry_idx]
                        ex = entry_pt[0] * scale + offset_x
                        ey = canvas_height - (entry_pt[1] * scale + offset_y)
                        # Draw blue circle for entry point
                        self.canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                              fill="blue", outline="darkblue", width=2)
                        self.canvas.create_text(ex, ey - 10, text="ENTRY", fill="blue", font=("Arial", 8, "bold"))
                    
                    # Draw exit point marker (red)
                    exit_idx = shape.get("exit_index")
                    if exit_idx is not None and 0 <= exit_idx < len(shape["points"]):
                        exit_pt = shape["points"][exit_idx]
                        ex = exit_pt[0] * scale + offset_x
                        ey = canvas_height - (exit_pt[1] * scale + offset_y)
                        # Draw red circle for exit point
                        self.canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                              fill="red", outline="darkred", width=2)
                        self.canvas.create_text(ex, ey - 10, text="EXIT", fill="red", font=("Arial", 8, "bold"))
                    
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def draw_path_arrows(self, cad_points, scale, offset_x, offset_y, canvas_height, shape, is_selected):
        """Draw green directional arrows along a path showing cutting direction"""
        import math
        
        if len(cad_points) < 2:
            return
        
        # Determine point order based on start_index and direction
        points_list = list(cad_points)
        start_idx = shape.get("start_index", 0)
        if start_idx > 0 and start_idx < len(points_list):
            points_list = points_list[start_idx:] + points_list[:start_idx]
        
        # Determine direction for closed shapes
        if shape.get("closed", False) and len(points_list) > 2:
            clockwise = shape.get("clockwise")
            if clockwise is not None:
                # Calculate signed area to check natural direction
                area = 0.0
                for i in range(len(points_list)):
                    j = (i + 1) % len(points_list)
                    area += points_list[i][0] * points_list[j][1]
                    area -= points_list[j][0] * points_list[i][1]
                is_naturally_clockwise = area < 0
                
                # Reverse if needed
                if clockwise != is_naturally_clockwise:
                    points_list = [points_list[0]] + list(reversed(points_list[1:]))
        
        # Draw arrows along the path
        # Calculate spacing based on path length
        total_length = 0
        for i in range(len(points_list)):
            next_i = (i + 1) % len(points_list) if shape.get("closed", False) else i + 1
            if next_i < len(points_list):
                dx = points_list[next_i][0] - points_list[i][0]
                dy = points_list[next_i][1] - points_list[i][1]
                total_length += math.sqrt(dx*dx + dy*dy)
        
        # Number of arrows based on path length (roughly one per 20-30 units)
        num_arrows = max(3, min(15, int(total_length / 25)))
        arrow_spacing = total_length / num_arrows if num_arrows > 0 else total_length
        
        # Draw arrows
        current_length = 0
        target_length = arrow_spacing
        arrow_color = "green"
        arrow_size = 8 * scale if scale > 0 else 8
        
        for i in range(len(points_list)):
            next_i = (i + 1) % len(points_list) if shape.get("closed", False) else i + 1
            if next_i >= len(points_list):
                break
            
            p1 = points_list[i]
            p2 = points_list[next_i]
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_length = math.sqrt(dx*dx + dy*dy)
            
            if seg_length == 0:
                continue
            
            # Normalize direction
            dx_norm = dx / seg_length
            dy_norm = dy / seg_length
            
            # Draw arrows along this segment
            while current_length + seg_length >= target_length:
                # Calculate position along segment
                t = (target_length - current_length) / seg_length if seg_length > 0 else 0
                t = max(0, min(1, t))
                
                arrow_x = p1[0] + t * dx
                arrow_y = p1[1] + t * dy
                
                # Convert to canvas coordinates
                canvas_x = arrow_x * scale + offset_x
                canvas_y = canvas_height - (arrow_y * scale + offset_y)
                
                # Calculate arrow angle
                angle = math.atan2(dy_norm, dx_norm)
                
                # Draw arrow
                arrow_len = arrow_size
                arrow_angle = math.pi / 6  # 30 degrees
                
                # Arrow head points
                tip_x = canvas_x + arrow_len * math.cos(angle)
                tip_y = canvas_y - arrow_len * math.sin(angle)  # Flip Y
                
                left_x = tip_x - arrow_len * 0.6 * math.cos(angle - arrow_angle)
                left_y = tip_y + arrow_len * 0.6 * math.sin(angle - arrow_angle)  # Flip Y
                
                right_x = tip_x - arrow_len * 0.6 * math.cos(angle + arrow_angle)
                right_y = tip_y + arrow_len * 0.6 * math.sin(angle + arrow_angle)  # Flip Y
                
                # Draw arrow
                self.canvas.create_line(canvas_x, canvas_y, tip_x, tip_y, 
                                      fill=arrow_color, width=2)
                self.canvas.create_line(tip_x, tip_y, left_x, left_y, 
                                      fill=arrow_color, width=2)
                self.canvas.create_line(tip_x, tip_y, right_x, right_y, 
                                      fill=arrow_color, width=2)
                
                target_length += arrow_spacing
            
            current_length += seg_length
            if current_length >= target_length:
                current_length -= target_length
                target_length = arrow_spacing
        
        # Update shape count
        self.shape_count_label.config(text=f"Shapes: {len(self.shapes)}")
        
        # Store scale and offset for click detection
        self.canvas_scale = scale
        self.canvas_offset_x = offset_x
        self.canvas_offset_y = offset_y
            
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
            
    def toggle_edit_mode(self):
        """Toggle edit mode on/off"""
        self.edit_mode = self.edit_mode_var.get()
        print(f"Edit mode toggled: {self.edit_mode}")
        if self.edit_mode:
            self.canvas.config(cursor="crosshair")
            # Ensure click binding is active
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            print("Edit mode ON - click handler bound")
        else:
            self.canvas.config(cursor="")
            self.selected_shape_index = None
            self.selected_label.config(text="Selected: None")
            # Unbind click handler when edit mode is off
            self.canvas.unbind("<Button-1>")
            print("Edit mode OFF - click handler unbound")
        self.update_shapes_list()  # Redraw with selection highlights
    
    def on_canvas_click(self, event):
        """Handle canvas click - select shape or point"""
        print(f"Canvas clicked at ({event.x}, {event.y}), edit_mode={self.edit_mode}, shapes={len(self.shapes)}")
        
        # Visual feedback - draw a small marker at click location
        self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, 
                               fill="yellow", outline="orange", width=2, tags="click_marker")
        self.root.after(1000, lambda: self.canvas.delete("click_marker"))  # Remove after 1 second
        
        if not self.edit_mode:
            print("Edit mode is False, returning")
            return
        
        if not self.shapes:
            print("No shapes loaded!")
            self.selected_label.config(text="No shapes loaded! Please load a CAD file first.")
            return
        
        # Convert canvas coordinates to CAD coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Get actual canvas dimensions
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300
        
        # Convert to CAD coordinates (accounting for Y-axis flip)
        # Canvas Y is top-down, CAD Y is bottom-up
        # When drawing: canvas_y = canvas_height - (cad_y * scale + offset_y)
        # So to convert back: cad_y = (canvas_height - canvas_y - offset_y) / scale
        if self.canvas_scale > 0:
            cad_x = (canvas_x - self.canvas_offset_x) / self.canvas_scale
            # Flip Y: canvas_y is from top, CAD y is from bottom
            # Reverse the drawing formula: canvas_y = canvas_height - (cad_y * scale + offset_y)
            # So: cad_y = (canvas_height - canvas_y - offset_y) / scale
            cad_y = (canvas_height - canvas_y - self.canvas_offset_y) / self.canvas_scale
        else:
            cad_x = canvas_x
            cad_y = canvas_y
        
        print(f"Converting click: canvas=({canvas_x:.1f}, {canvas_y:.1f}) -> CAD=({cad_x:.1f}, {cad_y:.1f})")
        print(f"Canvas scale={self.canvas_scale:.4f}, offset=({self.canvas_offset_x:.1f}, {self.canvas_offset_y:.1f})")
        
        # Find closest shape or point
        closest_shape_idx = None
        closest_point_idx = None
        min_dist = float('inf')
        all_distances = []  # For debugging
        
        print(f"Searching through {len(self.shapes)} shapes...")
        # First, try to find closest point (vertex) - with corner snapping
        for idx, shape in enumerate(self.shapes):
            if shape["type"] == "polyline":
                points = shape.get("points", [])
                print(f"  Shape {idx}: {len(points)} points")
                for pt_idx, pt in enumerate(points):
                    if isinstance(pt, (tuple, list)):
                        px, py = float(pt[0]), float(pt[1])
                    elif isinstance(pt, dict):
                        px, py = float(pt.get("x", 0)), float(pt.get("y", 0))
                    else:
                        continue
                    
                    dist = ((px - cad_x)**2 + (py - cad_y)**2)**0.5
                    all_distances.append((idx, pt_idx, dist, px, py))
                    
                    # Scale threshold by canvas scale - make it MUCH more forgiving
                    # Use a larger threshold in CAD units, not screen pixels
                    if self.snap_to_corner:
                        # Use 50 CAD units as threshold (much larger)
                        threshold = 50.0
                    else:
                        threshold = 20.0
                    
                    if dist < threshold and dist < min_dist:
                        min_dist = dist
                        closest_shape_idx = idx
                        closest_point_idx = pt_idx
                        print(f"  ✓ Found closer point: shape {idx}, point {pt_idx}, dist={dist:.2f}, threshold={threshold:.2f}")
        
        # Show closest points for debugging
        if all_distances and closest_shape_idx is None:
            all_distances.sort(key=lambda x: x[2])
            print(f"  Closest 5 points (none within threshold):")
            for idx, pt_idx, dist, px, py in all_distances[:5]:
                print(f"    Shape {idx}, Point {pt_idx}: dist={dist:.2f}, at ({px:.1f}, {py:.1f})")
        
        # If no point found, try to find closest line segment
        if closest_shape_idx is None:
            print("  No point found, checking line segments...")
            min_line_dist = float('inf')
            for idx, shape in enumerate(self.shapes):
                if shape["type"] == "polyline":
                    points = shape.get("points", [])
                    if len(points) < 2:
                        continue
                    
                    # Check each line segment
                    for i in range(len(points)):
                        if isinstance(points[i], (tuple, list)):
                            p1 = (float(points[i][0]), float(points[i][1]))
                        elif isinstance(points[i], dict):
                            p1 = (float(points[i].get("x", 0)), float(points[i].get("y", 0)))
                        else:
                            continue
                        
                        # Get next point (wrap around if closed)
                        next_i = (i + 1) % len(points) if shape.get("closed", False) else i + 1
                        if next_i >= len(points):
                            continue
                            
                        if isinstance(points[next_i], (tuple, list)):
                            p2 = (float(points[next_i][0]), float(points[next_i][1]))
                        elif isinstance(points[next_i], dict):
                            p2 = (float(points[next_i].get("x", 0)), float(points[next_i].get("y", 0)))
                        else:
                            continue
                        
                        # Calculate distance from point to line segment
                        import math
                        dx = p2[0] - p1[0]
                        dy = p2[1] - p1[1]
                        length_sq = dx*dx + dy*dy
                        
                        if length_sq == 0:
                            continue
                        
                        # Project point onto line segment
                        t = max(0, min(1, ((cad_x - p1[0])*dx + (cad_y - p1[1])*dy) / length_sq))
                        proj_x = p1[0] + t * dx
                        proj_y = p1[1] + t * dy
                        
                        dist = math.sqrt((cad_x - proj_x)**2 + (cad_y - proj_y)**2)
                        # Use larger threshold in CAD units
                        threshold = 30.0
                        
                        if dist < threshold and dist < min_line_dist:
                            min_line_dist = dist
                            closest_shape_idx = idx
                            # Use the closer endpoint as the start point
                            dist1 = math.sqrt((cad_x - p1[0])**2 + (cad_y - p1[1])**2)
                            dist2 = math.sqrt((cad_x - p2[0])**2 + (cad_y - p2[1])**2)
                            closest_point_idx = i if dist1 < dist2 else next_i
                            print(f"  ✓ Found line segment: shape {idx}, segment {i}-{next_i}, dist={dist:.2f}")
        
        if closest_shape_idx is not None:
            print(f"SELECTED: Shape {closest_shape_idx}, Point {closest_point_idx}")
            self.selected_shape_index = closest_shape_idx
            shape = self.shapes[closest_shape_idx]
            point_info = f" at Point {closest_point_idx + 1}" if closest_point_idx is not None else ""
            self.selected_label.config(text=f"Selected: Shape {closest_shape_idx + 1} ({shape['type']}){point_info}")
            
            # Update start point combo with available points
            if shape["type"] == "polyline":
                points = shape.get("points", [])
                point_labels = ["Auto"] + [f"Point {i+1}" for i in range(len(points))]
                self.start_point_combo['values'] = point_labels
                self.entry_point_combo['values'] = point_labels
                self.exit_point_combo['values'] = point_labels
                
                # If a specific point was clicked and snapping is enabled, snap to it
                if closest_point_idx is not None and self.snap_to_corner:
                    # Snap the click to the nearest corner
                    snapped_pt = points[closest_point_idx]
                    if isinstance(snapped_pt, (tuple, list)):
                        snapped_x, snapped_y = float(snapped_pt[0]), float(snapped_pt[1])
                    elif isinstance(snapped_pt, dict):
                        snapped_x, snapped_y = float(snapped_pt.get("x", 0)), float(snapped_pt.get("y", 0))
                    
                    # Set as start point
                    shape["start_index"] = closest_point_idx
                    self.start_point_var.set(f"Point {closest_point_idx + 1}")
                else:
                    current_start = shape.get("start_index")
                    if current_start is not None:
                        self.start_point_var.set(f"Point {current_start + 1}")
                    else:
                        self.start_point_var.set("Auto")
                self.start_point_combo.bind("<<ComboboxSelected>>", self.on_start_point_changed)
                
                # Update entry/exit points
                entry_idx = shape.get("entry_index")
                if entry_idx is not None:
                    self.entry_point_var.set(f"Point {entry_idx + 1}")
                else:
                    self.entry_point_var.set("Auto")
                
                exit_idx = shape.get("exit_index")
                if exit_idx is not None:
                    self.exit_point_var.set(f"Point {exit_idx + 1}")
                else:
                    self.exit_point_var.set("Auto")
            
            # Update direction
            current_dir = shape.get("clockwise")
            if current_dir is True:
                self.direction_var.set("Clockwise")
            elif current_dir is False:
                self.direction_var.set("Counter-Clockwise")
            else:
                self.direction_var.set("Auto")
            
            self.update_shapes_list()  # Redraw with selection
        else:
            # No shape found - clear selection
            print(f"NO SHAPE FOUND near click point ({cad_x:.1f}, {cad_y:.1f})")
            self.selected_shape_index = None
            self.selected_label.config(text=f"Selected: None (clicked at {cad_x:.1f}, {cad_y:.1f})")
            self.start_point_var.set("Auto")
            self.direction_var.set("Auto")
            self.entry_point_var.set("Auto")
            self.exit_point_var.set("Auto")
    
    def on_start_point_changed(self, event=None):
        """Handle start point selection change"""
        if self.selected_shape_index is None:
            return
        
        shape = self.shapes[self.selected_shape_index]
        if shape["type"] != "polyline":
            return
        
        selected = self.start_point_var.get()
        if selected == "Auto":
            shape["start_index"] = None
        else:
            # Extract point number from "Point N"
            try:
                point_num = int(selected.split()[-1]) - 1
                if 0 <= point_num < len(shape.get("points", [])):
                    shape["start_index"] = point_num
            except (ValueError, IndexError):
                pass
        
        self.update_shapes_list()
    
    def on_direction_changed(self, event=None):
        """Handle direction selection change"""
        if self.selected_shape_index is None:
            return
        
        shape = self.shapes[self.selected_shape_index]
        if shape["type"] != "polyline" or not shape.get("closed", False):
            return
        
        selected = self.direction_var.get()
        if selected == "Auto":
            shape["clockwise"] = None
        elif selected == "Clockwise":
            shape["clockwise"] = True
        elif selected == "Counter-Clockwise":
            shape["clockwise"] = False
        
        self.update_shapes_list()
    
    def on_entry_point_changed(self, event=None):
        """Handle entry point selection change"""
        if self.selected_shape_index is None:
            return
        
        shape = self.shapes[self.selected_shape_index]
        if shape["type"] != "polyline":
            return
        
        selected = self.entry_point_var.get()
        if selected == "Auto":
            shape["entry_index"] = None
        else:
            try:
                point_num = int(selected.split()[-1]) - 1
                if 0 <= point_num < len(shape.get("points", [])):
                    shape["entry_index"] = point_num
            except (ValueError, IndexError):
                pass
        
        self.update_shapes_list()
    
    def on_exit_point_changed(self, event=None):
        """Handle exit point selection change"""
        if self.selected_shape_index is None:
            return
        
        shape = self.shapes[self.selected_shape_index]
        if shape["type"] != "polyline":
            return
        
        selected = self.exit_point_var.get()
        if selected == "Auto":
            shape["exit_index"] = None
        else:
            try:
                point_num = int(selected.split()[-1]) - 1
                if 0 <= point_num < len(shape.get("points", [])):
                    shape["exit_index"] = point_num
            except (ValueError, IndexError):
                pass
        
        self.update_shapes_list()
    
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

