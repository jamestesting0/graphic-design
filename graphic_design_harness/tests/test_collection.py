import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SKILL = Path(__file__).resolve().parents[1] / ".agents/skills/setup-design-studio"


class StudioFlowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.cli = shutil.copytree(SKILL, self.root / "installed") / "scripts/studio.py"
        self.project = self.root / "commission"
        self.project.mkdir()
        self.call("init", "--intent", "Tournament kit", "banner", "bracket", "matchup")
        self.bundle = self.root / "bundle"
        (self.bundle / "art").mkdir(parents=True)
        (self.bundle / "art/mark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        shutil.copyfile(self.bundle / "art/mark.svg", self.studio / "library/mark.svg")
        (self.bundle / "master.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="art/mark.svg"/></svg>')
        Image.new("RGB", (128, 96), "navy").save(self.bundle / "proof.png")

    @property
    def studio(self):
        return self.project / ".graphic-design"

    def call(self, *args, fails=False):
        run = subprocess.run([sys.executable, "-B", self.cli, *args], cwd=self.project,
                             text=True, capture_output=True)
        if fails:
            self.assertNotEqual(run.returncode, 0)
        else:
            self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout + run.stderr

    def save(self, graphic, key, *extra, bundle=None, fails=False):
        return self.call("save", graphic, key, "--study", "layout", "--bundle", bundle or self.bundle,
                         "--master", "master.svg", "--preview", "proof.png", "--proof", "proof.png",
                         "--shared", "mark.svg=art/mark.svg", "--note", key, *extra, fails=fails)

    def approve(self, graphic, key, use="main"):
        proof = self.studio / "graphics" / graphic / "versions" / key / "bundle/proof.png"
        review = self.root / "review.json"
        review.write_text(json.dumps({"graphic": graphic, "version": key, "proof_sha256": hashlib.sha256(proof.read_bytes()).hexdigest(),
                                      "reviewer": "fixture", "verdict": "advance", "finding": "Blue sample fills the frame."}))
        self.call("approve", graphic, key, "--use", use, "--review", review, "--by", "fixture")

    def test_resume_move_pin_restore_and_merge_across_sessions(self):
        brief = self.studio / "graphics/bracket/brief.md"
        brief.write_text("Client requires eight entrants.")
        register = self.studio / "library/assets.md"
        self.assertTrue(register.is_file())
        register.write_text("supplied/club.svg — exact club mark for the bracket")
        self.call("init", "--intent", "other", "bracket")
        self.call("add", "icon")
        self.assertEqual(brief.read_text(), "Client requires eight entrants.")
        self.assertIn("exact club mark", register.read_text())
        self.assertIn("Tournament kit", (self.studio / "collection-plan.md").read_text())
        for key in "ABCDEF":
            self.save("bracket", key)
        self.call("keep", "bracket", "A")
        gallery = self.studio / "graphics/bracket/studies/layout/gallery.md"
        recent, older = gallery.read_text().split("## Earlier favorites")
        self.assertNotIn("**A", recent)
        self.assertIn("**A (pinned)", older)
        self.approve("bracket", "B")
        self.approve("bracket", "F")
        self.project = self.project.rename(self.root / "moved")
        edited = self.root / "recovered"
        self.call("restore", "bracket", "A", "--to", edited, "--next", "Widen gutters")
        self.assertEqual((edited / "art/mark.svg").read_bytes(), (self.bundle / "art/mark.svg").read_bytes())
        self.save("bracket", "G", bundle=edited)
        history = self.studio / "graphics/bracket/versions"
        self.assertEqual(json.loads((history / "G/version.json").read_text())["parents"], ["A"])
        self.save("bracket", "H", "--parent", "G", "--parent", "F")
        self.assertEqual(json.loads((history / "H/version.json").read_text())["parents"], ["G", "F"])
        self.assertIn("**B (pinned)", (self.studio / "graphics/bracket/studies/layout/gallery.md").read_text())
        main = json.loads((self.studio / "graphics/bracket/state.json").read_text())["uses"]["main"]
        self.assertEqual([a["version"] for a in main["earlier_approvals"]], ["B"])
        board = self.call("status")
        self.assertIn("(library/assets.md)", board)
        self.assertIn("[A](graphics/bracket", board)
        self.assertIn("[F](graphics/bracket", board)
        self.assertIn("Widen gutters", board)
        self.assertIn("icon/plan.md", board)

    def test_release_retry_does_not_change_last_delivery_or_active_approvals(self):
        for key, use in [("VS", "main"), ("Result", "result")]:
            self.save("matchup", key)
            self.approve("matchup", key, use)
        sheet = self.root / "sheet.png"
        self.call("sheet", "matchup/main", "matchup/result", "--out", sheet)
        picks = ["--reviewed-sheet", sheet, "matchup/main", "matchup/result"]
        self.call("release", "first", *picks)
        output = self.project / "deliverables"
        original = (output / "first/manifest.json").read_bytes()
        items = json.loads(original)["items"]
        self.assertEqual({use: row["version"] for use, row in items.items()},
                         {"matchup/main": "VS", "matchup/result": "Result"})
        self.assertEqual(items["matchup/result"]["approval"]["selected_by"], "fixture")
        damaged = self.studio / "graphics/matchup/versions/Result/bundle/art/mark.svg"
        damaged.unlink()
        self.call("release", "second", *picks, fails=True)
        self.call("restore", "matchup", "Result", "--to", self.root / "bad", "--next", "revise", fails=True)
        self.assertFalse((self.root / "bad").exists())
        self.assertFalse((output / "second").exists())
        self.assertEqual((output / "first/manifest.json").read_bytes(), original)
        shutil.copyfile(self.bundle / "art/mark.svg", damaged)
        self.call("release", "second", "--reviewed-sheet", sheet, "matchup/main", fails=True)
        self.call("release", "second", *picks)
        self.call("release", "second", *picks, fails=True)
        self.assertTrue((output / "second/contact-sheet.png").is_file())
        self.assertEqual((output / "second/matchup/result/art/mark.svg").read_bytes(), damaged.read_bytes())

    def test_failed_snapshot_stale_approval_and_shared_asset_impact(self):
        self.save("banner", "A")
        self.approve("banner", "A")
        self.save("bracket", "B")
        self.call("select", "bracket", "B", "--next", "Compare")
        consumers = self.call("consumers", "mark.svg")
        self.assertIn("banner main approved A", consumers)
        self.assertIn("bracket main working B", consumers)
        self.assertNotIn("matchup", consumers)
        self.call("approve", "banner", "A", "--by", " ", "--review", self.root / "review.json", fails=True)
        self.call("approve", "bracket", "B", "--by", "fixture", "--review", self.root / "review.json", fails=True)
        (self.studio / "library/mark.svg").write_text("changed library")
        (self.bundle / "art/mark.svg").write_text("unreviewed third copy")
        self.save("bracket", "C", fails=True)
        self.assertFalse((self.studio / "graphics/bracket/versions/C").exists())
        restored = self.root / "old"
        self.call("restore", "banner", "A", "--to", restored, "--next", "check original")
        old_mark = (restored / "art/mark.svg").read_bytes()
        self.assertNotEqual(old_mark, (self.studio / "library/mark.svg").read_bytes())
        self.call("save", "banner", "A2", "--study", "detail", "--bundle", restored,
                  "--master", "master.svg", "--proof", "proof.png", "--preview", "proof.png",
                  "--note", "New lettering, selected mark preserved")
        child = json.loads((self.studio / "graphics/banner/versions/A2/version.json").read_text())
        self.assertEqual(child["shared"]["mark.svg"]["sha256"], hashlib.sha256(old_mark).hexdigest())
