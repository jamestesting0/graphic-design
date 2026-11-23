import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from PIL import Image


SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/design-proof-review/scripts"


def rgb16_pixel(red):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", 1, 1, 16, 2, 0, 0, 0)
    scanline = b"\0" + struct.pack(">HHH", red, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(scanline)) + chunk(b"IEND", b""))


class ProofReviewTests(unittest.TestCase):
    def test_sub_byte_difference_in_high_depth_png_cannot_be_certified_as_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline, candidate = (Path(tmp) / name for name in ("a.png", "b.png"))
            baseline.write_bytes(rgb16_pixel(256))
            candidate.write_bytes(rgb16_pixel(257))
            run = subprocess.run([sys.executable, SCRIPTS / "check_edit_scope.py", baseline, candidate],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2, run.stdout)
            self.assertIn("8-bit", run.stderr)

    def test_coverage_requires_an_identifiable_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            art = folder / "proof.png"
            Image.new("RGB", (8, 8)).save(art)
            command = [sys.executable, SCRIPTS / "detail_review.py", art]
            subprocess.run([*command, "--tiles", folder], check=True)
            digest = json.loads((folder / "manifest.json").read_text())["sha256"]
            record = {"sha256": digest, "reviewer": [None], "observations": {"r1c1": "Black field."},
                      "zoom_checks": [{"box": [0, 0, 8, 8], "scale": 2, "finding": "Uniform edges."}]}
            path = folder / "review.json"
            path.write_text(json.dumps(record))
            run = subprocess.run([*command, "--record", path], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stdout)
            self.assertIn("reviewer", run.stderr)
