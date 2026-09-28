import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


VERIFY = Path(__file__).resolve().parents[1] / "harness/verify.py"


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        game = self.root / "game"
        (game / "src").mkdir(parents=True)
        (game / "src/main.txt").write_text("one\n")
        (game / "check.py").write_text(
            "from pathlib import Path\n"
            "p=Path('count'); p.write_text(str(int(p.read_text())+1) if p.exists() else '1')\n"
            "Path('out.txt').write_text('ok')\n"
        )
        (game / "tool.py").write_text("print('tool-v1')\n")
        self.group = {
            "cwd": "game",
            "command": [sys.executable, "check.py"],
            "inputs": ["game/src"],
            "env_keys": ["VERIFY_TEST_TOKEN"],
            "tool_versions": [[sys.executable, "tool.py"]],
            "outputs": ["game/out.txt"],
            "cache": True,
            "max_age_seconds": 86400,
            "timeout_seconds": 2,
        }
        self.write_config()

    def write_config(self):
        (self.root / "validation.json").write_text(json.dumps({"version": 1, "groups": {"smoke": self.group}}))

    def cli(self, action="run", *extra, env=None):
        values = os.environ.copy()
        values["VERIFY_TEST_TOKEN"] = "secret-one"
        if env:
            values.update(env)
        p = subprocess.run([sys.executable, str(VERIFY), "--workspace", str(self.root), action, "smoke", *extra],
                           text=True, capture_output=True, env=values, timeout=8)
        return p, json.loads(p.stdout) if p.stdout.strip() else {}

    def test_run_reuses_only_matching_passed_receipt(self):
        first, a = self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(a["state"], "passed")
        first_receipt = json.loads((self.root / "docs/runs/validation" / a["receipt"]).read_text())
        self.assertGreaterEqual(first_receipt["elapsed_seconds"], 0)
        self.assertGreaterEqual(first_receipt["finished_at"], first_receipt["started_at"])
        second, b = self.cli()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(b["state"], "cached-passed")
        self.assertEqual((self.root / "game/count").read_text(), "1")
        forced, c = self.cli("run", "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertEqual(c["state"], "passed")
        self.assertEqual((self.root / "game/count").read_text(), "2")
        receipts = list((self.root / "docs/runs/validation").glob("*.json"))
        self.assertEqual(len(receipts), 2)

    def test_directory_addition_and_config_env_tool_change_invalidate(self):
        self.assertEqual(self.cli()[1]["state"], "passed")
        (self.root / "game/src/new.txt").write_text("new")
        self.assertEqual(self.cli()[1]["state"], "passed")
        self.assertEqual(self.cli()[1]["state"], "cached-passed")
        self.group["command"] = [sys.executable, "check.py", "extra"]
        self.write_config()
        self.assertEqual(self.cli()[1]["state"], "passed")
        self.assertEqual(self.cli(env={"VERIFY_TEST_TOKEN": "secret-two"})[1]["state"], "passed")
        (self.root / "game/tool.py").write_text("print('tool-v2')\n")
        p, summary = self.cli(env={"VERIFY_TEST_TOKEN": "secret-two"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(summary["state"], "passed")
        self.assertNotIn("secret-two", p.stdout + p.stderr)
        self.assertEqual((self.root / "game/count").read_text(), "5")

    def test_input_executable_bit_change_invalidates_cache(self):
        source = self.root / "game/src/main.txt"
        source.chmod(0o755)
        self.assertEqual(self.cli()[1]["state"], "passed")
        source.chmod(0o644)
        rerun, summary = self.cli()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(summary["state"], "passed")
        self.assertEqual((self.root / "game/count").read_text(), "2")

    def test_tampered_log_or_output_forces_execution(self):
        self.assertEqual(self.cli()[1]["state"], "passed")
        receipt = next((self.root / "docs/runs/validation").glob("*.json"))
        record = json.loads(receipt.read_text())
        (self.root / "docs/runs/validation" / record["log"]).write_text("tampered")
        self.assertEqual(self.cli()[1]["state"], "passed")
        (self.root / "game/out.txt").write_text("tampered")
        self.assertEqual(self.cli()[1]["state"], "passed")
        (self.root / "game/out.txt").unlink()
        self.assertEqual(self.cli()[1]["state"], "passed")
        self.assertEqual((self.root / "game/count").read_text(), "4")

    def test_corrupt_latest_receipt_prevents_reuse(self):
        self.assertEqual(self.cli()[1]["state"], "passed")
        receipt = next((self.root / "docs/runs/validation").glob("*.json"))
        receipt.write_text("[]")
        rerun, summary = self.cli()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(summary["state"], "passed")
        self.assertEqual((self.root / "game/count").read_text(), "2")

    def test_latest_receipt_with_wrong_group_never_falls_back(self):
        self.assertEqual(self.cli()[1]["state"], "passed")
        folder = self.root / "docs/runs/validation"
        first = next(folder.glob("*.json"))
        prefix = first.name.split("-", 1)[0]
        (folder / (prefix + "-99999999999999999999-wrong.json")).write_text(
            json.dumps({"group": "other", "state": "failed"}))
        rerun, summary = self.cli()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(summary["state"], "passed")
        self.assertEqual((self.root / "game/count").read_text(), "2")

    def test_latest_failure_blocks_older_success(self):
        self.assertEqual(self.cli()[1]["state"], "passed")
        (self.root / "game/check.py").write_text("raise SystemExit(7)\n")
        failed, summary = self.cli("run", "--force")
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(summary["state"], "failed")
        (self.root / "game/check.py").write_text("print('recovered')\nfrom pathlib import Path\nPath('out.txt').write_text('ok')\n")
        rerun, summary = self.cli()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(summary["state"], "passed")

    def test_input_mutation_during_run_is_recorded_as_failed(self):
        (self.root / "game/check.py").write_text(
            "from pathlib import Path\n"
            "Path('src/main.txt').write_text('two')\n"
            "Path('out.txt').write_text('ok')\n"
        )
        failed, summary = self.cli()
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(summary["state"], "failed")
        self.assertIn("changed during validation", summary["reason"])
        rerun, summary = self.cli()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(summary["state"], "passed")

    def test_concurrent_runs_share_one_execution(self):
        script = self.root / "game/check.py"
        script.write_text(script.read_text().replace("Path('out.txt')", "__import__('time').sleep(.3); Path('out.txt')"))
        env = dict(os.environ, VERIFY_TEST_TOKEN="secret-one")
        command = [sys.executable, str(VERIFY), "--workspace", str(self.root), "run", "smoke"]
        first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        time.sleep(.05)
        second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        first_out, first_err = first.communicate(timeout=5)
        second_out, second_err = second.communicate(timeout=5)
        self.assertEqual(first.returncode, 0, first_err)
        self.assertEqual(second.returncode, 0, second_err)
        self.assertEqual({json.loads(first_out)["state"], json.loads(second_out)["state"]},
                         {"passed", "cached-passed"})
        self.assertEqual((self.root / "game/count").read_text(), "1")

    def _assert_signal_cleans_owned_process_group_and_records_failure(self, signum):
        child_code = ("import time; from pathlib import Path; time.sleep(.7); "
                      "Path('survived').write_text('yes'); time.sleep(10)")
        (self.root / "game/check.py").write_text(
            "import os, subprocess, sys, time\n"
            "from pathlib import Path\n"
            "child=subprocess.Popen([sys.executable, '-c', " + repr(child_code) + "])\n"
            "Path('pids').write_text(str(os.getpid())+' '+str(child.pid))\n"
            "time.sleep(10)\n"
        )
        self.group["outputs"] = []
        self.group["timeout_seconds"] = 20
        self.write_config()
        env = dict(os.environ, VERIFY_TEST_TOKEN="secret-one")
        command = [sys.executable, str(VERIFY), "--workspace", str(self.root), "run", "smoke"]
        verifier = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        command_pid = None
        try:
            marker = self.root / "game/pids"
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(marker.exists())
            command_pid = int(marker.read_text().split()[0])
            os.kill(verifier.pid, signum)
            stdout, stderr = verifier.communicate(timeout=3)
            self.assertNotEqual(verifier.returncode, 0)
            self.assertEqual(json.loads(stdout)["state"], "failed", stderr)
            receipt = next((self.root / "docs/runs/validation").glob("*.json"))
            self.assertIn("interrupted", json.loads(receipt.read_text())["reason"])
            time.sleep(.8)
            self.assertFalse((self.root / "game/survived").exists())
        finally:
            if verifier.poll() is None:
                verifier.kill()
                verifier.communicate()
            if command_pid is not None:
                try:
                    os.killpg(command_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_sigterm_cleans_owned_process_group_and_records_failure(self):
        self._assert_signal_cleans_owned_process_group_and_records_failure(signal.SIGTERM)

    def test_sigint_cleans_owned_process_group_and_records_failure(self):
        self._assert_signal_cleans_owned_process_group_and_records_failure(signal.SIGINT)

    def test_successful_command_cleans_background_descendants(self):
        child_code = ("import time; from pathlib import Path; time.sleep(.7); "
                      "Path('survived').write_text('yes'); time.sleep(10)")
        (self.root / "game/check.py").write_text(
            "import os, subprocess, sys\n"
            "from pathlib import Path\n"
            "child=subprocess.Popen([sys.executable, '-c', " + repr(child_code) + "])\n"
            "Path('pids').write_text(str(os.getpid())+' '+str(child.pid))\n"
            "Path('out.txt').write_text('ok')\n"
        )
        command_pid = None
        try:
            run, summary = self.cli()
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(summary["state"], "passed")
            command_pid = int((self.root / "game/pids").read_text().split()[0])
            time.sleep(.8)
            self.assertFalse((self.root / "game/survived").exists())
        finally:
            if command_pid is not None:
                try:
                    os.killpg(command_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_sigkill_during_forced_run_blocks_older_success(self):
        first, summary = self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(summary["state"], "passed")
        script = self.root / "game/check.py"
        original = script.read_text()
        script.write_text(
            "import os, time\n"
            "from pathlib import Path\n"
            "Path('started').write_text(str(os.getpid()))\n"
            "time.sleep(10)\n"
        )
        env = dict(os.environ, VERIFY_TEST_TOKEN="secret-one")
        command = [sys.executable, str(VERIFY), "--workspace", str(self.root), "run", "smoke", "--force"]
        verifier = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        command_pid = None
        try:
            marker = self.root / "game/started"
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(marker.exists())
            command_pid = int(marker.read_text())
            os.kill(verifier.pid, signal.SIGKILL)
            verifier.communicate(timeout=3)
            status, current = self.cli("status")
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(current["state"], "stale")
            script.write_text(original)
            rerun, summary = self.cli()
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual(summary["state"], "passed")
            self.assertEqual((self.root / "game/count").read_text(), "2")
        finally:
            if verifier.poll() is None:
                verifier.kill()
                verifier.communicate()
            if command_pid is not None:
                try:
                    os.killpg(command_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_status_is_read_only_and_missing_output_is_not_passed(self):
        status, summary = self.cli("status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(summary["state"], "missing")
        self.assertFalse((self.root / "docs/runs/validation").exists())
        (self.root / "game/check.py").write_text("print('no output')\n")
        failed, summary = self.cli()
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(summary["state"], "failed")

    def test_timeout_and_path_rejection(self):
        (self.root / "game/check.py").write_text("import time\ntime.sleep(5)\n")
        self.group["timeout_seconds"] = 0.1
        self.group["outputs"] = []
        self.write_config()
        failed, summary = self.cli()
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(summary["state"], "failed")
        self.assertTrue(summary["timed_out"])
        self.group["inputs"] = ["../outside"]
        self.write_config()
        rejected, _ = self.cli()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("path", rejected.stderr.lower())
        self.group["inputs"] = ["game/src"]
        (self.root / "game/src/escape").symlink_to(self.root.parent)
        self.write_config()
        rejected, _ = self.cli()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("symlink", rejected.stderr.lower())


if __name__ == "__main__":
    unittest.main()
