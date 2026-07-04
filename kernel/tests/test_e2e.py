import json
import subprocess
import sys
import unittest
from pathlib import Path

from watchllm_kernel.cli import build_default_rules
from watchllm_kernel.engine import ENFORCE_MODE, SHADOW_MODE, evaluate_source
from watchllm_kernel.models import Decision, RuleDecision

RULE_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "rules"
FIXTURE_SUFFIXES = {".js", ".ts"}


def discover_rule_fixtures(outcome: str) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in RULE_FIXTURE_DIR.rglob("*")
            if path.is_file()
            and path.suffix in FIXTURE_SUFFIXES
            and path.parent.name == outcome
        )
    )


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def infer_language(path: Path) -> str:
    if path.suffix == ".ts":
        return "typescript"
    return "javascript"


def result_snapshot(result):
    return {
        "decision": result.decision.value,
        "file_path": result.file_path,
        "language": result.language,
        "mode": result.mode,
        "rule_results": [
            {
                "rule_id": rule_result.rule_id,
                "decision": rule_result.decision.value,
                "violations": [
                    {
                        "rule_id": violation.rule_id,
                        "message": violation.message,
                        "severity": violation.severity.value,
                        "evidence": violation.evidence,
                        "line": violation.location.line if violation.location else None,
                        "column": violation.location.column if violation.location else None,
                    }
                    for violation in rule_result.violations
                ],
            }
            for rule_result in result.rule_results
        ],
    }


class TestEndToEndBehaviour(unittest.TestCase):
    def test_passing_fixtures_allow_in_enforce_mode(self):
        fixtures = discover_rule_fixtures("pass")
        self.assertTrue(fixtures, "Expected pass fixtures to exist")

        for fixture in fixtures:
            with self.subTest(fixture=fixture.relative_to(RULE_FIXTURE_DIR).as_posix()):
                result = evaluate_source(
                    read_source(fixture),
                    file_path=str(fixture),
                    language=infer_language(fixture),
                    rules=build_default_rules(),
                    mode=ENFORCE_MODE,
                )
                self.assertEqual(result.decision, Decision.ALLOW)

    def test_failing_fixtures_block_in_enforce_mode(self):
        fixtures = discover_rule_fixtures("fail")
        self.assertTrue(fixtures, "Expected fail fixtures to exist")

        for fixture in fixtures:
            with self.subTest(fixture=fixture.relative_to(RULE_FIXTURE_DIR).as_posix()):
                result = evaluate_source(
                    read_source(fixture),
                    file_path=str(fixture),
                    language=infer_language(fixture),
                    rules=build_default_rules(),
                    mode=ENFORCE_MODE,
                )
                self.assertEqual(result.decision, Decision.BLOCK)
                self.assertTrue(
                    any(
                        rule_result.decision == RuleDecision.FAIL
                        for rule_result in result.rule_results
                    ),
                    "A blocking fixture must include at least one FAIL rule result",
                )

    def test_shadow_mode_does_not_block_failing_fixtures(self):
        fixtures = discover_rule_fixtures("fail")
        self.assertTrue(fixtures, "Expected fail fixtures to exist")

        for fixture in fixtures:
            with self.subTest(fixture=fixture.relative_to(RULE_FIXTURE_DIR).as_posix()):
                result = evaluate_source(
                    read_source(fixture),
                    file_path=str(fixture),
                    language=infer_language(fixture),
                    rules=build_default_rules(),
                    mode=SHADOW_MODE,
                )
                self.assertEqual(result.decision, Decision.ALLOW)
                self.assertTrue(
                    any(
                        rule_result.decision == RuleDecision.FAIL
                        for rule_result in result.rule_results
                    ),
                    "Shadow mode should preserve failing rule results",
                )

    def test_regression_results_are_deterministic_across_runs(self):
        fixtures = tuple(sorted(discover_rule_fixtures("pass") + discover_rule_fixtures("fail")))
        self.assertTrue(fixtures, "Expected rule fixtures to exist")

        first_run = []
        second_run = []

        for fixture in fixtures:
            kwargs = {
                "source": read_source(fixture),
                "file_path": str(fixture),
                "language": infer_language(fixture),
                "rules": build_default_rules(),
                "mode": ENFORCE_MODE,
            }
            first_run.append(
                (
                    fixture.relative_to(RULE_FIXTURE_DIR).as_posix(),
                    result_snapshot(evaluate_source(**kwargs)),
                )
            )

            kwargs["rules"] = build_default_rules()
            second_run.append(
                (
                    fixture.relative_to(RULE_FIXTURE_DIR).as_posix(),
                    result_snapshot(evaluate_source(**kwargs)),
                )
            )

        self.assertEqual(first_run, second_run)

    def test_cli_stdin_save_path_simulation_blocks_unsafe_source(self):
        fixture = RULE_FIXTURE_DIR / "forbidden_imports" / "fail" / "child_process_import.js"
        source = read_source(fixture)

        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "watchllm_kernel",
                "evaluate",
                "--stdin",
                "--json",
                "--language",
                "javascript",
                "--mode",
                "enforce",
                str(fixture),
            ],
            input=source,
            capture_output=True,
            text=True,
        )

        self.assertEqual(proc.returncode, 1, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["decision"], "BLOCK")

    def test_cli_json_output_is_valid_and_stable(self):
        fixture = RULE_FIXTURE_DIR / "forbidden_imports" / "pass" / "safe_local_import.js"

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

        first = subprocess.run(cmd, capture_output=True, text=True)
        second = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(first.returncode, 0, msg=first.stderr)
        self.assertEqual(second.returncode, 0, msg=second.stderr)
        self.assertEqual(first.stdout, second.stdout)

        payload = json.loads(first.stdout)
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertIn("rule_results", payload)


if __name__ == "__main__":
    unittest.main()
