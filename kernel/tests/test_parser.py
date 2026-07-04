"""Unit tests for the parser abstraction."""

import unittest

from watchllm_kernel.parser import parse_source, ParseResult


class TestParser(unittest.TestCase):
    # ------------------------------------------------------------------
    # Basic parsing
    # ------------------------------------------------------------------

    def test_parse_javascript_simple(self):
        result = parse_source("const x = 1;", "javascript")
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(result.language, "javascript")
        self.assertIsNotNone(result.tree)
        self.assertIsNotNone(result.root_node)

    def test_parse_typescript_simple(self):
        result = parse_source("const x: number = 1;", "typescript")
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(result.language, "typescript")

    def test_parse_tsx_simple(self):
        result = parse_source("const el = <div />;", "tsx")
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(result.language, "tsx")

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError) as ctx:
            parse_source("x = 1", "python")
        self.assertIn("python", str(ctx.exception))

    def test_syntax_error_does_not_crash(self):
        """Tree-sitter is error-tolerant; parsing should succeed even with
        syntax errors, producing an ERROR node in the tree."""
        result = parse_source("const x = ;", "javascript")
        self.assertIsNotNone(result.tree)
        # The root node should still exist.
        self.assertTrue(result.root_node)

    # ------------------------------------------------------------------
    # ParseResult helpers
    # ------------------------------------------------------------------

    def test_root_node_accessor(self):
        result = parse_source("let a = 1;", "javascript")
        root = result.root_node
        self.assertEqual(root.type, "program")

    def test_walk_returns_cursor(self):
        result = parse_source("let a = 1;", "javascript")
        cursor = result.walk()
        self.assertTrue(cursor.node)

    def test_query_captures(self):
        result = parse_source(
            'const key = "sk_live_123";\n'
            'const env = process.env.STRIPE_SECRET;\n',
            "javascript",
        )
        captures = result.query("(string) @str")
        self.assertIn("str", captures)
        strings = [n.text.decode("utf-8") for n in captures["str"]]
        # Only quoted string literals are captured by (string).
        # process.env.STRIPE_SECRET is a member expression, not a string.
        self.assertIn('"sk_live_123"', strings)
        self.assertNotIn('"STRIPE_SECRET"', strings)

    def test_query_no_matches(self):
        result = parse_source("let x = 1;", "javascript")
        captures = result.query("(function_declaration) @func")
        self.assertEqual(captures, {})

    # ------------------------------------------------------------------
    # file_path propagation
    # ------------------------------------------------------------------

    def test_file_path_stored(self):
        result = parse_source("x = 1", "javascript", file_path="/tmp/test.js")
        self.assertEqual(result.file_path, "/tmp/test.js")

    def test_file_path_none_by_default(self):
        result = parse_source("x = 1", "javascript")
        self.assertIsNone(result.file_path)


if __name__ == "__main__":
    unittest.main()
