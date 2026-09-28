import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "harness/knowledge.py"
SPEC = importlib.util.spec_from_file_location("knowledge_under_test", SCRIPT)
KNOWLEDGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KNOWLEDGE)


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "work"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        (self.root / "docs/lesson.md").write_text("verified result\n", encoding="utf-8")

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.root), *args],
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stderr

    def proposal(self, *, slug="art/alpha", content="Keep silhouettes readable.",
                 evidence=None, **changes):
        raw = {"slug": slug, "title": "Readable silhouettes", "when_to_use": "When reviewing art",
               "content": content, "kind": "procedure", "reason": "Found in project review",
               "evidence": evidence if evidence is not None else ["docs/lesson.md"]}
        raw.update(changes)
        source = self.root / "draft.json"
        source.write_text(json.dumps(raw), encoding="utf-8")
        return source

    def test_init_propose_accept_context_and_history(self):
        self.assertEqual(self.run_cli("init")["status"], "initialized")
        candidate = self.run_cli("propose", str(self.proposal()))
        identifier = candidate["id"]
        self.assertEqual(candidate["expected_version"], 0)
        self.assertEqual(self.run_cli("context")["index"], [])
        saved = json.loads((self.root / "refinements/candidates" / (identifier + ".json")).read_text())
        self.assertEqual(saved["proposal"]["evidence"][0]["sha256"],
                         hashlib.sha256((self.root / "docs/lesson.md").read_bytes()).hexdigest())
        accepted = self.run_cli("accept", identifier)
        self.assertEqual(accepted["version"], 1)
        index_only = self.run_cli("context")
        self.assertEqual(index_only["index"][0]["slug"], "art/alpha")
        self.assertNotIn("selected", index_only)
        self.assertNotIn("Keep silhouettes", json.dumps(index_only))
        selected = self.run_cli("context", "--slug", "art/alpha")
        self.assertEqual(selected["selected"][0]["content"], "Keep silhouettes readable.")
        self.assertTrue((self.root / "refinements/accepted" / (identifier + ".json")).is_file())
        self.assertEqual((self.root / "knowledge/art/alpha.md").read_text(), "Keep silhouettes readable.")

    def test_context_defaults_to_current_working_directory(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", identifier)
        result = subprocess.run([sys.executable, str(SCRIPT), "context"], cwd=self.root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["index"][0]["slug"], "art/alpha")

    def test_update_and_rollback_latest_only(self):
        first = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", first)
        second = self.run_cli("propose", str(self.proposal(content="Use a stronger outline.")))["id"]
        self.assertEqual(self.run_cli("accept", second)["version"], 2)
        self.assertIn("stale rollback", self.run_cli("rollback", first, ok=False))
        self.assertEqual(self.run_cli("rollback", second)["version"], 1)
        self.assertEqual((self.root / "knowledge/art/alpha.md").read_text(), "Keep silhouettes readable.")
        self.assertTrue((self.root / "refinements/rollbacks" / (second + ".json")).is_file())
        self.assertEqual(self.run_cli("rollback", first)["version"], 0)
        self.assertFalse((self.root / "knowledge/art/alpha.md").exists())
        self.assertEqual(self.run_cli("context")["index"], [])

    def test_accepted_candidate_cannot_replay_after_rollback(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", identifier)
        self.run_cli("rollback", identifier)
        self.assertIn("cannot be replayed", self.run_cli("accept", identifier, ok=False))
        self.assertEqual(list((self.root / "refinements/transactions").glob("*.json")), [])
        self.assertEqual(self.run_cli("context")["index"], [])
        replacement = self.run_cli("propose", str(self.proposal(content="Updated.")))["id"]
        self.assertEqual(self.run_cli("accept", replacement)["version"], 1)

    def test_index_capacity_rejects_entry_before_journal(self):
        evidence = []
        for number in range(20):
            relative = "docs/evidence-%02d-%s.md" % (number, "x" * 125)
            (self.root / relative).write_text("source", encoding="utf-8")
            evidence.append(relative)
        accepted = 0
        for number in range(40):
            source = self.proposal(slug="topic/%02d" % number, evidence=evidence,
                                   title="T" * 115, when_to_use="W" * 490)
            identifier = KNOWLEDGE.propose(self.root, str(source))["id"]
            try:
                KNOWLEDGE.accept(self.root, identifier)
            except KNOWLEDGE.KnowledgeError as error:
                self.assertIn("index size limit", str(error))
                break
            accepted += 1
        else:
            self.fail("test fixture did not reach index byte limit")
        self.assertGreater(accepted, 0)
        self.assertEqual(len(self.run_cli("context")["index"]), accepted)
        self.assertEqual(list((self.root / "refinements/transactions").glob("*.json")), [])
        self.assertFalse((self.root / "refinements/accepted" / (identifier + ".json")).exists())
        self.assertLessEqual((self.root / "knowledge/index.json").stat().st_size,
                             KNOWLEDGE.MAX_INDEX_BYTES)

    def test_stale_evidence_and_concurrent_candidate(self):
        first = self.run_cli("propose", str(self.proposal()))["id"]
        (self.root / "docs/lesson.md").write_text("new result\n")
        self.assertIn("hash mismatch", self.run_cli("accept", first, ok=False))
        self.assertFalse((self.root / "knowledge/art/alpha.md").exists())
        second = self.run_cli("propose", str(self.proposal()))["id"]
        third = self.run_cli("propose", str(self.proposal(content="Another result.")))["id"]
        self.run_cli("accept", second)
        self.assertIn("stale candidate version", self.run_cli("accept", third, ok=False))

    def test_candidate_tracks_exact_prior_acceptance(self):
        first = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", first)
        stale = self.run_cli("propose", str(self.proposal(content="Old suggestion.")))["id"]
        self.run_cli("rollback", first)
        replacement = self.run_cli("propose", str(self.proposal(content="Replacement.")))["id"]
        self.run_cli("accept", replacement)
        self.assertIn("stale candidate version", self.run_cli("accept", stale, ok=False))

    def test_malformed_traversal_symlinks_and_protected_paths(self):
        self.assertIn("invalid JSON", self._bad_draft("{"))
        self.assertIn("invalid slug", self.run_cli("propose", str(self.proposal(slug="../escape")), ok=False))
        self.assertIn("path traversal", self.run_cli("propose", str(self.proposal(evidence=["../outside"])), ok=False))
        self.assertIn("protected", self.run_cli("propose", str(self.proposal(evidence=["harness/knowledge.py"])), ok=False))
        (self.root / "AGENTS.md").write_text("protected")
        self.assertIn("relative", self.run_cli("propose", str(self.proposal(evidence=[str(self.root / "AGENTS.md")])), ok=False))
        (self.root / "docs/link.md").symlink_to(self.root / "docs/lesson.md")
        self.assertIn("symlink", self.run_cli("propose", str(self.proposal(evidence=["docs/link.md"])), ok=False))
        (self.root / "draft-link.json").symlink_to(self.proposal())
        self.assertIn("symlink", self.run_cli("propose", "draft-link.json", ok=False))
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as outside:
            outside.write("{}")
            outside.flush()
            self.assertIn("outside workspace", self.run_cli("propose", outside.name, ok=False))
        self.assertFalse((self.root / "knowledge/index.json").read_text().find("art/alpha") >= 0)

    def test_symlinked_store_is_rejected(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "knowledge").symlink_to(outside, target_is_directory=True)
        self.assertIn("symlink", self.run_cli("init", ok=False))
        self.assertEqual(list(outside.iterdir()), [])

    def test_malformed_candidate_cannot_be_accepted(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        candidate = self.root / "refinements/candidates" / (identifier + ".json")
        raw = json.loads(candidate.read_text())
        raw["proposal"]["content"] = "x" * 16001
        candidate.write_text(json.dumps(raw))
        self.assertIn("oversized content", self.run_cli("accept", identifier, ok=False))
        self.assertEqual(self.run_cli("context")["index"], [])

    def _bad_draft(self, text):
        (self.root / "draft.json").write_text(text)
        return self.run_cli("propose", "draft.json", ok=False)

    def test_context_excludes_unrelated_bodies_and_bounds(self):
        alpha = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", alpha)
        beta = self.run_cli("propose", str(self.proposal(slug="code/beta", content="Private beta guidance.")))["id"]
        self.run_cli("accept", beta)
        selected = self.run_cli("context", "--slug", "art/alpha")
        self.assertNotIn("Private beta guidance", json.dumps(selected))
        self.assertIn("Private beta guidance", json.dumps(self.run_cli("context", "--slug", "code/beta")))
        self.assertIn("distinct", self.run_cli("context", "--slug", "art/alpha", "--slug", "art/alpha", ok=False))

    def test_external_body_mutation_blocks_rollback(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", identifier)
        (self.root / "knowledge/art/alpha.md").write_text("tampered")
        self.assertIn("changed outside lifecycle", self.run_cli("rollback", identifier, ok=False))
        self.assertFalse((self.root / "refinements/rollbacks" / (identifier + ".json")).exists())

    def test_interrupted_accept_recovers_on_next_cli(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        original = KNOWLEDGE.write_atomic
        interrupted = {"once": False}

        def fail_index_once(path, data):
            if path == self.root / "knowledge/index.json" and not interrupted["once"]:
                interrupted["once"] = True
                raise OSError("injected index write failure")
            return original(path, data)

        with mock.patch.object(KNOWLEDGE, "write_atomic", side_effect=fail_index_once):
            with self.assertRaisesRegex(OSError, "injected"):
                KNOWLEDGE.accept(self.root, identifier)
        self.assertTrue((self.root / "refinements/transactions" / ("accept-" + identifier + ".json")).exists())
        self.assertEqual(self.run_cli("context", "--slug", "art/alpha")["selected"][0]["content"],
                         "Keep silhouettes readable.")
        self.assertEqual(list((self.root / "refinements/transactions").glob("*.json")), [])
        self.assertEqual(self.run_cli("accept", identifier)["status"], "accepted")

    def test_interrupted_before_history_recovers_on_next_cli(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        with mock.patch.object(KNOWLEDGE, "ensure_immutable", side_effect=OSError("injected history failure")):
            with self.assertRaisesRegex(OSError, "injected"):
                KNOWLEDGE.accept(self.root, identifier)
        pending = self.root / "refinements/transactions" / ("accept-" + identifier + ".json")
        self.assertTrue(pending.is_file())
        self.assertFalse((self.root / "refinements/accepted" / (identifier + ".json")).exists())
        self.assertEqual(self.run_cli("context", "--slug", "art/alpha")["selected"][0]["version"], 1)
        self.assertTrue((self.root / "refinements/accepted" / (identifier + ".json")).is_file())
        self.assertFalse(pending.exists())

    def test_interrupted_rollback_recovers_on_next_cli(self):
        identifier = self.run_cli("propose", str(self.proposal()))["id"]
        self.run_cli("accept", identifier)
        original = KNOWLEDGE.write_atomic
        interrupted = {"once": False}

        def fail_index_once(path, data):
            if path == self.root / "knowledge/index.json" and not interrupted["once"]:
                interrupted["once"] = True
                raise OSError("injected index write failure")
            return original(path, data)

        with mock.patch.object(KNOWLEDGE, "write_atomic", side_effect=fail_index_once):
            with self.assertRaisesRegex(OSError, "injected"):
                KNOWLEDGE.rollback(self.root, identifier)
        self.assertTrue((self.root / "refinements/transactions" / ("rollback-" + identifier + ".json")).exists())
        self.assertEqual(self.run_cli("context")["index"], [])
        self.assertFalse((self.root / "knowledge/art/alpha.md").exists())
        self.assertTrue((self.root / "refinements/rollbacks" / (identifier + ".json")).exists())
        self.assertEqual(list((self.root / "refinements/transactions").glob("*.json")), [])
        self.assertEqual(self.run_cli("rollback", identifier)["status"], "rolled_back")


if __name__ == "__main__":
    unittest.main()
