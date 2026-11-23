from pathlib import Path
import subprocess
import tempfile
import unittest


class InstalledPackageTests(unittest.TestCase):
    def test_installed_command_and_skills_in_an_empty_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            skills = Path(subprocess.check_output(
                ["graphic-design", "skills-path"], cwd=project, text=True
            ).strip())
            self.assertEqual(
                {file.parent.name for file in skills.glob("*/SKILL.md")},
                {"setup-design-studio", "design-direction", "plan-design-stages",
                 "design-in-layers", "design-proof-review", "design-effects-and-sound"},
            )
            self.assertTrue((skills / "setup-design-studio/references/commands.md").is_file())
            self.assertTrue((skills / "design-proof-review/scripts/detail_review.py").is_file())
            self.assertTrue((skills / "design-proof-review/scripts/check_edit_scope.py").is_file())
            subprocess.run(["graphic-design", "init", "--intent", "Friday tournament", "poster", "results"],
                           cwd=project, check=True)
            board = subprocess.check_output(["graphic-design", "status"], cwd=project, text=True)
            self.assertIn("graphics/poster/plan.md", board)
            self.assertIn("graphics/results/plan.md", board)
            self.assertIn("Friday tournament", (project / ".graphic-design/collection-plan.md").read_text())


if __name__ == "__main__":
    unittest.main()
