"""Unit tests for the forbidden-import rule."""

import unittest

from watchllm_kernel.models import RuleDecision
from watchllm_kernel.rules.forbidden_imports import (
    ForbiddenImportRule,
    extract_import_paths,
    normalize_import_path,
)


class TestForbiddenImportRule(unittest.TestCase):
    # ------------------------------------------------------------------
    # Import extraction
    # ------------------------------------------------------------------

    def test_extract_import_statement(self):
        source = 'import fs from "fs";'
        paths = extract_import_paths(source)
        self.assertIn("fs", paths)

    def test_extract_require_call(self):
        source = 'const cp = require("child_process");'
        paths = extract_import_paths(source)
        self.assertIn("child_process", paths)

    def test_extract_relative_import(self):
        source = 'import utils from "../../utils";'
        paths = extract_import_paths(source)
        self.assertIn("../../utils", paths)

    def test_extract_no_imports(self):
        source = "const x = 1;"
        paths = extract_import_paths(source)
        self.assertEqual(paths, [])

    # ------------------------------------------------------------------
    # Path normalisation
    # ------------------------------------------------------------------

    def test_normalize_strips_leading_dot_slash(self):
        self.assertEqual(normalize_import_path("./utils"), "utils")

    def test_normalize_strips_trailing_slash(self):
        self.assertEqual(normalize_import_path("utils/"), "utils")

    def test_normalize_preserves_relative_prefix(self):
        self.assertEqual(normalize_import_path("../db/internal"), "../db/internal")

    # ------------------------------------------------------------------
    # Rule evaluation – pass cases
    # ------------------------------------------------------------------

    def test_safe_local_import_passes(self):
        source = 'import { helper } from "./utils";'
        rule = ForbiddenImportRule()
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.PASS)

    def test_allowed_module_passes(self):
        source = 'import express from "express";'
        rule = ForbiddenImportRule()
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.PASS)

    # ------------------------------------------------------------------
    # Rule evaluation – fail cases
    # ------------------------------------------------------------------

    def test_forbidden_module_fails(self):
        source = 'import cp from "child_process";'
        rule = ForbiddenImportRule()
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.FAIL)
        self.assertTrue(any("child_process" in v.message for v in result.violations))

    def test_forbidden_relative_prefix_fails(self):
        source = 'import db from "../../../db/internal";'
        rule = ForbiddenImportRule()
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.FAIL)
        self.assertTrue(
            any("../../../db/internal" in v.evidence for v in result.violations)
        )

    def test_multiple_forbidden_imports_fails(self):
        source = (
            'import cp from "child_process";\n'
            'import v from "vm";\n'
        )
        rule = ForbiddenImportRule()
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.FAIL)
        self.assertGreaterEqual(len(result.violations), 2)

    # ------------------------------------------------------------------
    # Custom configuration
    # ------------------------------------------------------------------

    def test_custom_forbidden_modules(self):
        source = 'import express from "express";'
        rule = ForbiddenImportRule(forbidden_modules=frozenset({"express"}))
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.FAIL)

    def test_custom_forbidden_prefixes(self):
        source = 'import utils from "./utils";'
        rule = ForbiddenImportRule(forbidden_prefixes=frozenset({"./"}))
        result = rule.evaluate(source)
        self.assertEqual(result.decision, RuleDecision.FAIL)


if __name__ == "__main__":
    unittest.main()
