import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "rules"


class TestCLI(unittest.TestCase):
    def test_module_help_exit_zero(self):
        """python -m watchllm_kernel --help exits 0"""
        result = subprocess.run(
            [sys.executable, "-m", "watchllm_kernel", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_help_output_contains_watchllm(self):
        """Output of --help contains WatchLLM Kernel or watchllm"""
        result = subprocess.run(
            [sys.executable, "-m", "watchllm_kernel", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertIn("watchllm", result.stdout.lower())

    def test_import_cli_does_not_break(self):
        """Importing watchllm_kernel.cli does not trigger missing placeholder imports"""
        try:
            from watchllm_kernel import cli
        except Exception as exc:
            self.fail(f"Importing watchllm_kernel.cli raised {exc}")

    def test_main_help_returns_cleanly(self):
        """main(["--help"]) raises SystemExit(0) or returns cleanly"""
        from watchllm_kernel.cli import main
        try:
            ret = main(["--help"])
            self.assertEqual(ret, 0)
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    # ------------------------------------------------------------------
    # Task 11 CLI evaluation tests
    # ------------------------------------------------------------------

    def _run_evaluate(self, file_path: Path, mode="enforce", extra_args=None):
        cmd = [
            sys.executable,
            "-m",
            "watchllm_kernel",
            "evaluate",
            str(file_path),
            "--json",
            "--mode",
            mode,
        ]
        if extra_args:
            cmd.extend(extra_args)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc

    def test_evaluate_secret_pass_returns_allow(self):
        """env_stripe_secret.ts should be ALLOW in enforce mode"""
        fixture = FIXTURES_DIR / "secrets" / "pass" / "env_stripe_secret.ts"
        proc = self._run_evaluate(fixture)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "ALLOW")

    def test_evaluate_secret_fail_returns_block(self):
        """hardcoded_stripe_secret.ts should be BLOCK in enforce mode"""
        fixture = FIXTURES_DIR / "secrets" / "fail" / "hardcoded_stripe_secret.ts"
        proc = self._run_evaluate(fixture)
        self.assertNotEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")

    def test_evaluate_forbidden_import_fail_returns_block(self):
        """child_process_import.js should be BLOCK in enforce mode"""
        fixture = FIXTURES_DIR / "forbidden_imports" / "fail" / "child_process_import.js"
        proc = self._run_evaluate(fixture)
        self.assertNotEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")

    def test_evaluate_shadow_mode_allows_failing_fixture(self):
        """hardcoded_stripe_secret.ts in shadow mode should be ALLOW but contain a FAIL rule result"""
        fixture = FIXTURES_DIR / "secrets" / "fail" / "hardcoded_stripe_secret.ts"
        proc = self._run_evaluate(fixture, mode="shadow")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertTrue(
            any(
                rule_result["decision"] == "FAIL"
                for rule_result in payload["rule_results"]
            )
        )

    def test_evaluate_stdin_works(self):
        """Reading from stdin should evaluate correctly"""
        source = 'const key = "sk_live_1234567890abcdef";'
        cmd = [
            sys.executable,
            "-m",
            "watchllm_kernel",
            "evaluate",
            "--stdin",
            "--json",
            "--mode",
            "enforce",
        ]
        proc = subprocess.run(cmd, input=source, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")

    # ------------------------------------------------------------------
    # Task 14 local logging integration test
    # ------------------------------------------------------------------

    def test_blocked_evaluation_writes_local_log(self):
        """A blocked evaluation writes a JSONL log entry."""
        fixture = FIXTURES_DIR / "forbidden_imports" / "fail" / "child_process_import.js"

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "violations.jsonl"
            env = os.environ.copy()
            env["WATCHLLM_LOG_PATH"] = str(log_path)

            cmd = [
                sys.executable,
                "-m",
                "watchllm_kernel",
                "evaluate",
                str(fixture),
                "--json",
                "--language",
                "javascript",
                "--mode",
                "enforce",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env)

            self.assertNotEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["decision"], "BLOCK")

            self.assertTrue(log_path.exists(), "Expected log file to exist")
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1, "Expected exactly one log line")

            log_entry = json.loads(lines[0])
            self.assertEqual(
                log_entry["schema_version"],
                "watchllm.kernel.violation_report.v1",
            )
            self.assertEqual(log_entry["decision"], "BLOCK")
            self.assertEqual(log_entry["mode"], "enforce")
            self.assertIsInstance(log_entry["violations"], list)
            self.assertGreater(len(log_entry["violations"]), 0)
            self.assertIn("rule_id", log_entry["violations"][0])


if __name__ == "__main__":
    unittest.main()
