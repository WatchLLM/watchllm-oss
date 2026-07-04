"""Parser abstraction for the WatchLLM kernel.

Provides a minimal, deterministic interface to Tree-sitter for JavaScript
and TypeScript source files.  The module exposes a single `parse_source`
function that returns a structured parse result containing the raw
Tree-sitter tree and a convenience traversal helper.

This module is intentionally narrow: it does not perform rule evaluation,
enforcement, or any decision-making.  It exists solely to give rule
implementations a stable AST surface.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

import tree_sitter_javascript
import tree_sitter_typescript
from tree_sitter import Language, Parser, Node, Tree


# ---------------------------------------------------------------------------
# Language registry
# ---------------------------------------------------------------------------

_LANGUAGE_MAP: dict[str, Language] = {
    "javascript": Language(tree_sitter_javascript.language()),
    "typescript": Language(tree_sitter_typescript.language_typescript()),
    "tsx": Language(tree_sitter_typescript.language_tsx()),
}


def _resolve_language(language: str) -> Language:
    """Return the Tree-sitter Language for *language*.

    Raises `ValueError` when the language is not supported.
    """
    lang = _LANGUAGE_MAP.get(language)
    if lang is None:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported: {', '.join(sorted(_LANGUAGE_MAP))}"
        )
    return lang


# ---------------------------------------------------------------------------
# Parse result
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ParseResult:
    """Result of parsing a single source file.

    Attributes:
        tree: The raw Tree-sitter parse tree.  Callers may traverse it
            directly or use the helper methods on this class.
        source: The original source text (bytes).
        language: The language identifier that was used for parsing.
        file_path: Optional path of the file that was parsed.
    """

    tree: Tree
    source: bytes
    language: str
    file_path: Optional[str] = None

    @property
    def root_node(self) -> Node:
        """Convenience accessor for the root syntax node."""
        return self.tree.root_node

    def walk(self):
        """Return a Tree-sitter TreeCursor for depth-first traversal."""
        return self.tree.walk()

    def query(self, query_string: str) -> dict[str, list[Node]]:
        """Execute a Tree-sitter query against the parse tree.

        Returns a dictionary mapping capture names to lists of captured
        nodes.  Raises ``tree_sitter.QueryError`` if the query is malformed.
        """
        from tree_sitter import Query as _Query, QueryCursor as _QueryCursor
        lang = _resolve_language(self.language)
        q = _Query(lang, query_string)
        return _QueryCursor(q).captures(self.root_node)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_source(
    source: str,
    language: str,
    file_path: Optional[str] = None,
) -> ParseResult:
    """Parse *source* text using the Tree-sitter grammar for *language*.

    Parameters:
        source: The source code to parse (a Python string).
        language: One of ``"javascript"``, ``"typescript"``, or ``"tsx"``.
        file_path: Optional path used for reporting; not used for parsing.

    Returns:
        A `ParseResult` wrapping the raw Tree-sitter tree and the original
        source bytes.

    Raises:
        ValueError: If *language* is not supported.
        tree_sitter.LanguageError: If the grammar cannot be loaded (should
            not happen with the bundled grammars).
    """
    lang = _resolve_language(language)
    parser = Parser(lang)

    source_bytes = source.encode("utf-8")
    tree = parser.parse(source_bytes)

    return ParseResult(
        tree=tree,
        source=source_bytes,
        language=language,
        file_path=file_path,
    )
