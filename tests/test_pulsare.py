import os
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "pulsare"
pulsare = SourceFileLoader("pulsare", str(P)).load_module()


class InboxTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        (self.cwd / "SCORE.md").write_text("# SCORE\n")
        (self.cwd / "BRIEF.md").write_text("# BRIEF\n")
        self.root = pulsare.init(self.cwd, "testholon")
        os.environ["PULSARE_ROLE"] = "grok"
        os.environ["PULSARE_SESSION"] = "testholon"
        os.environ["PULSARE_ROOT"] = str(self.root)

    def tearDown(self) -> None:
        os.environ.pop("PULSARE_ROLE", None)
        os.environ.pop("PULSARE_SESSION", None)
        os.environ.pop("PULSARE_ROOT", None)
        self.tmp.cleanup()

    def test_write_inbox_has_no_seq(self) -> None:
        box, text, rels = pulsare.write_inbox(self.root, "grok", "scored", ["SCORE.md"])
        self.assertEqual(box.name, "to-claude")
        self.assertEqual(rels, ["SCORE.md"])
        self.assertNotIn("seq=", text)
        self.assertIn("kind=scored", text)
        self.assertTrue(box.is_file())
        rec = pulsare.last(self.root)
        self.assertEqual(rec["from"], "grok")
        self.assertEqual(rec["to"], "claude")
        self.assertNotIn("seq", rec)

    def test_claude_writes_to_grok(self) -> None:
        box, text, _ = pulsare.write_inbox(self.root, "claude", "briefed", ["BRIEF.md"])
        self.assertEqual(box.name, "to-grok")
        self.assertIn("kind=briefed", text)

    def test_overwrite_last_wins(self) -> None:
        pulsare.write_inbox(self.root, "grok", "scored", ["SCORE.md"])
        pulsare.write_inbox(self.root, "grok", "scored", ["SCORE.md"])
        self.assertEqual(pulsare.inbox(self.root, "claude").read_text().count("PULSARE INGEST"), 1)

    def test_busy_chrome_is_footer_only(self) -> None:
        history = (
            "esc to interrupt\n"
            + ("work line\n" * 20)
            + "Churned for 9s · done 11:32 PM\n"
            "❯ \n"
            "── footer ──\n"
            "auto mode on (shift+tab to cycle)\n"
        )
        self.assertIsNone(pulsare.chrome_in_footer(history))
        live = history.replace("auto mode on (shift+tab to cycle)", "esc to interrupt")
        self.assertEqual(pulsare.chrome_in_footer(live), "esc to interrupt")

    def test_knock_without_inbox_errors(self) -> None:
        with self.assertRaises(pulsare.Error) as ctx:
            pulsare.pulsare_knock()
        self.assertIn("no inbox", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
