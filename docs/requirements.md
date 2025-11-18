# G-CODE GENERATOR REQUIREMENTS & INSTRUCTIONS

## 1. Overview

This document defines the requirements, workflow, and rules for a G-code generator that produces toolpaths for cutting text-based shapes (e.g., foam letters). The generator converts font outlines into machining instructions with proper offsets, cutting order, linking moves, and G-code emission.

## 2. Functional Requirements

### 2.1 Input Requirements

- Accept a text string.
- Accept font name, size, and layout (left-to-right baseline).
- Accept machining parameters:
  * Tool radius
  * Cutting depth (Z)
  * Safe travel height
  * Feed rates (cutting, plunge)
  * Curve tolerance for polygonization

### 2.2 Output Requirements

- Generate clean, valid G-code (ISO-style).
- Output outer and inner contours in correct cutting order.
- Include lead-in/lead-out moves.
- Include rapid linking moves between contours.
- Support linear segments; arcs optional.

## 3. Processing Pipeline

### 3.1 Font Geometry Import

- Extract glyph contours from a TrueType or OpenType font.
- Convert Bezier curves into internal contour objects.

### 3.2 Curve Polygonization

- Approximate curves with straight-line segments.
- Use recursive subdivision until deviation < tolerance.

### 3.3 Tool-Offsetting

- Determine contour orientation (outer vs hole).
- Offset by tool radius:
  * Outer contours offset outward.
  * Inner holes offset inward.
- Ensure no self-intersections are produced.

### 3.4 Contour Ordering

- Cut inner holes before outer boundaries.
- Order letters left-to-right.
- Optional: optimize via nearest-neighbor travel.

### 3.5 Path Planning

- Choose start point on each contour.
- Maintain consistent direction (CCW outer, CW inner).
- Add lead-in/lead-out segments.
- Add rapid linking moves between contours.

## 4. G-code Generation Rules

### 4.1 Header

- G21 (mm)
- G90 (absolute mode)
- G17 (XY plane)
- Spindle/hotwire ON if applicable

### 4.2 Contour Cutting

- G0 to safe Z.
- G0 to start point.
- G1 plunge to cutting depth.
- G1 along contour points at cutting feed.

### 4.3 Linking Moves

- Retract to safe Z.
- G0 to next contour start.

### 4.4 Footer

- Retract to safe Z.
- Spindle OFF.
- Return to origin.
- M30 program end.

## 5. Error Handling

- Reject overlapping contours after offsetting.
- Report when offsetting collapses a contour.
- Reject fonts with malformed Bezier outlines.

## 6. Summary

A correct G-code generator implements:
- Accurate vector-to-toolpath conversion.
- Reliable tool-radius compensation.
- Safe and ordered machining logic.
- Clean and readable G-code output.
