#!/usr/bin/env python3
"""Read-only checks for the Academic Drawio single-page XML contract (stdlib)."""

import argparse
from collections import Counter
from html.entities import html5
from html.parser import HTMLParser
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def _finite(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def validate_xml(data, profile="structural"):
    """Return actionable error strings; bytes honor the XML encoding declaration."""
    try:
        document = ET.fromstring(data)
    except (ET.ParseError, ValueError, LookupError) as exc:
        return [f"XML parse error: {exc}"]

    if document.tag == "mxfile":
        pages = document.findall("diagram")
        if len(pages) != 1:
            return ["mxfile: exactly one uncompressed diagram is supported"]
        models = pages[0].findall("mxGraphModel")
        if len(models) != 1:
            return ["diagram: expected one uncompressed mxGraphModel; compressed pages are unsupported"]
        model = models[0]
    elif document.tag == "mxGraphModel":
        model = document
    else:
        return ["Expected mxGraphModel or an uncompressed single-page mxfile"]

    roots = model.findall("root")
    if len(roots) != 1:
        return ["mxGraphModel: expected exactly one root"]
    root = roots[0]
    errors = []
    if any(child.tag != "mxCell" for child in root):
        errors.append("root: only direct mxCell children are supported; unwrap user objects first")
    cells = root.findall("mxCell")
    ids = [cell.get("id", "") for cell in cells]
    for cell_id, count in Counter(ids).items():
        if not cell_id.strip():
            errors.append("mxCell: missing or empty id")
        elif count > 1:
            errors.append(f"{cell_id}: duplicate id")
    by_id = {cell.get("id"): cell for cell in cells if cell.get("id")}
    for reserved in ("0", "1"):
        if reserved not in by_id:
            errors.append(f"root: missing base cell {reserved}")
    if "0" in by_id and by_id["0"].get("parent") is not None:
        errors.append("0: root cell must not have a parent")
    if "1" in by_id and by_id["1"].get("parent") != "0":
        errors.append("1: base layer must have parent 0")

    for cell in cells:
        cell_id = cell.get("id", "<missing>")
        parent = cell.get("parent")
        vertex = cell.get("vertex") == "1"
        edge = cell.get("edge") == "1"
        if cell.get("vertex") not in (None, "0", "1") or cell.get("edge") not in (None, "0", "1"):
            errors.append(f"{cell_id}: vertex and edge flags must be 0 or 1")
        if cell_id in ("0", "1") and (vertex or edge):
            errors.append(f"{cell_id}: base cells cannot be vertices or edges")
        if vertex and edge:
            errors.append(f"{cell_id}: cannot be both vertex and edge")
        if cell_id != "0":
            if parent not in by_id:
                errors.append(f"{cell_id}: missing or unknown parent {parent!r}")
            elif by_id[parent].get("edge") == "1":
                errors.append(f"{cell_id}: edge parents are unsupported by this generator")
            if (vertex or edge) and parent == "0":
                errors.append(f"{cell_id}: drawable must belong to a layer or container, not cell 0")
            if not vertex and not edge and parent != "0":
                errors.append(f"{cell_id}: non-drawable cell must be a layer under 0")

        if not (vertex or edge):
            continue
        geometries = cell.findall("mxGeometry")
        if len(geometries) != 1:
            errors.append(f"{cell_id}: expected exactly one mxGeometry")
            continue
        geometry = geometries[0]
        if geometry.get("as") != "geometry":
            errors.append(f"{cell_id}: mxGeometry must have as='geometry'")
        for coord in ("x", "y"):
            # draw.io omits zero-valued coordinates when saving a diagram.
            if not _finite(geometry.get(coord, "0")):
                errors.append(f"{cell_id}: {coord} must be a finite number")
        if vertex:
            for dimension in ("width", "height"):
                value = geometry.get(dimension)
                if not _finite(value) or float(value) <= 0:
                    errors.append(f"{cell_id}: {dimension} must be a finite positive number")
        if edge:
            if geometry.get("relative") != "1":
                errors.append(f"{cell_id}: edge geometry must have relative='1'")
            for terminal in ("source", "target"):
                ref = cell.get(terminal)
                if ref not in by_id:
                    errors.append(f"{cell_id}: missing or unknown {terminal} {ref!r}")
                elif by_id[ref].get("vertex") != "1":
                    errors.append(f"{cell_id}: {terminal} {ref!r} must reference a vertex")
        for point in geometry.iter("mxPoint"):
            for coord in ("x", "y"):
                if not _finite(point.get(coord, "0")):
                    errors.append(f"{cell_id}: waypoint {coord} must be a finite number")

    # Iterative ancestry traversal avoids recursion limits on damaged files.
    done = set()
    for start in by_id:
        chain = []
        positions = {}
        current = start
        while current in by_id and current not in done:
            if current in positions:
                cycle = chain[positions[current]:] + [current]
                errors.append("Parent cycle: " + " -> ".join(cycle))
                break
            positions[current] = len(chain)
            chain.append(current)
            current = by_id[current].get("parent")
        done.update(chain)

    for dimension in ("pageWidth", "pageHeight", "pageScale"):
        value = model.get(dimension)
        if value is not None and (not _finite(value) or float(value) <= 0):
            errors.append(f"mxGraphModel: {dimension} must be a finite positive number")
    if profile == "academic" and not errors:
        errors.extend(_academic_errors(document, model, by_id))
    elif profile not in ("structural", "academic"):
        errors.append(f"Unknown validation profile: {profile}")
    return errors


def _style(cell):
    return dict(token.split("=", 1) for token in cell.get("style", "").split(";") if "=" in token)


class _LabelHTML(HTMLParser):
    """Validate the small editable HTML subset this skill deliberately emits."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in {"b", "strong", "i", "em", "span", "div", "p", "sub", "sup", "br"}:
            self.errors.append(f"unsupported HTML tag {tag}")
        if tag != "br":
            self.stack.append(tag)
        for key, value in attrs:
            if key == "style" and value:
                if re.search(r"font-weight\s*:\s*(?:normal|[1-6]00)\b", value, re.I):
                    self.errors.append("HTML must not override bold text")
                if re.search(r"text-align\s*:\s*(?:left|right|justify)\b", value, re.I):
                    self.errors.append("HTML must preserve centered text")

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced HTML closing tag {tag}")
        else:
            self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag != "br":
            self.handle_endtag(tag)

    def handle_entityref(self, name):
        if name + ";" not in html5:
            self.errors.append(f"unknown HTML entity &{name};")


def _academic_errors(document, model, by_id):
    errors = []
    if document.tag != "mxfile":
        errors.append("academic: complete mxfile with a meaningful diagram name is required")
    else:
        page = document.find("diagram")
        name = page.get("name", "").strip()
        if not name or re.fullmatch(r"(?:page[- ]?\d*|untitled|未命名|页面[- ]?\d*)", name, re.I):
            errors.append("diagram: meaningful name required (not Page-1/Untitled)")
        if not page.get("id", "").strip():
            errors.append("diagram: nonempty id required")
    width = float(model.get("pageWidth", "0"))
    height = float(model.get("pageHeight", "0"))
    if (width, height) not in ((827, 1169), (1169, 827)):
        errors.append("academic: page must be A4 (827x1169 or 1169x827)")
    for key, value in {"page":"1", "pageScale":"1", "grid":"1", "gridSize":"10", "math":"0"}.items():
        if model.get(key) != value:
            errors.append(f"academic: {key}={value} required")

    boxes = {}
    for ident, cell in by_id.items():
        if cell.get("vertex") != "1" and cell.get("edge") != "1":
            continue
        style = _style(cell)
        if not re.search(r"[^\W\d_]", ident, re.UNICODE):
            errors.append(f"{ident}: use a functional, nonnumeric id")
        label = cell.get("value", "")
        required = {"strokeWidth":"3", "jumpStyle":"arc", "jumpSize":"5"}
        if label:
            required.update({"fontStyle":"1", "html":"1", "align":"center", "verticalAlign":"middle"})
            if not _finite(style.get("fontSize")) or float(style["fontSize"]) < 14:
                errors.append(f"{ident}: set a readable explicit fontSize (at least 14 editor units)")
            if re.search(r"\\(?:frac|sqrt|begin|end|[\[\]()])|\$[^$]+\$", label):
                errors.append(f"{ident}: use HTML sup/sub instead of LaTeX")
            if "⊙" in label:
                errors.append(f"{ident}: write HTML &odot; (XML &amp;odot;) for the dot product")
            parser = _LabelHTML()
            parser.feed(label)
            parser.close()
            if parser.stack:
                parser.errors.append("unclosed HTML tags: " + ", ".join(parser.stack))
            errors.extend(f"{ident}: {problem}" for problem in parser.errors)
        if cell.get("edge") == "1":
            required.update({"rounded":"1", "endArrow":"classic"})
            if style.get("startArrow", "none") != "none":
                errors.append(f"{ident}: use two independent edges for a bidirectional relationship")
            for key in ("entryX","entryY","entryDx","entryDy","exitX","exitY","exitDx","exitDy","sourcePort","targetPort"):
                if key in style:
                    errors.append(f"{ident}: remove {key}; use floating connections and waypoints")
            if style.get("portConstraint") == "fixed":
                errors.append(f"{ident}: fixed portConstraint is not a floating connection")
            if not all(cell.get(key) in ident for key in ("source", "target")):
                errors.append(f"{ident}: edge id should contain its source and target ids")
        for wrong in ("jumpstyle", "jumpsize"):
            if wrong in style:
                errors.append(f"{ident}: wrong-case {wrong}; use jumpStyle/jumpSize")
        for key, value in required.items():
            actual = style.get(key)
            matches = actual == value
            if key in ("strokeWidth", "jumpSize") and _finite(actual):
                matches = math.isclose(float(actual), float(value))
            if not matches:
                errors.append(f"{ident}: {key}={value} required")
        if cell.get("vertex") == "1":
            geom = cell.find("mxGeometry")
            x,y,w,h = [float(geom.get(k,"0")) for k in ("x","y","width","height")]
            parent = by_id[cell.get("parent")]
            pg = parent.find("mxGeometry")
            pw,ph = (float(pg.get("width")),float(pg.get("height"))) if pg is not None else (width,height)
            if x < 0 or y < 0 or x+w > pw or y+h > ph:
                errors.append(f"{ident}: geometry exceeds its parent/page bounds")
            pstyle = _style(parent)
            if "swimlane" in parent.get("style", "") and _finite(pstyle.get("startSize")):
                if y < float(pstyle["startSize"]):
                    errors.append(f"{ident}: overlaps its container title band")
            boxes[ident] = (cell.get("parent"), x,y,w,h)
    # Only same-parent vertex rectangles; parent-child containment is intentional.
    entries = list(boxes.items())
    for i, (a, (pa,ax,ay,aw,ah)) in enumerate(entries):
        for b, (pb,bx,by,bw,bh) in entries[i+1:]:
            if pa == pb and min(ax+aw,bx+bw)>max(ax,bx) and min(ay+ah,by+bh)>max(ay,by):
                errors.append(f"{a}/{b}: overlapping sibling geometry; review layout")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml_file", type=Path)
    parser.add_argument("--profile", choices=("structural", "academic"), default="structural")
    args = parser.parse_args(argv)
    try:
        data = args.xml_file.read_bytes()
    except OSError as exc:
        print(f"Cannot read XML: {exc}", file=sys.stderr)
        return 2
    errors = validate_xml(data, args.profile)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.profile} checks passed (rendered layout and research meaning not verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

