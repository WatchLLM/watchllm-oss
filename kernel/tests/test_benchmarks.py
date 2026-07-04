import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "watchllm.kernel.benchmark.v1"
BENCHMARK_KEYS = {
    "count",
    "min_ms",
    "median_ms",
    "p95_ms",
    "max_ms",
    "mean_ms",
}


class TestBenchmarks(unittest.TestCase):
    def test_benchmark_json_command_outputs_valid_schema(self):
        proc = subprocess.run(
            [
                sys.executable,
                "benchmarks/run_benchmarks.py",
                "--iterations",
                "1",
                "--warmup",
                "0",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)

        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertGreater(payload["fixture_count"], 0)

        self.assertIn("benchmarks", payload)
        benchmarks = payload["benchmarks"]

        for name in ("parse_ms", "rule_evaluation_ms", "end_to_end_ms"):
            self.assertIn(name, benchmarks)
            stats = benchmarks[name]
            for key in BENCHMARK_KEYS:
                self.assertIn(key, stats)
                self.assertIsInstance(stats[key], (int, float))

    def test_benchmark_output_file_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "benchmarks.json"

            proc = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/run_benchmarks.py",
                    "--iterations",
                    "1",
                    "--warmup",
                    "0",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue(output_path.exists())

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
