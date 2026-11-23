# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=10"]
# ///
import argparse
from pathlib import Path

from PIL import Image, ImageChops


def main():
    parser = argparse.ArgumentParser(description="Check locked pixels in registered 8-bit PNG proofs.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--allow", nargs=4, type=int, action="append", default=[],
                        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
                        help="Permitted edit bounds in native pixels, right/bottom exclusive. Repeat for separate regions.")
    args = parser.parse_args()

    for path in (args.baseline, args.candidate):
        with path.open("rb") as source:
            header = source.read(25)
        if header[12:16] != b"IHDR" or header[24:25] != b"\x08":
            parser.error("Use PNG exports with 8-bit samples. Re-export both at matching settings.")

    with Image.open(args.baseline) as baseline, Image.open(args.candidate) as candidate:
        for proof in (baseline, candidate):
            if (proof.format != "PNG" or proof.n_frames != 1
                    or proof.mode not in {"L", "LA", "P", "RGB", "RGBA"}):
                parser.error("Use registered single-frame PNG exports in comparable 8-bit color.")
        if baseline.size != candidate.size:
            parser.error("Proof dimensions differ. Re-export at matching registration.")
        width, height = baseline.size
        difference = ImageChops.difference(baseline.convert("RGBA"), candidate.convert("RGBA"))

    for left, top, right, bottom in args.allow:
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            parser.error("Allowed bounds must be nonempty and inside the proof.")
        difference.paste((0, 0, 0, 0), (left, top, right, bottom))
    changed = difference.getbbox(alpha_only=False)
    if changed:
        parser.exit(1, f"Locked pixels changed within {changed} (right and bottom exclusive).\n")
    print("Locked RGBA pixels match. Inspect the allowed regions visually.")


if __name__ == "__main__":
    main()
