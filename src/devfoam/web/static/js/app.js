/**
 * DevFoam Web Application
 * Interactive CAD to G-code converter for foam cutting
 */

class DevFoamApp {
    constructor() {
        this.shapes = null;
        this.gcode = null;
        this.canvas = document.getElementById('cadCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Canvas state
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;

        // Edit mode state
        this.editMode = false;
        this.selectedShapeIndex = null;
        this.selectedShapeType = null;

        // Track if we've done initial auto-fit
        this.hasAutoFitted = false;

        this.initializeEventListeners();
        this.drawGrid();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // File upload
        document.getElementById('uploadBtn').addEventListener('click', () => this.handleUpload());
        document.getElementById('fileInput').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('fileInfo').textContent = `Selected: ${file.name}`;
            }
        });

        // Generate G-code
        document.getElementById('generateBtn').addEventListener('click', () => this.generateGCode());

        // Download G-code
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadGCode());

        // Canvas controls
        document.getElementById('zoomInBtn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoomOutBtn').addEventListener('click', () => this.zoomOut());
        document.getElementById('resetViewBtn').addEventListener('click', () => this.resetView());

        // Edit mode
        document.getElementById('editModeCheckbox').addEventListener('change', (e) => this.toggleEditMode(e.target.checked));

        // Path controls
        document.getElementById('startPoint').addEventListener('change', (e) => this.onStartPointChanged(e.target.value));
        document.getElementById('direction').addEventListener('change', (e) => this.onDirectionChanged(e.target.value));

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Canvas mouse events
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
    }

    /**
     * Handle file upload
     */
    async handleUpload() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];

        if (!file) {
            this.setStatus('Please select a file first', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        this.setStatus('Uploading file...', 'loading');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.shapes = data.shapes;
                this.hasAutoFitted = false; // Reset so auto-fit happens on new file
                this.setStatus(`Loaded: ${data.filename}`, 'success');
                this.renderShapes();
                document.getElementById('generateBtn').disabled = false;
            } else {
                this.setStatus(data.error || 'Upload failed', 'error');
            }
        } catch (error) {
            this.setStatus(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Generate G-code from current shapes
     */
    async generateGCode() {
        if (!this.shapes) {
            this.setStatus('No shapes loaded', 'error');
            return;
        }

        const params = {
            shapes: this.shapes,
            feed_rate: parseFloat(document.getElementById('feedRate').value),
            safety_height: parseFloat(document.getElementById('safetyHeight').value),
            wire_temp: parseFloat(document.getElementById('wireTemp').value),
            units: document.getElementById('units').value,
            depth: parseFloat(document.getElementById('depth').value)
        };

        this.setStatus('Generating G-code...', 'loading');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();

            if (data.success) {
                this.gcode = data.gcode;
                document.getElementById('gcodeOutput').textContent = data.gcode;
                document.getElementById('lineCount').textContent = `${data.line_count} lines`;
                document.getElementById('downloadBtn').disabled = false;
                this.setStatus('G-code generated successfully', 'success');
                this.switchTab('gcode');
            } else {
                this.setStatus(data.error || 'Generation failed', 'error');
            }
        } catch (error) {
            this.setStatus(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Download generated G-code
     */
    async downloadGCode() {
        if (!this.gcode) {
            this.setStatus('No G-code to download', 'error');
            return;
        }

        const filename = 'devfoam_output.nc';

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gcode: this.gcode,
                    filename: filename
                })
            });

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.setStatus('G-code downloaded', 'success');
        } catch (error) {
            this.setStatus(`Download error: ${error.message}`, 'error');
        }
    }

    /**
     * Render shapes on canvas
     */
    renderShapes() {
        if (!this.shapes) return;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();

        // Save context state
        this.ctx.save();

        // Calculate bounds for auto-fit (only on first render after loading)
        if (!this.hasAutoFitted) {
            const bounds = this.calculateBounds();
            if (bounds) {
                const scale = Math.min(
                    (this.canvas.width * 0.8) / (bounds.maxX - bounds.minX),
                    (this.canvas.height * 0.8) / (bounds.maxY - bounds.minY)
                );
                this.zoom = scale;
                this.panX = -(bounds.minX + bounds.maxX) / 2;
                this.panY = -(bounds.minY + bounds.maxY) / 2;
                this.hasAutoFitted = true;
            }
        }

        // Apply transformations
        this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.scale(this.zoom, -this.zoom); // Flip Y-axis for CAD coordinates
        this.ctx.translate(this.panX, this.panY);

        // Draw shapes
        const defaultLineWidth = 2 / this.zoom;
        const selectedLineWidth = 4 / this.zoom;

        // Draw lines
        if (this.shapes.lines) {
            this.shapes.lines.forEach((line, index) => {
                const isSelected = this.editMode && this.selectedShapeType === 'line' && this.selectedShapeIndex === index;
                this.ctx.strokeStyle = isSelected ? '#3498db' : '#2c3e50';
                this.ctx.lineWidth = isSelected ? selectedLineWidth : defaultLineWidth;

                this.ctx.beginPath();
                this.ctx.moveTo(line.x1, line.y1);
                this.ctx.lineTo(line.x2, line.y2);
                this.ctx.stroke();

                // Draw arrows on lines
                const points = [{x: line.x1, y: line.y1}, {x: line.x2, y: line.y2}];
                this.drawPathArrows(points, false);
            });
        }

        // Draw circles
        if (this.shapes.circles) {
            this.shapes.circles.forEach((circle, index) => {
                const isSelected = this.editMode && this.selectedShapeType === 'circle' && this.selectedShapeIndex === index;
                this.ctx.strokeStyle = isSelected ? '#3498db' : '#2c3e50';
                this.ctx.lineWidth = isSelected ? selectedLineWidth : defaultLineWidth;

                this.ctx.beginPath();
                this.ctx.arc(circle.cx, circle.cy, circle.radius, 0, 2 * Math.PI);
                this.ctx.stroke();

                // Draw arrows on circles - sample points along circumference
                const points = this.sampleCirclePoints(circle.cx, circle.cy, circle.radius);
                this.drawPathArrows(points, true);
            });
        }

        // Draw rectangles
        if (this.shapes.rectangles) {
            this.shapes.rectangles.forEach((rect, index) => {
                const isSelected = this.editMode && this.selectedShapeType === 'rectangle' && this.selectedShapeIndex === index;
                this.ctx.strokeStyle = isSelected ? '#3498db' : '#27ae60';
                this.ctx.lineWidth = isSelected ? selectedLineWidth : defaultLineWidth;

                const width = rect.x2 - rect.x1;
                const height = rect.y2 - rect.y1;
                this.ctx.strokeRect(rect.x1, rect.y1, width, height);

                // Draw arrows on rectangles
                const points = [
                    {x: rect.x1, y: rect.y1},
                    {x: rect.x2, y: rect.y1},
                    {x: rect.x2, y: rect.y2},
                    {x: rect.x1, y: rect.y2}
                ];
                this.drawPathArrows(points, true);
            });
        }

        // Draw polylines
        if (this.shapes.polylines) {
            this.shapes.polylines.forEach((poly, index) => {
                if (poly.points && poly.points.length > 0) {
                    const isSelected = this.editMode && this.selectedShapeType === 'polyline' && this.selectedShapeIndex === index;
                    this.ctx.strokeStyle = isSelected ? '#3498db' : '#e74c3c';
                    this.ctx.lineWidth = isSelected ? selectedLineWidth : defaultLineWidth;

                    // Normalize points to {x, y} format
                    const normalizedPoints = poly.points.map(pt => {
                        if (typeof pt === 'object' && 'x' in pt && 'y' in pt) {
                            return { x: pt.x, y: pt.y };
                        } else if (Array.isArray(pt)) {
                            return { x: pt[0], y: pt[1] };
                        }
                        return { x: 0, y: 0 };
                    });

                    // Get reordered points if a start point is selected
                    const startPointIndex = poly.start_index;
                    const renderPoints = this.getReorderedPoints(normalizedPoints, poly.closed, startPointIndex);

                    this.ctx.beginPath();
                    this.ctx.moveTo(renderPoints[0].x, renderPoints[0].y);
                    for (let i = 1; i < renderPoints.length; i++) {
                        this.ctx.lineTo(renderPoints[i].x, renderPoints[i].y);
                    }
                    if (poly.closed) {
                        this.ctx.closePath();
                    }
                    this.ctx.stroke();

                    // Draw arrows on polylines (using reordered points)
                    this.drawPathArrows(renderPoints, poly.closed);

                    // Draw START marker for all shapes with start_index (matching desktop behavior)
                    this.drawStartMarker(poly, normalizedPoints);

                    // Draw entry/exit points if selected (for additional feedback)
                    if (isSelected) {
                        this.drawEntryExitPoints(renderPoints, poly.closed, 0); // Entry is now always at index 0 after reordering
                    }
                }
            });
        }

        // Restore context
        this.ctx.restore();

        // Update canvas status
        const shapeCount = (this.shapes.lines?.length || 0) +
                          (this.shapes.circles?.length || 0) +
                          (this.shapes.rectangles?.length || 0) +
                          (this.shapes.polylines?.length || 0);
        document.getElementById('canvasStatus').textContent =
            `${shapeCount} shapes | Zoom: ${(this.zoom * 100).toFixed(0)}%`;
    }

    /**
     * Reorder points based on selected start point
     */
    getReorderedPoints(points, closed, startPointIndex) {
        // If no start point selected or auto, return original order
        if (startPointIndex === undefined || startPointIndex === 'auto' || startPointIndex === null) {
            return points;
        }

        const startIdx = typeof startPointIndex === 'number' ? startPointIndex : parseInt(startPointIndex);

        if (isNaN(startIdx) || startIdx < 0 || startIdx >= points.length) {
            return points;
        }

        // If start is already at 0, no need to reorder
        if (startIdx === 0) {
            return points;
        }

        // Reorder points to start from selected index
        const reordered = [];
        for (let i = 0; i < points.length; i++) {
            const idx = (startIdx + i) % points.length;
            reordered.push(points[idx]);
        }

        return reordered;
    }

    /**
     * Sample points along a circle for arrow placement
     */
    sampleCirclePoints(cx, cy, radius, numPoints = 32) {
        const points = [];
        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * 2 * Math.PI;
            points.push({
                x: cx + radius * Math.cos(angle),
                y: cy + radius * Math.sin(angle)
            });
        }
        return points;
    }

    /**
     * Draw directional arrows along a path
     */
    drawPathArrows(points, closed) {
        if (!points || points.length < 2) return;

        // Calculate total path length
        let totalLength = 0;
        for (let i = 0; i < points.length - 1; i++) {
            const dx = points[i + 1].x - points[i].x;
            const dy = points[i + 1].y - points[i].y;
            totalLength += Math.sqrt(dx * dx + dy * dy);
        }

        if (closed && points.length > 2) {
            const dx = points[0].x - points[points.length - 1].x;
            const dy = points[0].y - points[points.length - 1].y;
            totalLength += Math.sqrt(dx * dx + dy * dy);
        }

        // Determine number of arrows based on path length
        const numArrows = Math.max(3, Math.min(15, Math.floor(totalLength / 25)));
        const arrowSpacing = totalLength / numArrows;

        // Arrow styling
        const arrowColor = '#27ae60';
        const arrowSize = 8 / this.zoom;
        const arrowAngle = Math.PI / 6;

        // Track distance along path
        let targetLength = arrowSpacing;
        let currentLength = 0;

        // Draw arrows along each segment
        for (let i = 0; i < points.length - 1; i++) {
            const p1 = points[i];
            const p2 = points[i + 1];
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const segmentLength = Math.sqrt(dx * dx + dy * dy);

            while (currentLength + segmentLength >= targetLength && targetLength <= totalLength) {
                const t = (targetLength - currentLength) / segmentLength;

                // Arrow position
                const arrowX = p1.x + t * dx;
                const arrowY = p1.y + t * dy;

                // Arrow direction angle
                const angle = Math.atan2(dy, dx);

                // Draw arrow
                this.drawArrow(arrowX, arrowY, angle, arrowSize, arrowColor, arrowAngle);

                targetLength += arrowSpacing;
            }

            currentLength += segmentLength;
        }

        // Handle closed path - draw arrows on closing segment
        if (closed && points.length > 2) {
            const p1 = points[points.length - 1];
            const p2 = points[0];
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const segmentLength = Math.sqrt(dx * dx + dy * dy);

            while (currentLength + segmentLength >= targetLength && targetLength <= totalLength) {
                const t = (targetLength - currentLength) / segmentLength;

                const arrowX = p1.x + t * dx;
                const arrowY = p1.y + t * dy;
                const angle = Math.atan2(dy, dx);

                this.drawArrow(arrowX, arrowY, angle, arrowSize, arrowColor, arrowAngle);

                targetLength += arrowSpacing;
            }
        }
    }

    /**
     * Draw a single arrow at specified position and angle
     */
    drawArrow(x, y, angle, size, color, arrowAngle) {
        this.ctx.save();

        // Set arrow style
        this.ctx.strokeStyle = color;
        this.ctx.fillStyle = color;
        this.ctx.lineWidth = 2 / this.zoom;

        // Calculate arrow tip and wings
        const tipX = x + size * Math.cos(angle);
        const tipY = y + size * Math.sin(angle);

        const leftX = tipX - size * 0.6 * Math.cos(angle - arrowAngle);
        const leftY = tipY - size * 0.6 * Math.sin(angle - arrowAngle);

        const rightX = tipX - size * 0.6 * Math.cos(angle + arrowAngle);
        const rightY = tipY - size * 0.6 * Math.sin(angle + arrowAngle);

        // Draw arrow shaft
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(tipX, tipY);
        this.ctx.stroke();

        // Draw arrow head
        this.ctx.beginPath();
        this.ctx.moveTo(tipX, tipY);
        this.ctx.lineTo(leftX, leftY);
        this.ctx.stroke();

        this.ctx.beginPath();
        this.ctx.moveTo(tipX, tipY);
        this.ctx.lineTo(rightX, rightY);
        this.ctx.stroke();

        this.ctx.restore();
    }

    /**
     * Draw START marker for a shape (matching desktop behavior)
     * Draws for ALL shapes with start_index, not just selected ones
     */
    drawStartMarker(poly, points) {
        const startIdx = poly.start_index;
        
        // Only draw if start_index is set and valid
        if (startIdx === undefined || startIdx === null || startIdx < 0 || startIdx >= points.length) {
            return;
        }

        const startPoint = points[startIdx];
        const markerSize = 6 / this.zoom; // Match desktop size (6 pixels)

        // Draw START marker (green circle) - matching desktop
        this.ctx.save();
        this.ctx.fillStyle = '#27ae60';
        this.ctx.strokeStyle = '#1e8449';
        this.ctx.lineWidth = 2 / this.zoom;
        this.ctx.beginPath();
        this.ctx.arc(startPoint.x, startPoint.y, markerSize, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();
        this.ctx.restore();

        // Draw "START" label - matching desktop
        const fontSize = 8 / this.zoom; // Match desktop font size
        this.ctx.save();
        this.ctx.scale(1, -1); // Flip text back to normal (Y is flipped)
        this.ctx.font = `bold ${fontSize}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillStyle = '#27ae60';
        this.ctx.fillText('START', startPoint.x, -startPoint.y - markerSize - 6 / this.zoom);
        this.ctx.restore();
    }

    /**
     * Draw entry and exit points for a selected path (additional feedback)
     */
    drawEntryExitPoints(points, closed, startPointIndex) {
        if (!points || points.length === 0) {
            return;
        }

        // Entry is always at index 0 because points are already reordered
        const entryIndex = 0;
        const entry = points[entryIndex];

        const markerSize = 12 / this.zoom;

        // Entry point (blue circle) - for selected shapes only
        this.ctx.save();
        this.ctx.fillStyle = '#3498db';
        this.ctx.strokeStyle = '#2980b9';
        this.ctx.lineWidth = 3 / this.zoom;
        this.ctx.beginPath();
        this.ctx.arc(entry.x, entry.y, markerSize, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();
        this.ctx.restore();

        // Exit point (red circle) - for non-closed paths
        if (!closed && points.length > 1) {
            const exitIndex = points.length - 1;
            const exit = points[exitIndex];

            this.ctx.save();
            this.ctx.fillStyle = '#e74c3c';
            this.ctx.strokeStyle = '#c0392b';
            this.ctx.lineWidth = 3 / this.zoom;
            this.ctx.beginPath();
            this.ctx.arc(exit.x, exit.y, markerSize, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();
            this.ctx.restore();
        }

        // Draw labels with better visibility
        const fontSize = 14 / this.zoom;
        this.ctx.save();
        this.ctx.scale(1, -1); // Flip text back to normal
        this.ctx.font = `bold ${fontSize}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // Entry label with background
        this.ctx.fillStyle = '#2980b9';
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 4 / this.zoom;
        this.ctx.strokeText('ENTRY', entry.x, -entry.y - markerSize - 5 / this.zoom);
        this.ctx.fillText('ENTRY', entry.x, -entry.y - markerSize - 5 / this.zoom);

        // Exit label (for open paths)
        if (!closed && points.length > 1) {
            const exitIndex = points.length - 1;
            const exit = points[exitIndex];
            this.ctx.fillStyle = '#c0392b';
            this.ctx.strokeStyle = 'white';
            this.ctx.strokeText('EXIT', exit.x, -exit.y - markerSize - 5 / this.zoom);
            this.ctx.fillText('EXIT', exit.x, -exit.y - markerSize - 5 / this.zoom);
        }

        this.ctx.restore();
    }

    /**
     * Calculate bounding box for all shapes
     */
    calculateBounds() {
        if (!this.shapes) return null;

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        const updateBounds = (x, y) => {
            minX = Math.min(minX, x);
            minY = Math.min(minY, y);
            maxX = Math.max(maxX, x);
            maxY = Math.max(maxY, y);
        };

        // Process all shape types
        if (this.shapes.lines) {
            this.shapes.lines.forEach(line => {
                updateBounds(line.x1, line.y1);
                updateBounds(line.x2, line.y2);
            });
        }

        if (this.shapes.circles) {
            this.shapes.circles.forEach(circle => {
                updateBounds(circle.cx - circle.radius, circle.cy - circle.radius);
                updateBounds(circle.cx + circle.radius, circle.cy + circle.radius);
            });
        }

        if (this.shapes.rectangles) {
            this.shapes.rectangles.forEach(rect => {
                updateBounds(rect.x1, rect.y1);
                updateBounds(rect.x2, rect.y2);
            });
        }

        if (this.shapes.polylines) {
            this.shapes.polylines.forEach(poly => {
                poly.points.forEach(pt => updateBounds(pt.x, pt.y));
            });
        }

        return minX !== Infinity ? { minX, minY, maxX, maxY } : null;
    }

    /**
     * Draw grid on canvas
     */
    drawGrid() {
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 0.5;

        const gridSize = 50;
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    /**
     * Canvas zoom controls
     */
    zoomIn() {
        this.zoom *= 1.2;
        this.renderShapes();
    }

    zoomOut() {
        this.zoom /= 1.2;
        this.renderShapes();
    }

    resetView() {
        this.hasAutoFitted = false; // Trigger auto-fit on next render
        this.renderShapes();
    }

    /**
     * Canvas mouse event handlers
     */
    handleMouseDown(e) {
        this.mouseDownX = e.clientX;
        this.mouseDownY = e.clientY;
        this.mouseDownTime = Date.now();

        // Don't start dragging if in edit mode
        if (this.editMode) {
            return;
        }
        this.isDragging = true;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
    }

    handleMouseMove(e) {
        if (!this.isDragging) {
            // Update cursor based on edit mode
            if (this.editMode) {
                this.canvas.style.cursor = 'crosshair';
            } else {
                this.canvas.style.cursor = 'grab';
            }
            return;
        }

        this.canvas.style.cursor = 'grabbing';

        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;

        this.panX += dx / this.zoom;
        this.panY -= dy / this.zoom; // Invert Y for CAD coordinates

        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;

        this.renderShapes();
    }

    handleMouseUp(e) {
        // Handle case where e might be undefined (from mouseleave event)
        if (!e) {
            this.isDragging = false;
            this.canvas.style.cursor = this.editMode ? 'crosshair' : 'grab';
            return;
        }

        // Check if this was a click (not a drag)
        const timeDiff = Date.now() - this.mouseDownTime;
        const distX = Math.abs(e.clientX - this.mouseDownX);
        const distY = Math.abs(e.clientY - this.mouseDownY);
        const isClick = timeDiff < 300 && distX < 5 && distY < 5;

        console.log('MouseUp - isClick:', isClick, 'editMode:', this.editMode);

        if (isClick && this.editMode) {
            this.handleCanvasClick(e);
        }

        this.isDragging = false;
        this.canvas.style.cursor = this.editMode ? 'crosshair' : 'grab';
    }

    handleWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoom *= delta;
        this.renderShapes();
    }

    handleCanvasClick(e) {
        console.log('Canvas clicked! Edit mode:', this.editMode, 'Has shapes:', !!this.shapes);

        if (!this.editMode || !this.shapes) {
            console.log('  -> Ignoring click (edit mode off or no shapes)');
            return;
        }

        const rect = this.canvas.getBoundingClientRect();
        const canvasX = e.clientX - rect.left;
        const canvasY = e.clientY - rect.top;

        console.log('  -> Canvas coords:', canvasX, canvasY);

        // Convert to CAD coordinates
        // Transform order: translate(center) -> scale(zoom, -zoom) -> translate(panX, panY)
        // To reverse: reverse pan, reverse scale, reverse center
        const cadX = (canvasX - this.canvas.width / 2) / this.zoom - this.panX;
        const cadY = -(canvasY - this.canvas.height / 2) / this.zoom - this.panY;

        console.log('  -> CAD coords:', cadX, cadY);
        console.log('  -> Zoom:', this.zoom, 'Pan:', this.panX, this.panY);
        console.log('  -> Shapes available:', {
            polylines: this.shapes.polylines?.length || 0,
            lines: this.shapes.lines?.length || 0,
            circles: this.shapes.circles?.length || 0,
            rectangles: this.shapes.rectangles?.length || 0
        });

        // Find clicked shape and point (matching desktop behavior)
        const result = this.findShapeAndPointAtLocation(cadX, cadY);

        console.log('  -> Found:', result);

        if (result && result.shapeIndex !== null) {
            this.selectShape(result.type, result.shapeIndex, result.pointIndex);
        } else {
            console.log('  -> No shape found at location');
            this.deselectShape();
        }
    }

    /**
     * Toggle edit mode
     */
    toggleEditMode(enabled) {
        console.log('===== TOGGLE EDIT MODE =====');
        console.log('Enabled:', enabled);
        this.editMode = enabled;
        console.log('this.editMode now:', this.editMode);
        if (!enabled) {
            this.deselectShape();
        }
        this.canvas.style.cursor = enabled ? 'crosshair' : 'grab';
        console.log('Cursor set to:', this.canvas.style.cursor);
        this.renderShapes();
        this.setStatus(enabled ? 'Edit Mode: Click shapes to configure' : 'Ready');
        console.log('===== EDIT MODE TOGGLE COMPLETE =====');
    }

    /**
     * Find shape and point at clicked location (matching desktop behavior)
     * First checks vertices, then falls back to line segments
     */
    findShapeAndPointAtLocation(x, y) {
        const vertexThreshold = 50.0; // CAD units - same as desktop
        const lineThreshold = 30.0; // CAD units for line segments
        
        console.log(`  Searching for shape at CAD location (${x.toFixed(2)}, ${y.toFixed(2)})`);
        
        let closestShapeIdx = null;
        let closestPointIdx = null;
        let minDist = Infinity;
        
        // First, try to find closest vertex (point) - with corner snapping
        if (this.shapes.polylines && this.shapes.polylines.length > 0) {
            console.log(`  Checking ${this.shapes.polylines.length} polylines for vertices...`);
            for (let i = 0; i < this.shapes.polylines.length; i++) {
                const poly = this.shapes.polylines[i];
                if (!poly.points || poly.points.length === 0) {
                    console.log(`    Shape ${i}: no points`);
                    continue;
                }
                
                console.log(`    Shape ${i}: ${poly.points.length} points`);
                for (let ptIdx = 0; ptIdx < poly.points.length; ptIdx++) {
                    const pt = poly.points[ptIdx];
                    const px = typeof pt === 'object' && 'x' in pt ? pt.x : (Array.isArray(pt) ? pt[0] : 0);
                    const py = typeof pt === 'object' && 'y' in pt ? pt.y : (Array.isArray(pt) ? pt[1] : 0);
                    
                    const dist = Math.sqrt((px - x) ** 2 + (py - y) ** 2);
                    
                    if (ptIdx < 3) {
                        console.log(`      Point ${ptIdx}: (${px.toFixed(2)}, ${py.toFixed(2)}), dist=${dist.toFixed(2)}`);
                    }
                    
                    if (dist < vertexThreshold && dist < minDist) {
                        minDist = dist;
                        closestShapeIdx = i;
                        closestPointIdx = ptIdx;
                        console.log(`  ✓ Found closer point: shape ${i}, point ${ptIdx}, dist=${dist.toFixed(2)}, threshold=${vertexThreshold.toFixed(2)}`);
                    }
                }
            }
        } else {
            console.log('  No polylines found in shapes');
        }
        
        // If no vertex found, try to find closest line segment
        if (closestShapeIdx === null) {
            console.log('  No point found, checking line segments...');
            let minLineDist = Infinity;
            
            if (this.shapes.polylines && this.shapes.polylines.length > 0) {
                for (let i = 0; i < this.shapes.polylines.length; i++) {
                    const poly = this.shapes.polylines[i];
                    if (!poly.points || poly.points.length < 2) continue;
                    
                    // Check each line segment
                    for (let segIdx = 0; segIdx < poly.points.length; segIdx++) {
                        const nextIdx = poly.closed ? (segIdx + 1) % poly.points.length : segIdx + 1;
                        if (nextIdx >= poly.points.length) continue;
                        
                        const p1 = poly.points[segIdx];
                        const p2 = poly.points[nextIdx];
                        const x1 = typeof p1 === 'object' && 'x' in p1 ? p1.x : (Array.isArray(p1) ? p1[0] : 0);
                        const y1 = typeof p1 === 'object' && 'y' in p1 ? p1.y : (Array.isArray(p1) ? p1[1] : 0);
                        const x2 = typeof p2 === 'object' && 'x' in p2 ? p2.x : (Array.isArray(p2) ? p2[0] : 0);
                        const y2 = typeof p2 === 'object' && 'y' in p2 ? p2.y : (Array.isArray(p2) ? p2[1] : 0);
                        
                        const dist = this.pointToSegmentDistance(x, y, x1, y1, x2, y2);
                        
                        if (dist < lineThreshold && dist < minLineDist) {
                            minLineDist = dist;
                            closestShapeIdx = i;
                            // Use the closer endpoint as the start point
                            const dist1 = Math.sqrt((x - x1) ** 2 + (y - y1) ** 2);
                            const dist2 = Math.sqrt((x - x2) ** 2 + (y - y2) ** 2);
                            closestPointIdx = dist1 < dist2 ? segIdx : nextIdx;
                            console.log(`  ✓ Found line segment: shape ${i}, segment ${segIdx}-${nextIdx}, dist=${dist.toFixed(2)}`);
                        }
                    }
                }
            }
        }
        
        if (closestShapeIdx !== null) {
            return {
                type: 'polyline',
                shapeIndex: closestShapeIdx,
                pointIndex: closestPointIdx
            };
        }
        
        console.log('  No shape found');
        return null;
    }

    /**
     * Check if point is near a path
     */
    isPointNearPath(x, y, points, closed, threshold) {
        for (let i = 0; i < points.length - 1; i++) {
            const p1 = points[i];
            const p2 = points[i + 1];
            const dist = this.pointToSegmentDistance(x, y, p1.x, p1.y, p2.x, p2.y);
            if (dist < threshold) return true;
        }

        // Check closing segment for closed paths
        if (closed && points.length > 2) {
            const p1 = points[points.length - 1];
            const p2 = points[0];
            const dist = this.pointToSegmentDistance(x, y, p1.x, p1.y, p2.x, p2.y);
            if (dist < threshold) return true;
        }

        return false;
    }

    /**
     * Calculate distance from point to line segment
     */
    pointToSegmentDistance(px, py, x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const lengthSq = dx * dx + dy * dy;

        if (lengthSq === 0) {
            return Math.sqrt((px - x1) ** 2 + (py - y1) ** 2);
        }

        const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / lengthSq));
        const projX = x1 + t * dx;
        const projY = y1 + t * dy;

        return Math.sqrt((px - projX) ** 2 + (py - projY) ** 2);
    }

    /**
     * Select a shape (and optionally a specific point)
     */
    selectShape(type, index, pointIndex = null) {
        console.log('Selecting shape:', type, index, 'point:', pointIndex);
        this.selectedShapeType = type;
        this.selectedShapeIndex = index;

        // Show path control panel
        document.getElementById('pathControlSection').style.display = 'block';

        // Update selected shape info
        let infoText = `Selected: ${type} #${index + 1}`;
        if (pointIndex !== null && pointIndex !== undefined) {
            infoText += ` at Point ${pointIndex + 1}`;
        }
        document.getElementById('selectedShapeInfo').textContent = infoText;

        // Populate start point options for polylines
        const startPointSelect = document.getElementById('startPoint');
        startPointSelect.innerHTML = '<option value="auto">Auto</option>';

        if (type === 'polyline') {
            const poly = this.shapes.polylines[index];
            console.log('Polyline has', poly.points.length, 'points');
            
            poly.points.forEach((pt, i) => {
                const option = document.createElement('option');
                option.value = i;
                const px = typeof pt === 'object' && 'x' in pt ? pt.x : (Array.isArray(pt) ? pt[0] : 0);
                const py = typeof pt === 'object' && 'y' in pt ? pt.y : (Array.isArray(pt) ? pt[1] : 0);
                option.textContent = `Point ${i + 1} (${px.toFixed(1)}, ${py.toFixed(1)})`;
                startPointSelect.appendChild(option);
                console.log('  Added option:', option.value, option.textContent);
            });
            
            // If a specific point was clicked, snap to it (like desktop)
            if (pointIndex !== null && pointIndex !== undefined) {
                poly.start_index = pointIndex;
                startPointSelect.value = pointIndex;
                console.log('Set start_index to:', pointIndex);
            } else {
                // Restore saved settings from shape object
                if (poly.start_index !== undefined && poly.start_index !== null) {
                    startPointSelect.value = poly.start_index;
                    console.log('Restored start point:', poly.start_index);
                } else {
                    startPointSelect.value = 'auto';
                }
            }
            
            if (poly.direction !== undefined) {
                document.getElementById('direction').value = poly.direction;
            }
        }

        this.renderShapes();
    }

    /**
     * Deselect shape
     */
    deselectShape() {
        this.selectedShapeType = null;
        this.selectedShapeIndex = null;
        document.getElementById('pathControlSection').style.display = 'none';
        document.getElementById('selectedShapeInfo').textContent = 'Selected: None';
        this.renderShapes();
    }

    /**
     * Handle start point change
     */
    onStartPointChanged(value) {
        console.log('Start point changed to:', value);
        console.log('Selected shape:', this.selectedShapeType, this.selectedShapeIndex);

        if (this.selectedShapeType === 'polyline' && this.selectedShapeIndex !== null) {
            const poly = this.shapes.polylines[this.selectedShapeIndex];

            if (value === 'auto') {
                poly.start_index = null;
                console.log('Set to auto (null)');
            } else {
                const pointIndex = parseInt(value);
                if (!isNaN(pointIndex) && pointIndex >= 0 && pointIndex < poly.points.length) {
                    poly.start_index = pointIndex;
                    console.log('Saved start_index to shape:', poly.start_index);
                }
            }

            console.log('Shape now:', poly);
            this.renderShapes();
        }
    }

    /**
     * Handle direction change
     */
    onDirectionChanged(value) {
        if (this.selectedShapeType === 'polyline' && this.selectedShapeIndex !== null) {
            const poly = this.shapes.polylines[this.selectedShapeIndex];
            poly.direction = value;
            console.log('Saved direction to shape:', value);
            this.renderShapes();
        }
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        if (tabName === 'canvas') {
            document.getElementById('canvasTab').classList.add('active');
        } else if (tabName === 'gcode') {
            document.getElementById('gcodeTab').classList.add('active');
        }
    }

    /**
     * Update status bar
     */
    setStatus(message, type = 'info') {
        const statusBar = document.getElementById('statusBar');
        statusBar.textContent = message;

        // Add loading spinner if needed
        if (type === 'loading') {
            const spinner = document.createElement('span');
            spinner.className = 'loading';
            statusBar.appendChild(spinner);
        }

        // Color coding
        if (type === 'error') {
            statusBar.style.backgroundColor = '#e74c3c';
        } else if (type === 'success') {
            statusBar.style.backgroundColor = '#27ae60';
        } else {
            statusBar.style.backgroundColor = '#2c3e50';
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('===== DevFoam App Starting =====');
    try {
        window.devfoamApp = new DevFoamApp();
        console.log('===== DevFoam App Initialized Successfully =====');
        console.log('Edit mode:', window.devfoamApp.editMode);
        console.log('Canvas element:', window.devfoamApp.canvas);
    } catch (error) {
        console.error('===== FAILED TO INITIALIZE APP =====');
        console.error(error);
    }
});
