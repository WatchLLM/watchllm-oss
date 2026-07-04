from pathlib import Path
import unittest

RULE_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "rules"

RULE_CATEGORIES = (
    "secrets",
    "forbidden_imports",
    "boundary",
    "auth_flow",
)


def discover_fixture_files(category: str, outcome: str) -> tuple[Path, ...]:
    directory = RULE_FIXTURE_DIR / category / outcome
    return tuple(sorted(path for path in directory.iterdir() if path.suffix in {".js", ".ts"}))


class TestFixtureCorpus(unittest.TestCase):
    def test_category_directories_exist(self):
        for category in RULE_CATEGORIES:
            cat_dir = RULE_FIXTURE_DIR / category
            self.assertTrue(cat_dir.is_dir(), f"Missing category directory: {cat_dir}")
            pass_dir = cat_dir / "pass"
            fail_dir = cat_dir / "fail"
            self.assertTrue(pass_dir.is_dir(), f"Missing pass directory: {pass_dir}")
            self.assertTrue(fail_dir.is_dir(), f"Missing fail directory: {fail_dir}")

    def test_each_category_has_pass_and_fail_fixtures(self):
        for category in RULE_CATEGORIES:
            pass_files = discover_fixture_files(category, "pass")
            fail_files = discover_fixture_files(category, "fail")
            self.assertTrue(len(pass_files) > 0, f"No pass fixtures for {category}")
            self.assertTrue(len(fail_files) > 0, f"No fail fixtures for {category}")

    def test_all_fixtures_readable_and_minimal(self):
        for category in RULE_CATEGORIES:
            for outcome in ("pass", "fail"):
                for path in discover_fixture_files(category, outcome):
                    with self.subTest(fixture=path):
                        content = path.read_text(encoding="utf-8")
                        stripped = content.strip()
                        self.assertTrue(len(stripped) > 0, f"Fixture is empty: {path}")
                        lines = stripped.splitlines()
                        self.assertLessEqual(len(lines), 20, f"Fixture too long ({len(lines)} lines): {path}")

    def test_automatic_discovery_is_deterministic(self):
        paths = []
        for category in sorted(RULE_CATEGORIES):
            for outcome in ("fail", "pass"):
                for path in discover_fixture_files(category, outcome):
                    paths.append(path.relative_to(RULE_FIXTURE_DIR).as_posix())
        self.assertEqual(paths, sorted(paths))


if __name__ == "__main__":
    unittest.main()
