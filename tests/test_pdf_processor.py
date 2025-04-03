"""Tests for the PDF processor module."""

import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from pdf_splitter.pdf_processor import PDFProcessor


class TestPDFProcessor(unittest.TestCase):
    """Test cases for the PDFProcessor class."""

    def test_parse_page_ranges(self):
        """Test parsing of page range strings."""
        # Test single page
        self.assertEqual(PDFProcessor.parse_page_ranges("5", 10), [(5, 5)])
        
        # Test simple range
        self.assertEqual(PDFProcessor.parse_page_ranges("1-5", 10), [(1, 5)])
        
        # Test multiple ranges
        self.assertEqual(
            PDFProcessor.parse_page_ranges("1-3,5,7-9", 10),
            [(1, 3), (5, 5), (7, 9)]
        )
        
        # Test range with "end"
        ranges = PDFProcessor.parse_page_ranges("1-3,5-end", 10)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0], (1, 3))
        self.assertEqual(ranges[1][0], 5)
        self.assertEqual(ranges[1][1], float('inf'))
        
        # Test empty string (default to all pages)
        self.assertEqual(PDFProcessor.parse_page_ranges("", 10), [(1, 10)])

    @patch('pdf_splitter.pdf_processor.PdfReader')
    @patch('pdf_splitter.pdf_processor.PdfWriter')
    def test_split_by_range(self, mock_writer_class, mock_reader_class):
        """Test splitting PDF by page ranges."""
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(10)]
        mock_reader.is_encrypted = False
        mock_reader_class.return_value = mock_reader
        
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path("test.pdf")
            output_dir = Path(temp_dir)
            page_ranges = [(1, 3), (5, 7)]
            
            # Mock open to avoid actually writing files
            with patch('builtins.open'):
                result = PDFProcessor.split_by_range(input_file, output_dir, page_ranges)
            
            # Verify results
            self.assertEqual(len(result), 2)
            self.assertTrue(str(result[0]).endswith("test_pages_1-3.pdf"))
            self.assertTrue(str(result[1]).endswith("test_pages_5-7.pdf"))
            
            # Verify writer.add_page was called with correct pages
            self.assertEqual(mock_writer.add_page.call_count, 6)  # 3 pages + 3 pages

    @patch('pdf_splitter.pdf_processor.PdfReader')
    def test_get_pdf_info(self, mock_reader_class):
        """Test getting PDF information."""
        # Setup mock
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(5)]
        mock_reader.is_encrypted = False
        mock_reader.metadata = {"Title": "Test PDF"}
        mock_reader_class.return_value = mock_reader
        
        # Test
        pdf_path = Path("test.pdf")
        result = PDFProcessor.get_pdf_info(pdf_path)
        
        # Verify results
        self.assertEqual(result["path"], pdf_path)
        self.assertEqual(result["filename"], "test.pdf")
        self.assertEqual(result["pages"], 5)
        self.assertEqual(result["is_encrypted"], False)
        self.assertEqual(result["metadata"], {"Title": "Test PDF"})


if __name__ == "__main__":
    unittest.main()
