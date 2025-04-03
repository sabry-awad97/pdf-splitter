"""Tests for the CLI module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from pdf_splitter.cli import cli


class TestCLI(unittest.TestCase):
    """Test cases for the CLI interface."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test the CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("PDF Splitter", result.output)

    @patch("pdf_splitter.cli.PDFProcessor")
    def test_split_by_range(self, mock_processor):
        """Test the split-by-range command."""
        # Setup mocks
        mock_processor.get_pdf_info.return_value = {
            "path": Path("test.pdf"),
            "filename": "test.pdf",
            "pages": 10,
            "is_encrypted": False,
            "can_be_decrypted": False,
            "metadata": None,
        }
        mock_processor.parse_page_ranges.return_value = [(1, 5)]
        mock_processor.split_by_range.return_value = [Path("output/test_pages_1-5.pdf")]

        # Run command
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            result = self.runner.invoke(
                cli, ["split-by-range", temp_file.name, "--ranges", "1-5"]
            )

            # Verify results
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Successfully created", result.output)
            self.assertIn("1", result.output)
            self.assertIn("file", result.output)

            # Verify mock calls
            mock_processor.get_pdf_info.assert_called_once()
            mock_processor.parse_page_ranges.assert_called_once()
            mock_processor.split_by_range.assert_called_once()

    @patch("pdf_splitter.cli.PDFProcessor")
    def test_split_by_count(self, mock_processor):
        """Test the split-by-count command."""
        # Setup mocks
        mock_processor.get_pdf_info.return_value = {
            "path": Path("test.pdf"),
            "filename": "test.pdf",
            "pages": 10,
            "is_encrypted": False,
            "can_be_decrypted": False,
            "metadata": None,
        }
        mock_processor.split_by_count.return_value = [
            Path("output/test_pages_1-5.pdf"),
            Path("output/test_pages_6-10.pdf"),
        ]

        # Run command
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            result = self.runner.invoke(
                cli, ["split-by-count", temp_file.name, "--pages-per-file", "5"]
            )

            # Verify results
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Successfully created", result.output)
            self.assertIn("2", result.output)
            self.assertIn("file", result.output)

            # Verify mock calls
            mock_processor.get_pdf_info.assert_called_once()
            mock_processor.split_by_count.assert_called_once()

    @patch("pdf_splitter.cli.PDFProcessor")
    def test_info(self, mock_processor):
        """Test the info command."""
        # Setup mocks
        mock_processor.get_pdf_info.return_value = {
            "path": Path("test.pdf"),
            "filename": "test.pdf",
            "pages": 10,
            "is_encrypted": False,
            "can_be_decrypted": False,
            "metadata": None,
        }

        # Run command
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            result = self.runner.invoke(cli, ["info", temp_file.name])

            # Verify results
            self.assertEqual(result.exit_code, 0)
            self.assertIn("PDF Information", result.output)
            self.assertIn("Pages", result.output)
            self.assertIn("10", result.output)

            # Verify mock calls
            mock_processor.get_pdf_info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
