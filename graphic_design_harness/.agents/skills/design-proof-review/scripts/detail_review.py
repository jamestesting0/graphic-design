import argparse
import hashlib
import json
from math import ceil, isfinite
from pathlib import Path

from PIL import Image


def starts(length):
    if length <= 864:
        return [0]
    steps = ceil((length - 864) / 800)
    return [round(i * (length - 864) / steps) for i in range(steps + 1)]


def regions(width, height):
    return {f"r{r}c{c}": (x, y, min(x + 864, width), min(y + 864, height))
            for r, y in enumerate(starts(height), 1)
            for c, x in enumerate(starts(width), 1)}


def coverage_error(record, digest, boxes, size):
    if not isinstance(record, dict):
        return "The review record must be a JSON object."
    if record.get("sha256") != digest:
        return "Review belongs to a different render."
    if not isinstance(record.get("reviewer"), str) or not record["reviewer"].strip():
        return "Identify the reviewer."
    notes = record.get("observations")
    if not isinstance(notes, dict) or set(notes) != set(boxes):
        return "Record a native-size observation for every region."
    if any(not isinstance(note, str) or not note.strip() for note in notes.values()):
        return "An observation is empty."
    zooms = record.get("zoom_checks")
    if not isinstance(zooms, list) or not zooms:
        return "Record the enlarged detail checks."
    for zoom in zooms:
        if not isinstance(zoom, dict):
            return "Invalid zoom check."
        box = zoom.get("box")
        if not isinstance(box, list) or len(box) != 4 or not all(type(n) is int for n in box):
            return "Record native pixel bounds for the enlarged view."
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1]):
            return "Zoom bounds are outside the render."
        scale = zoom.get("scale")
        if not isinstance(scale, (float, int)) or not isfinite(scale) or scale < 2:
            return "Record a finite magnification of 2× or greater."
        if not isinstance(zoom.get("finding"), str) or not zoom["finding"].strip():
            return "Record a finding at 2× or greater."
    return None


def main():
    parser = argparse.ArgumentParser(description="Prepare native-size tiles or check a reviewer's coverage record.")
    parser.add_argument("art", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tiles", type=Path)
    mode.add_argument("--record", type=Path)
    args = parser.parse_args()
    digest = hashlib.sha256(args.art.read_bytes()).hexdigest()
    with Image.open(args.art) as image:
        boxes = regions(*image.size)
        if args.tiles:
            args.tiles.mkdir(parents=True, exist_ok=True)
            for name, box in boxes.items():
                image.crop(box).save(args.tiles / f"{name}.png")
            manifest = {"sha256": digest, "size": image.size, "regions": boxes}
            (args.tiles / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        else:
            error = coverage_error(json.loads(args.record.read_text()), digest, boxes, image.size)
            if error:
                parser.exit(1, error + "\n")
            print("Review record covers this render. Read the findings for the design verdict.")


if __name__ == "__main__":
    main()
