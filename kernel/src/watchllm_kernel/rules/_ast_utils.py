"""Shared AST utility layer for WatchLLM kernel rules.

Provides the common tree-sitter helpers that were previously duplicated
across ``secrets.py``, ``forbidden_imports.py``, ``auth_flow.py``, and
``boundary.py``.  All rule modules should import from here instead of
maintaining their own copies.

Functions:
    infer_language_from_path: Map a file extension to a parser language id.
    parse_to_tree:            Parse source text and return (root_node, source_bytes).
    node_text:                Extract UTF-8 decoded text for a tree-sitter node.
    location_from_node:       Convert a tree-sitter node position to a 1-based SourceLocation.
    strip_quotes:             Remove surrounding single/double quotes from a string.
"""

from __future__ import annotations

from watchllm_kernel.models import SourceLocation
from watchllm_kernel.parser import ParseResult, parse_source


# ---------------------------------------------------------------------------
# Language inference
# ---------------------------------------------------------------------------


def infer_language_from_path(file_path: str | None) -> str:
    """Infer a tree-sitter language identifier from *file_path*.

    Returns ``"javascript"`` when the extension is unrecognised or absent.
    """
    if not file_path:
        return "javascript"
    lower = file_path.lower()
    if lower.endswith(".tsx"):
        return "tsx"
    if lower.endswith(".ts"):
        return "typescript"
    return "javascript"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def ensure_parse_result(
    source: str,
    file_path: str | None = None,
    parse_result: ParseResult | None = None,
) -> ParseResult:
    """Return an existing *parse_result* or create one from *source*.

    If a ``ParseResult`` is already available (e.g. provided by the engine),
    it is returned directly — avoiding a redundant parse.  Otherwise
    ``parse_source`` is called with the language inferred from *file_path*.
    """
    if parse_result is not None:
        return parse_result
    language = infer_language_from_path(file_path)
    return parse_source(source, language=language, file_path=file_path)


# ---------------------------------------------------------------------------
# Node helpers
# ---------------------------------------------------------------------------


def node_text(source_bytes: bytes, node) -> str:
    """Return the UTF-8 decoded source text for *node*."""
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8")


def location_from_node(node) -> SourceLocation:
    """Convert a tree-sitter node position to a 1-based ``SourceLocation``."""
    start_line, start_col = node.start_point
    end_line, end_col = node.end_point
    return SourceLocation(
        line=start_line + 1,
        column=start_col + 1,
        end_line=end_line + 1,
        end_column=end_col + 1,
    )


def strip_quotes(text: str) -> str:
    """Remove surrounding single or double quotes from *text*.

    Returns *text* unchanged if it is not quoted.
    """
    if len(text) >= 2:
        if (text[0] == '"' and text[-1] == '"') or (
            text[0] == "'" and text[-1] == "'"
        ):
            return text[1:-1]
    return text
