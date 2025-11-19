#!/usr/bin/env python3
"""
CAD to G-code Converter - Modern UI
Integrated CAD viewer and G-code generator for foam cutting
"""

# Try to import tkinter - handle all possible errors
# On web servers, tkinter may exist but _tkinter C extension is missing
# This causes an error inside tkinter's __init__.py which we need to catch
HAS_TKINTER = False
tk = None
ttk = None
filedialog = None
messagebox = None

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    # If we got here, try to verify tkinter actually works
    # by attempting to create a dummy root (this will fail if _tkinter is missing)
    try:
        # Don't actually create a window, just test if the import chain works
        # Accessing a class attribute should work if _tkinter is available
        _ = tk.Tk.__name__
        HAS_TKINTER = True
    except (AttributeError, RuntimeError, ImportError, ModuleNotFoundError):
        HAS_TKINTER = False
        tk = None
        ttk = None
        filedialog = None
        messagebox = None
except Exception:
    # Catch any exception during import (including errors from tkinter's __init__.py)
    HAS_TKINTER = False
    tk = None
    ttk = None
    filedialog = None
    messagebox = None

if not HAS_TKINTER:
    # Create dummy classes for environments without tkinter (e.g., web servers)
    class tk:
        class Tk:
            pass
        RAISED = "raised"
    class ttk:
        class Frame:
            pass
        class Notebook:
            pass
        class Scrollbar:
            pass
    class filedialog:
        @staticmethod
        def askopenfilename(**kwargs):
            return None
        @staticmethod
        def asksaveasfilename(**kwargs):
            return None
    class messagebox:
        @staticmethod
        def showerror(title, message):
            print(f"ERROR: {title}: {message}")

import json
import os
import math
from .gcode_generator import GCodeGenerator

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


class ModernCADToGCodeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DevFoam - CAD to G-code Converter")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # State variables
        self.shapes = []
        self.selected_shape_index = None
        self.edit_mode = False
        self.canvas_scale = 1.0
        self.canvas_offset_x = 0.0
        self.canvas_offset_y = 0.0
        self.snap_to_corner = True
        self.zoom_level = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_panning = False
        self.loaded_filename = None  # Store loaded CAD filename for default save name
        
        # Create modern UI
        self.setup_modern_ui()
        
    def setup_modern_ui(self):
        """Create modern UI with toolbar, tabs, and status bar"""
        
        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#2c3e50", height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Toolbar buttons - use dark text on light buttons for visibility
        btn_style = {"bg": "#ecf0f1", "fg": "#2c3e50", "relief": tk.RAISED, "bd": 1, 
                     "padx": 15, "pady": 8, "font": ("Arial", 10, "bold")}
        tk.Button(toolbar, text="📁 Load CAD", command=self.load_cad_file, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💾 Save G-code", command=self.save_gcode, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="⚙️ Generate", command=self.generate_gcode, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(toolbar, bg="#34495e", width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Canvas controls
        tk.Label(toolbar, text="Canvas:", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        canvas_btn_style = {"bg": "#ecf0f1", "fg": "#2c3e50", "relief": tk.RAISED, "bd": 1, 
                           "padx": 10, "pady": 6, "font": ("Arial", 9, "bold")}
        tk.Button(toolbar, text="🔍+", command=self.zoom_in, **canvas_btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔍-", command=self.zoom_out, **canvas_btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="⌂ Fit", command=self.fit_to_window, **canvas_btn_style).pack(side=tk.LEFT, padx=2)
        
        # Edit mode toggle - make it more prominent and visible
        tk.Frame(toolbar, bg="#34495e", width=2).pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        self.edit_mode_var = tk.BooleanVar(value=False)
        # Use a bright, visible color for the text
        edit_btn = tk.Checkbutton(toolbar, text="✏️ Edit Mode (Click shapes to configure)", 
                                 variable=self.edit_mode_var,
                                 command=self.toggle_edit_mode, 
                                 bg="#2c3e50", 
                                 fg="#ecf0f1",  # Light gray instead of white for better visibility
                                 selectcolor="#e74c3c", 
                                 font=("Arial", 10, "bold"),
                                 activebackground="#2c3e50", 
                                 activeforeground="#ecf0f1",
                                 highlightthickness=0)  # Remove highlight border
        edit_btn.pack(side=tk.RIGHT, padx=10)
        
        # Main container with paned windows
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - CAD viewer and controls
        left_pane = ttk.Frame(main_paned)
        main_paned.add(left_pane, weight=2)
        
        # Right pane - Settings and preview
        right_pane = ttk.Frame(main_paned)
        main_paned.add(right_pane, weight=1)
        
        # Setup left pane (CAD viewer)
        self.setup_cad_viewer(left_pane)
        
        # Setup right pane (Settings and preview)
        self.setup_settings_panel(right_pane)
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#34495e", height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", bg="#34495e", fg="#ecf0f1",
                                    font=("Arial", 9), anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.shape_count_status = tk.Label(self.status_bar, text="Shapes: 0", bg="#34495e", fg="#ecf0f1",
                                          font=("Arial", 9), padx=10)
        self.shape_count_status.pack(side=tk.RIGHT)
        
    def setup_cad_viewer(self, parent):
        """Setup CAD viewer with canvas and controls"""
        
        # Viewer header
        viewer_header = tk.Frame(parent, bg="#ecf0f1", height=40)
        viewer_header.pack(side=tk.TOP, fill=tk.X)
        viewer_header.pack_propagate(False)
        
        tk.Label(viewer_header, text="CAD Preview", bg="#ecf0f1", font=("Arial", 12, "bold"),
                padx=10).pack(side=tk.LEFT)
        
        self.file_label = tk.Label(viewer_header, text="No file loaded", bg="#ecf0f1",
                                  fg="#7f8c8d", font=("Arial", 9), padx=10)
        self.file_label.pack(side=tk.RIGHT)
        
        # Canvas frame with scrollbars
        canvas_container = tk.Frame(parent, bg="white", relief=tk.SUNKEN, borderwidth=2)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_container, bg="white", highlightthickness=0)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
        
        # Bind canvas events
        # Always bind click handler - it will return early if edit mode is off
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)  # Middle mouse button
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)
        
        # Mouse wheel - platform-specific bindings
        import sys
        if sys.platform == "win32":
            # Windows uses MouseWheel
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        elif sys.platform == "darwin":
            # macOS uses MouseWheel with different event.delta
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        else:
            # Linux uses Button-4 and Button-5
            self.canvas.bind("<Button-4>", self.on_mousewheel)
            self.canvas.bind("<Button-5>", self.on_mousewheel)
        
        # Enable corner snapping
        self.snap_to_corner = True
        
        # Path control panel (collapsible)
        self.path_control_frame = ttk.LabelFrame(parent, text="Path Control", padding=10)
        self.path_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Selected shape info
        self.selected_label = tk.Label(self.path_control_frame, text="Selected: None",
                                      font=("Arial", 9), anchor=tk.W)
        self.selected_label.pack(fill=tk.X, pady=5)
        
        # Control grid
        controls_grid = tk.Frame(self.path_control_frame)
        controls_grid.pack(fill=tk.X)
        
        # Start point
        tk.Label(controls_grid, text="Start Point:", width=12, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.start_point_var = tk.StringVar(value="Auto")
        self.start_point_combo = ttk.Combobox(controls_grid, textvariable=self.start_point_var,
                                             state="readonly", width=18)
        self.start_point_combo.grid(row=0, column=1, padx=5, pady=3)
        self.start_point_combo.bind("<<ComboboxSelected>>", self.on_start_point_changed)
        
        # Direction
        tk.Label(controls_grid, text="Direction:", width=12, anchor=tk.W).grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.direction_var = tk.StringVar(value="Auto")
        dir_combo = ttk.Combobox(controls_grid, textvariable=self.direction_var,
                                values=["Auto", "Clockwise", "Counter-Clockwise"],
                                state="readonly", width=18)
        dir_combo.grid(row=0, column=3, padx=5, pady=3)
        dir_combo.bind("<<ComboboxSelected>>", self.on_direction_changed)
        
        # Entry point
        tk.Label(controls_grid, text="Entry Point:", width=12, anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_point_var = tk.StringVar(value="Auto")
        self.entry_point_combo = ttk.Combobox(controls_grid, textvariable=self.entry_point_var,
                                             state="readonly", width=18)
        self.entry_point_combo.grid(row=1, column=1, padx=5, pady=3)
        self.entry_point_combo.bind("<<ComboboxSelected>>", self.on_entry_point_changed)
        
        # Exit point
        tk.Label(controls_grid, text="Exit Point:", width=12, anchor=tk.W).grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.exit_point_var = tk.StringVar(value="Auto")
        self.exit_point_combo = ttk.Combobox(controls_grid, textvariable=self.exit_point_var,
                                            state="readonly", width=18)
        self.exit_point_combo.grid(row=1, column=3, padx=5, pady=3)
        self.exit_point_combo.bind("<<ComboboxSelected>>", self.on_exit_point_changed)
        
    def setup_settings_panel(self, parent):
        """Setup settings panel with tabs"""
        
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Settings tab
        settings_tab = ttk.Frame(notebook, padding=10)
        notebook.add(settings_tab, text="⚙️ Settings")
        
        # Create scrollable frame for settings
        settings_canvas = tk.Canvas(settings_tab, highlightthickness=0)
        settings_scroll = ttk.Scrollbar(settings_tab, orient=tk.VERTICAL, command=settings_canvas.yview)
        settings_frame = ttk.Frame(settings_canvas)
        
        settings_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
        settings_canvas.create_window((0, 0), window=settings_frame, anchor=tk.NW)
        settings_canvas.configure(yscrollcommand=settings_scroll.set)
        
        settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        settings_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings fields with modern styling
        settings_fields = [
            ("Cutting Feed Rate (mm/min):", "feed_rate_var", "100"),
            ("Safety Height (mm):", "safety_height_var", "10"),
            ("Cut Depth (mm):", "depth_var", "0"),
            ("Wire Temp (°C):", "temp_var", "200"),
        ]
        
        for i, (label_text, var_name, default) in enumerate(settings_fields):
            frame = tk.Frame(settings_frame, bg="#f8f9fa", relief=tk.FLAT, pady=8)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(frame, text=label_text, width=25, anchor=tk.W,
                    font=("Arial", 9), bg="#f8f9fa").pack(side=tk.LEFT, padx=10)
            
            var = tk.StringVar(value=default)
            setattr(self, var_name, var)
            entry = ttk.Entry(frame, textvariable=var, width=15, font=("Arial", 10))
            entry.pack(side=tk.LEFT, padx=5)
        
        # Units selector
        units_frame = tk.Frame(settings_frame, bg="#f8f9fa", relief=tk.FLAT, pady=8)
        units_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(units_frame, text="Units:", width=25, anchor=tk.W,
                font=("Arial", 9), bg="#f8f9fa").pack(side=tk.LEFT, padx=10)
        self.units_var = tk.StringVar(value="mm")
        units_radio_frame = tk.Frame(units_frame, bg="#f8f9fa")
        units_radio_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(units_radio_frame, text="mm", variable=self.units_var, value="mm").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(units_radio_frame, text="inches", variable=self.units_var, value="inches").pack(side=tk.LEFT, padx=5)
        
        # Preview tab
        preview_tab = ttk.Frame(notebook, padding=10)
        notebook.add(preview_tab, text="📄 G-code Preview")
        
        # Preview text with syntax highlighting background
        preview_header = tk.Frame(preview_tab, bg="#34495e", height=30)
        preview_header.pack(fill=tk.X)
        preview_header.pack_propagate(False)
        tk.Label(preview_header, text="Generated G-code", bg="#34495e", fg="#ecf0f1",
                font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT)
        
        preview_text_frame = tk.Frame(preview_tab)
        preview_text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(preview_text_frame, wrap=tk.NONE, font=("Courier", 9),
                                   bg="#2c3e50", fg="#ecf0f1", insertbackground="white",
                                   selectbackground="#3498db")
        preview_scroll_v = ttk.Scrollbar(preview_text_frame, orient=tk.VERTICAL,
                                 command=self.preview_text.yview)
        preview_scroll_h = ttk.Scrollbar(preview_text_frame, orient=tk.HORIZONTAL,
                                        command=self.preview_text.xview)
        
        self.preview_text.configure(yscrollcommand=preview_scroll_v.set,
                                   xscrollcommand=preview_scroll_h.set)
        
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        preview_scroll_v.grid(row=0, column=1, sticky="ns")
        preview_scroll_h.grid(row=1, column=0, sticky="ew")
        preview_text_frame.grid_rowconfigure(0, weight=1)
        preview_text_frame.grid_columnconfigure(0, weight=1)
        
    # Canvas control methods
    def zoom_in(self):
        """Zoom in on canvas"""
        self.zoom_level *= 1.2
        self.update_shapes_list()
        self.status_label.config(text="Zoomed in")
        
    def zoom_out(self):
        """Zoom out on canvas"""
        self.zoom_level /= 1.2
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
        self.update_shapes_list()
        self.status_label.config(text="Zoomed out")
        
    def fit_to_window(self):
        """Fit all shapes to window"""
        self.zoom_level = 1.0
        self.update_shapes_list()
        self.status_label.config(text="Fitted to window")
        
    def on_mousewheel(self, event):
        """Handle mouse wheel zoom - cross-platform"""
        import sys
        if sys.platform == "win32":
            # Windows: event.delta is positive for up, negative for down
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        elif sys.platform == "darwin":
            # macOS: event.delta is positive for up, negative for down
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # Linux: event.num is 4 for up, 5 for down
            if event.num == 4:
                self.zoom_in()
            else:
                self.zoom_out()
            
    def on_pan_start(self, event):
        """Start panning"""
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.config(cursor="fleur")
        
    def on_pan_move(self, event):
        """Pan canvas"""
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            
    def on_pan_end(self, event):
        """End panning"""
        self.is_panning = False
        self.canvas.config(cursor="")
        
    # File operations
    def load_cad_file(self):
        """Load CAD file"""
        filename = filedialog.askopenfilename(
            title="Load CAD File",
            filetypes=[
                ("All CAD", "*.dxf *.svg *.json"),
                      ("DXF", "*.dxf"), 
                      ("SVG", "*.svg"),
                ("JSON", "*.json")
            ]
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
                    
                self.file_label.config(text=f"📄 {os.path.basename(filename)}")
                self.loaded_filename = filename  # Store for default save filename
                self.update_shapes_list()
                self.status_label.config(text=f"Loaded {len(self.shapes)} shapes")
                self.shape_count_status.config(text=f"Shapes: {len(self.shapes)}")
                messagebox.showinfo("Success", f"Loaded {len(self.shapes)} shapes")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")
                
    def load_dxf(self, filename):
        """Load DXF file"""
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
                pl_points = list(entity.get_points())
                
                for i, point_data in enumerate(pl_points):
                    x = float(point_data[0])
                    y = float(point_data[1])
                    bulge = float(point_data[4]) if len(point_data) > 4 else 0.0
                    points.append((x, y))
                    
                    if bulge != 0:
                        next_idx = (i + 1) % len(pl_points) if entity.closed else i + 1
                        if next_idx < len(pl_points):
                            p1 = points[i]
                            next_point_data = pl_points[next_idx]
                            p2 = (float(next_point_data[0]), float(next_point_data[1]))
                            
                            arc_angle = 4 * math.atan(abs(bulge))
                            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                            if dist > 0 and arc_angle > 0:
                                radius = dist / (2 * math.sin(arc_angle / 2))
                                mid_x = (p1[0] + p2[0]) / 2
                                mid_y = (p1[1] + p2[1]) / 2
                                dx = p2[0] - p1[0]
                                dy = p2[1] - p1[1]
                                perp_dist = radius * math.cos(arc_angle / 2)
                                if abs(dx) > abs(dy):
                                    center_x = mid_x
                                    center_y = mid_y + (perp_dist * (1 if bulge > 0 else -1))
                                else:
                                    center_x = mid_x + (perp_dist * (1 if bulge > 0 else -1))
                                    center_y = mid_y
                                
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
        """Update canvas with shapes"""
        self.canvas.delete("all")
        
        if self.edit_mode:
            self.canvas.create_text(10, 10, anchor=tk.NW, 
                                  text="✏️ Edit Mode: Click shapes to configure",
                                  fill="#3498db", font=("Arial", 10, "bold"))
        
        if not self.shapes:
            self.shape_count_status.config(text="Shapes: 0")
            return
            
        # Calculate bounding box
        all_x, all_y = [], []
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
            
            padding = max(width, height) * 0.1
            min_x -= padding
            min_y -= padding
            width += 2 * padding
            height += 2 * padding
            
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            if width > 0 and height > 0:
                scale_x = (canvas_width - 20) / width
                scale_y = (canvas_height - 20) / height
                scale = min(scale_x, scale_y, 1.0) * self.zoom_level
                
                offset_x = -min_x * scale + (canvas_width - width * scale) / 2
                offset_y = -min_y * scale + (canvas_height - height * scale) / 2
            else:
                scale = 1.0 * self.zoom_level
                offset_x = 0
                offset_y = 0
        else:
            scale = 1.0 * self.zoom_level
            offset_x = 0
            offset_y = 0
            
        # Draw shapes
        canvas_height = self.canvas.winfo_height() or 600
        for shape in self.shapes:
            shape_idx = self.shapes.index(shape)
            is_selected = (self.edit_mode and shape_idx == self.selected_shape_index)
            line_color = "#3498db" if is_selected else "#2c3e50"
            line_width = 3 if is_selected else 2
            
            if shape["type"] == "line":
                x1 = shape["x1"] * scale + offset_x
                y1 = canvas_height - (shape["y1"] * scale + offset_y)
                x2 = shape["x2"] * scale + offset_x
                y2 = canvas_height - (shape["y2"] * scale + offset_y)
                self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)

            elif shape["type"] == "circle":
                cx = shape["cx"] * scale + offset_x
                cy = canvas_height - (shape["cy"] * scale + offset_y)
                r = shape["radius"] * scale
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                      outline=line_color, width=line_width)

            elif shape["type"] == "rectangle":
                x1 = shape["x1"] * scale + offset_x
                y1 = canvas_height - (shape["y1"] * scale + offset_y)
                x2 = shape["x2"] * scale + offset_x
                y2 = canvas_height - (shape["y2"] * scale + offset_y)
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                            outline=line_color, width=line_width)

            elif shape["type"] == "arc":
                cx = shape["cx"] * scale + offset_x
                cy = canvas_height - (shape["cy"] * scale + offset_y)
                r = shape["radius"] * scale
                start_angle = shape.get("start_angle", 0)
                end_angle = shape.get("end_angle", 180)
                extent = end_angle - start_angle
                if extent > 360:
                    extent = extent % 360
                elif extent < -360:
                    extent = extent % -360
                self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                      start=180-end_angle, extent=extent,
                                      outline=line_color, width=line_width, style=tk.ARC)

            elif shape["type"] == "polyline":
                points = []
                cad_points = []
                for x, y in shape["points"]:
                    canvas_x = x * scale + offset_x
                    canvas_y = canvas_height - (y * scale + offset_y)
                    points.extend([canvas_x, canvas_y])
                    cad_points.append((x, y))
                    
                if len(points) >= 4:
                    self.canvas.create_line(*points, fill=line_color, width=line_width)
                    
                    # Draw arrows
                    self.draw_path_arrows(cad_points, scale, offset_x, offset_y, canvas_height, shape, is_selected)
                    
                    # Draw markers
                    self.draw_markers(shape, scale, offset_x, offset_y, canvas_height)
        
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
        self.canvas_scale = scale
        self.canvas_offset_x = offset_x
        self.canvas_offset_y = offset_y
        
    def draw_path_arrows(self, cad_points, scale, offset_x, offset_y, canvas_height, shape, is_selected):
        """Draw directional arrows"""
        if len(cad_points) < 2:
            return
        
        points_list = list(cad_points)
        start_idx = shape.get("start_index", 0)
        if start_idx > 0 and start_idx < len(points_list):
            points_list = points_list[start_idx:] + points_list[:start_idx]
        
        if shape.get("closed", False) and len(points_list) > 2:
            clockwise = shape.get("clockwise")
            if clockwise is not None:
                area = 0.0
                for i in range(len(points_list)):
                    j = (i + 1) % len(points_list)
                    area += points_list[i][0] * points_list[j][1]
                    area -= points_list[j][0] * points_list[i][1]
                is_naturally_clockwise = area < 0
                if clockwise != is_naturally_clockwise:
                    points_list = [points_list[0]] + list(reversed(points_list[1:]))
        
        total_length = 0
        for i in range(len(points_list)):
            next_i = (i + 1) % len(points_list) if shape.get("closed", False) else i + 1
            if next_i < len(points_list):
                dx = points_list[next_i][0] - points_list[i][0]
                dy = points_list[next_i][1] - points_list[i][1]
                total_length += math.sqrt(dx*dx + dy*dy)
        
        num_arrows = max(3, min(15, int(total_length / 25)))
        arrow_spacing = total_length / num_arrows if num_arrows > 0 else total_length
        
        current_length = 0
        target_length = arrow_spacing
        arrow_color = "#27ae60"
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
            
            dx_norm = dx / seg_length
            dy_norm = dy / seg_length
            
            while current_length + seg_length >= target_length:
                t = (target_length - current_length) / seg_length if seg_length > 0 else 0
                t = max(0, min(1, t))
                
                arrow_x = p1[0] + t * dx
                arrow_y = p1[1] + t * dy
                
                canvas_x = arrow_x * scale + offset_x
                canvas_y = canvas_height - (arrow_y * scale + offset_y)
                
                angle = math.atan2(dy_norm, dx_norm)
                arrow_len = arrow_size
                arrow_angle = math.pi / 6
                
                tip_x = canvas_x + arrow_len * math.cos(angle)
                tip_y = canvas_y - arrow_len * math.sin(angle)
                left_x = tip_x - arrow_len * 0.6 * math.cos(angle - arrow_angle)
                left_y = tip_y + arrow_len * 0.6 * math.sin(angle - arrow_angle)
                right_x = tip_x - arrow_len * 0.6 * math.cos(angle + arrow_angle)
                right_y = tip_y + arrow_len * 0.6 * math.sin(angle + arrow_angle)
                
                self.canvas.create_line(canvas_x, canvas_y, tip_x, tip_y, fill=arrow_color, width=2)
                self.canvas.create_line(tip_x, tip_y, left_x, left_y, fill=arrow_color, width=2)
                self.canvas.create_line(tip_x, tip_y, right_x, right_y, fill=arrow_color, width=2)
                
                target_length += arrow_spacing
            
            current_length += seg_length
            if current_length >= target_length:
                current_length -= target_length
                target_length = arrow_spacing
        
    def draw_markers(self, shape, scale, offset_x, offset_y, canvas_height):
        """Draw start/entry/exit point markers"""
        points = shape.get("points", [])
        
        # Start point
        start_idx = shape.get("start_index")
        if start_idx is not None and 0 <= start_idx < len(points):
            pt = points[start_idx]
            sx = pt[0] * scale + offset_x
            sy = canvas_height - (pt[1] * scale + offset_y)
            self.canvas.create_oval(sx - 6, sy - 6, sx + 6, sy + 6,
                                  fill="#27ae60", outline="#1e8449", width=2)
            self.canvas.create_text(sx, sy - 12, text="START", fill="#27ae60",
                                   font=("Arial", 8, "bold"))
        
        # Entry point
        entry_idx = shape.get("entry_index")
        if entry_idx is not None and 0 <= entry_idx < len(points):
            pt = points[entry_idx]
            ex = pt[0] * scale + offset_x
            ey = canvas_height - (pt[1] * scale + offset_y)
            self.canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                  fill="#3498db", outline="#2980b9", width=2)
            self.canvas.create_text(ex, ey - 12, text="ENTRY", fill="#3498db",
                                   font=("Arial", 8, "bold"))
        
        # Exit point
        exit_idx = shape.get("exit_index")
        if exit_idx is not None and 0 <= exit_idx < len(points):
            pt = points[exit_idx]
            ex = pt[0] * scale + offset_x
            ey = canvas_height - (pt[1] * scale + offset_y)
            self.canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                  fill="#e74c3c", outline="#c0392b", width=2)
            self.canvas.create_text(ex, ey - 12, text="EXIT", fill="#e74c3c",
                                   font=("Arial", 8, "bold"))
    
    # Event handlers
    def toggle_edit_mode(self):
        """Toggle edit mode on/off"""
        self.edit_mode = self.edit_mode_var.get()
        print(f"Edit mode toggled: {self.edit_mode}")
        if self.edit_mode:
            self.canvas.config(cursor="crosshair")
            # Ensure click binding is active (already bound, but ensure it's active)
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.status_label.config(text="Edit Mode: Click shapes or points to configure")
            print("Edit mode ON - click handler bound")
        else:
            self.canvas.config(cursor="")
            self.selected_shape_index = None
            self.selected_label.config(text="Selected: None")
            self.status_label.config(text="Ready")
            print("Edit mode OFF")
        self.update_shapes_list()  # Redraw with selection highlights
    
    def on_canvas_click(self, event):
        """Handle canvas click - select shape or point with full functionality"""
        # Visual feedback - draw a small marker at click location
        self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, 
                               fill="yellow", outline="orange", width=2, tags="click_marker")
        self.root.after(1000, lambda: self.canvas.delete("click_marker"))
        
        # Debug output (matching original)
        print(f"Canvas clicked at ({event.x}, {event.y}), edit_mode={self.edit_mode}, shapes={len(self.shapes)}")
        
        if not self.edit_mode:
            print("Edit mode is False, returning")
            return
        
        if not self.shapes:
            print("No shapes loaded!")
            self.selected_label.config(text="No shapes loaded! Please load a CAD file first.")
            self.status_label.config(text="No shapes loaded")
            return
        
        # Convert canvas coordinates to CAD coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Get actual canvas dimensions
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
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
        
        # Debug output (matching original)
        print(f"Converting click: canvas=({canvas_x:.1f}, {canvas_y:.1f}) -> CAD=({cad_x:.1f}, {cad_y:.1f})")
        print(f"Canvas scale={self.canvas_scale:.4f}, offset=({self.canvas_offset_x:.1f}, {self.canvas_offset_y:.1f})")
        
        # Find closest shape or point
        closest_shape_idx = None
        closest_point_idx = None
        min_dist = float('inf')
        all_distances = []
        
        # Debug output (matching original)
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
            self.status_label.config(text=f"Selected: Shape {closest_shape_idx + 1}")
            
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
            self.status_label.config(text="No shape found at click location")
            self.start_point_var.set("Auto")
            self.direction_var.set("Auto")
            self.entry_point_var.set("Auto")
            self.exit_point_var.set("Auto")
    
    def on_start_point_changed(self, event=None):
        """Handle start point change"""
        if self.selected_shape_index is None:
            return
        shape = self.shapes[self.selected_shape_index]
        if shape["type"] != "polyline":
            return
        selected = self.start_point_var.get()
        if selected == "Auto":
            shape["start_index"] = None
        else:
            try:
                point_num = int(selected.split()[-1]) - 1
                if 0 <= point_num < len(shape.get("points", [])):
                    shape["start_index"] = point_num
            except (ValueError, IndexError):
                pass
        self.update_shapes_list()
    
    def on_direction_changed(self, event=None):
        """Handle direction change"""
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
        """Handle entry point change"""
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
        """Handle exit point change"""
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
    
    # G-code generation
    def generate_gcode(self):
        """Generate G-code"""
        if not self.shapes:
            messagebox.showwarning("Warning", "No shapes loaded. Please load a CAD file first.")
            return
            
        try:
            feed_rate = float(self.feed_rate_var.get())
            depth = float(self.depth_var.get())
            safety_height = float(self.safety_height_var.get())
            units = self.units_var.get()
            temp = float(self.temp_var.get())
            
            self.status_label.config(text="Generating G-code...")
            self.root.update()
            
            gen = GCodeGenerator()
            gen.set_units(units)
            gen.set_feed_rate(feed_rate)
            gen.set_safety_height(safety_height)
            gen.set_wire_temp(temp)
            
            gen.header("Foam Cutting from CAD File")
            gen.generate_from_shapes(self.shapes, depth=depth)
            gen.footer()
            
            gcode = gen.get_gcode()
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, gcode)
            
            self.current_gcode = gcode
            self.current_generator = gen
            
            self.status_label.config(text="G-code generated successfully!")
            messagebox.showinfo("Success", "G-code generated successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input value: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate G-code: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def save_gcode(self):
        """Save G-code to file"""
        if not hasattr(self, 'current_gcode'):
            messagebox.showwarning("Warning", "Please generate G-code first.")
            return
        
        # Suggest filename based on loaded CAD file
        default_filename = "output.gcode"
        if hasattr(self, 'loaded_filename') and self.loaded_filename:
            base_name = os.path.splitext(os.path.basename(self.loaded_filename))[0]
            default_filename = f"{base_name}.gcode"
            
        filename = filedialog.asksaveasfilename(
            title="Save G-code",
            defaultextension=".gcode",
            initialfile=default_filename,
            filetypes=[
                ("G-code", "*.gcode"),
                ("G-code", "*.nc"),
                ("Text", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            try:
                self.current_generator.save(filename)
                self.status_label.config(text=f"Saved to {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"G-code saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")


# Alias for backward compatibility
CADToGCodeConverter = ModernCADToGCodeConverter


def main():
    root = tk.Tk()
    app = ModernCADToGCodeConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
