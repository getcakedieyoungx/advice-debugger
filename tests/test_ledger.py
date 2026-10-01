"""End-to-end tests for skills/advice-debugger/scripts/ledger.py.

Run: python -m unittest discover -s tests -v
Each test gets its own temporary ledger via ADVICE_LEDGER_DIR.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "skills" / "advice-debugger" / "scripts" / "ledger.py"
TODAY = "2026-10-01"

ADD_DAILY = {
    "domain": "Content",
    "tags": ["x", "posting-routine"],
    "advice": "Post once every day",
    "assumptions": [
        {"text": "The bottleneck is writing; picking topics is easy", "critical": True},
        {"text": "They can spare 20 minutes a day"},
    ],
    "expected": {"change": "consistent posting", "signal": ">=5 posts in 7 days"},
    "check_on": "2026-09-30",
}
RESULT_ABANDONED = {
    "status": "abandoned",
    "actual": "Posted for 3 days, then stopped. Choosing a topic every day was exhausting.",
    "verdicts": {"A1": {"verdict": "broke", "note": "daily topic decision"}, "A2": "held"},
    "lesson": "A routine needing a fresh decision every day stalled on day 3.",
}


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.env = dict(os.environ, ADVICE_LEDGER_DIR=str(self.dir / "ledger"),
                        ADVICE_LEDGER_TODAY=TODAY, PYTHONIOENCODING="utf-8")
        self.env.pop("ADVICE_DEBUGGER_NO_HOOK", None)
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args, payload=None, ok=True):
        argv = [sys.executable, str(LEDGER), *args]
        if payload is not None:
            self.n += 1
            f = self.dir / f"in{self.n}.json"
            f.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            argv += ["--file", str(f)]
        p = subprocess.run(argv, env=self.env, capture_output=True, text=True, encoding="utf-8")
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout)
        return p

    def data(self):
        return json.loads((self.dir / "ledger" / "ledger.json").read_text(encoding="utf-8"))

    # --- happy path ---

    def test_full_loop(self):
        self.assertIn("#1 recorded", self.run_cmd("add", payload=ADD_DAILY).stdout)
        self.assertIn("#1", self.run_cmd("due").stdout)
        self.run_cmd("result", "1", payload=RESULT_ABANDONED)
        fix = dict(ADD_DAILY, advice="Pick topics weekly, draft three posts at once",
                   assumptions=[{"text": "Batching removes daily decision load", "critical": True}],
                   check_on="2026-10-08", revises=1)
        self.run_cmd("add", payload=fix)
        e1, e2 = self.data()["entries"]
        self.assertEqual(e1["status"], "abandoned")
        self.assertEqual(e1["assumptions"][0]["verdict"], "broke")
        self.assertEqual(e2["revises"], 1)
        lessons = self.run_cmd("lessons", "--domain", "content").stdout
        self.assertIn("broke: The bottleneck is writing", lessons)
        self.assertIn("revised by: #2", self.run_cmd("show", "1").stdout)
        self.assertTrue((self.dir / "ledger" / "ledger.md").exists())
        self.assertTrue((self.dir / "ledger" / "ledger.json.bak").exists())

    def test_skill_md_examples_are_valid(self):
        """The JSON examples in SKILL.md must be accepted by the script."""
        text = (ROOT / "skills" / "advice-debugger" / "SKILL.md").read_text(encoding="utf-8")
        blocks = [b.split("```", 1)[0] for b in text.split("```json\n")[1:]]
        self.assertEqual(len(blocks), 2)
        self.run_cmd("add", payload=json.loads(blocks[0]))
        self.run_cmd("result", "1", payload=json.loads(blocks[1]))

    # --- hook ---

    def test_hook_silent_without_ledger(self):
        p = self.run_cmd("due", "--hook")
        self.assertEqual(p.stdout, "")
        self.assertFalse((self.dir / "ledger").exists(), "hook must not create the ledger dir")

    def test_hook_reminds_oldest_due(self):
        self.run_cmd("add", payload=ADD_DAILY)
        self.run_cmd("add", payload=dict(ADD_DAILY, advice="Second", check_on="2026-09-29"))
        out = self.run_cmd("due", "--hook").stdout
        self.assertIn("#2", out)
        self.assertIn("1 more due", out)

    def test_hook_silent_when_nothing_due_or_disabled(self):
        self.run_cmd("add", payload=dict(ADD_DAILY, check_on="2026-12-01"))
        self.assertEqual(self.run_cmd("due", "--hook").stdout, "")
        self.run_cmd("add", payload=ADD_DAILY)
        self.env["ADVICE_DEBUGGER_NO_HOOK"] = "1"
        self.assertEqual(self.run_cmd("due", "--hook").stdout, "")

    def test_hook_survives_corrupt_ledger(self):
        (self.dir / "ledger").mkdir()
        (self.dir / "ledger" / "ledger.json").write_text("{bad", encoding="utf-8")
        self.assertEqual(self.run_cmd("due", "--hook").stdout, "")

    # --- search and labels ---

    def test_search_is_accent_and_case_insensitive(self):
        self.run_cmd("add", payload=dict(ADD_DAILY, domain="İçerik", advice="Günlük paylaşım yap"))
        self.assertEqual(self.data()["entries"][0]["domain"], "içerik")
        self.assertIn("#1", self.run_cmd("search", "--domain", "ICERIK").stdout)
        self.assertIn("(1/2 terms)", self.run_cmd("search", "gunluk", "tweet").stdout)

    def test_english_labels_untouched(self):
        self.run_cmd("add", payload=dict(ADD_DAILY, domain="Image UI"))
        self.assertEqual(self.data()["entries"][0]["domain"], "image ui")

    def test_string_inputs_coerced(self):
        self.run_cmd("add", payload=dict(ADD_DAILY, tags="a, b", assumptions=[
            {"text": "x", "critical": "false"}, {"text": "y", "critical": "true"}]))
        e = self.data()["entries"][0]
        self.assertEqual(e["tags"], ["a", "b"])
        self.assertEqual([a["critical"] for a in e["assumptions"]], [False, True])

    # --- guards ---

    def test_validation_errors(self):
        self.run_cmd("add", payload=dict(ADD_DAILY, assumptions=["no critical"]), ok=False)
        p = self.run_cmd("add", payload=dict(ADD_DAILY, expected={"change": "x"}), ok=False)
        self.assertIn("expected.signal", p.stderr)
        self.run_cmd("add", payload=dict(ADD_DAILY, check_on="next week"), ok=False)
        self.run_cmd("add", payload=dict(ADD_DAILY, revises=99), ok=False)
        self.run_cmd("search", ok=False)
        self.run_cmd("show", "1", ok=False)

    def test_result_guards(self):
        self.run_cmd("add", payload=ADD_DAILY)
        self.run_cmd("result", "1", payload=dict(RESULT_ABANDONED, lesson=""), ok=False)
        self.run_cmd("result", "1", payload=dict(RESULT_ABANDONED, verdicts=["A1"]), ok=False)
        self.run_cmd("result", "1", payload=dict(RESULT_ABANDONED, verdicts={"A9": "held"}), ok=False)
        self.run_cmd("result", "1", payload=RESULT_ABANDONED)
        p = self.run_cmd("result", "1", payload=dict(RESULT_ABANDONED, status="worked"), ok=False)
        self.assertIn("already closed", p.stderr)
        self.assertEqual(self.data()["entries"][0]["status"], "abandoned")
        self.run_cmd("result", "1", "--force", payload=dict(RESULT_ABANDONED, status="worked"))

    def test_postpone_and_delete(self):
        self.run_cmd("add", payload=ADD_DAILY)
        self.run_cmd("postpone", "1", "--to", "2020-01-01", ok=False)
        self.run_cmd("postpone", "1", "--to", "2026-10-10")
        self.assertIn("Nothing is due", self.run_cmd("due").stdout)
        self.run_cmd("add", payload=dict(ADD_DAILY, revises=1))
        self.run_cmd("delete", "1", ok=False)
        self.run_cmd("delete", "1", "--force")
        self.assertIsNone(self.data()["entries"][0]["revises"])

    def test_corrupt_ledger_is_not_overwritten(self):
        (self.dir / "ledger").mkdir()
        f = self.dir / "ledger" / "ledger.json"
        f.write_text("{bad", encoding="utf-8")
        p = self.run_cmd("add", payload=ADD_DAILY, ok=False)
        self.assertIn("corrupt", p.stderr)
        self.assertEqual(f.read_text(encoding="utf-8"), "{bad")


if __name__ == "__main__":
    unittest.main()
