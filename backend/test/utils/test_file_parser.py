"""Tests for the file parser service."""

import pytest

from services.file_parser import (
    ExcelParser,
    ImageParser,
    PDFParser,
    TextParser,
    WordParser,
    get_parser,
)


def test_get_parser_word():
    """Verify docx MIME type returns WordParser."""
    parser = get_parser(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert isinstance(parser, WordParser)

    parser = get_parser("application/msword")
    assert isinstance(parser, WordParser)


def test_get_parser_pdf():
    """Verify PDF MIME type returns PDFParser."""
    parser = get_parser("application/pdf")
    assert isinstance(parser, PDFParser)


def test_get_parser_text():
    """Verify text/plain returns TextParser."""
    parser = get_parser("text/plain")
    assert isinstance(parser, TextParser)

    parser = get_parser("text/markdown")
    assert isinstance(parser, TextParser)


def test_get_parser_unknown():
    """Verify unsupported type returns None."""
    parser = get_parser("application/unknown")
    assert parser is None
