"""CLI contract tests for editor integration readiness.

Validates exit codes, JSON output, stdin usage, and logging isolation
so that editor hosts can rely on the kernel without internal knowledge
of rule mechanics.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "rules"


class TestCLIContract(unittest.TestCase):
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run(self, *args, stdin_text=None, env=None):
        cmd = [sys.executable, "-m", "watchllm_kernel", "check", *args]
        proc = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            env=env,
        )
        return proc

    # ------------------------------------------------------------------
    # Exit code contract
    # ------------------------------------------------------------------

    def test_enforce_block_exit_code(self):
        """Failing fixture in enforce mode exits 1 and returns BLOCK JSON."""
        fixture = FIXTURES_DIR / "forbidden_imports" / "fail" / "child_process_import.js"
        proc = self._run(
            "--filepath", str(fixture),
            "--json",
            "--language", "js",
            "--mode", "enforce",
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")
        self.assertEqual(payload["mode"], "enforce")
        self.assertIn("rule_results", payload)

    def test_shadow_allow_exit_code(self):
        """Failing fixture in shadow mode exits 0 and returns ALLOW JSON."""
        fixture = FIXTURES_DIR / "forbidden_imports" / "fail" / "child_process_import.js"
        proc = self._run(
            "--filepath", str(fixture),
            "--json",
            "--language", "js",
            "--mode", "shadow",
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertTrue(
            any(
                rr["status"] == "FAIL"
                for rr in payload["rule_results"]
            ),
            "Shadow mode should preserve failing rule results",
        )

    # ------------------------------------------------------------------
    # Stdin contract
    # ------------------------------------------------------------------

    def test_stdin_block_exit_code(self):
        """Stdin evaluation of unsafe source exits 1 and returns BLOCK JSON."""
        source = 'import { execSync } from "child_process";\nexecSync("rm -rf /tmp/example");'
        proc = self._run(
            "--stdin",
            "--json",
            "--language", "js",
            "--mode", "enforce",
            stdin_text=source,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")
        self.assertIsNone(payload["file_path"])
        self.assertEqual(payload["language"], "javascript")

    # ------------------------------------------------------------------
    # Input error contract
    # ------------------------------------------------------------------

    def test_missing_input_exit_code(self):
        """No file and no stdin exits 2 with error on stderr."""
        proc = self._run(
            "--json",
            "--language", "js",
            "--mode", "enforce",
        )
        self.assertEqual(proc.returncode, 2, msg=proc.stderr)
        self.assertIn("Error", proc.stderr)
        self.assertEqual(proc.stdout.strip(), "")

    # ------------------------------------------------------------------
    # Logging isolation contract
    # ------------------------------------------------------------------

    def test_json_stdout_not_polluted_by_logging(self):
        """Blocked evaluation with --json must not leak log text into stdout."""
        fixture = FIXTURES_DIR / "forbidden_imports" / "fail" / "child_process_import.js"

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "violations.jsonl"
            env = os.environ.copy()
            env["WATCHLLM_LOG_PATH"] = str(log_path)

            proc = self._run(
                "--filepath", str(fixture),
                "--json",
                "--language", "js",
                "--mode", "enforce",
                env=env,
            )

            self.assertEqual(proc.returncode, 1, msg=proc.stderr)

            # stdout must be valid JSON
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["decision"], "BLOCK")

            # log file must exist
            self.assertTrue(log_path.exists(), "Expected log file to exist")

            # stdout must not contain log text
            stdout_text = proc.stdout
            self.assertNotIn("violations.jsonl", stdout_text)
            self.assertNotIn("WATCHLLM_LOG_PATH", stdout_text)


if __name__ == "__main__":
    unittest.main()
