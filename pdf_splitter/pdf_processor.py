"""Core PDF processing functionality for the PDF Splitter utility."""

from pathlib import Path
from typing import List, Tuple

from PyPDF2 import PdfReader, PdfWriter


class PDFProcessor:
    """Handles PDF processing operations including splitting and validation."""

    @staticmethod
    def split_by_range(
        input_file: Path,
        output_dir: Path,
        page_ranges: List[Tuple[int, int]],
        progress_callback=None,
    ) -> List[Path]:
        """
        Split a PDF file based on specified page ranges.

        Args:
            input_file: Path to the input PDF file
            output_dir: Directory where split PDFs will be saved
            page_ranges: List of tuples representing page ranges (1-indexed)
            progress_callback: Optional callback for progress reporting

        Returns:
            List of paths to the created PDF files
        """
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create reader object
        try:
            reader = PdfReader(input_file)
        except Exception as e:
            raise ValueError(f"Failed to open PDF file: {e}")

        # Check if PDF is encrypted
        if reader.is_encrypted:
            try:
                # Try to decrypt with empty password
                reader.decrypt("")
            except Exception:
                raise ValueError("Cannot process encrypted PDF. Password removal failed.")

        total_pages = len(reader.pages)
        created_files = []

        # Process each page range
        for i, (start, end) in enumerate(page_ranges):
            # Adjust for 0-indexed pages in PyPDF2
            start_idx = start - 1
            # Handle 'end' as the last page
            end_idx = end - 1 if end != float('inf') else total_pages - 1

            # Validate page range
            if start_idx < 0 or end_idx >= total_pages or start_idx > end_idx:
                raise ValueError(
                    f"Invalid page range {start}-{end if end != float('inf') else 'end'} "
                    f"for a PDF with {total_pages} pages"
                )

            # Create writer object
            writer = PdfWriter()

            # Add pages to writer
            for page_idx in range(start_idx, end_idx + 1):
                writer.add_page(reader.pages[page_idx])
                if progress_callback:
                    progress_callback()

            # Generate output filename
            range_str = f"{start}-{end}" if end != float('inf') else f"{start}-{total_pages}"
            output_filename = f"{input_file.stem}_pages_{range_str}{input_file.suffix}"
            output_path = output_dir / output_filename

            # Write the output file
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            created_files.append(output_path)

        return created_files

    @staticmethod
    def parse_page_ranges(range_str: str, total_pages: int) -> List[Tuple[int, int]]:
        """
        Parse a page range string into a list of (start, end) tuples.

        Args:
            range_str: String representing page ranges (e.g., "1-5, 7, 9-end")
            total_pages: Total number of pages in the PDF

        Returns:
            List of tuples representing page ranges
        """
        if not range_str:
            # Default to all pages if no range is specified
            return [(1, total_pages)]

        page_ranges = []
        parts = [p.strip() for p in range_str.split(",")]

        for part in parts:
            if "-" in part:
                # Handle range like "1-5" or "9-end"
                start_str, end_str = part.split("-", 1)
                start = int(start_str)

                if end_str.lower() == "end":
                    end = float('inf')  # Will be replaced with total_pages later
                else:
                    end = int(end_str)

                page_ranges.append((start, end))
            else:
                # Handle single page like "7"
                page = int(part)
                page_ranges.append((page, page))

        return page_ranges

    @staticmethod
    def split_by_count(
        input_file: Path,
        output_dir: Path,
        pages_per_file: int,
        progress_callback=None,
    ) -> List[Path]:
        """
        Split a PDF file into multiple files with a fixed number of pages per file.

        Args:
            input_file: Path to the input PDF file
            output_dir: Directory where split PDFs will be saved
            pages_per_file: Number of pages per output file
            progress_callback: Optional callback for progress reporting

        Returns:
            List of paths to the created PDF files
        """
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create reader object
        try:
            reader = PdfReader(input_file)
        except Exception as e:
            raise ValueError(f"Failed to open PDF file: {e}")

        # Check if PDF is encrypted
        if reader.is_encrypted:
            try:
                # Try to decrypt with empty password
                reader.decrypt("")
            except Exception:
                raise ValueError("Cannot process encrypted PDF. Password removal failed.")

        total_pages = len(reader.pages)
        created_files = []

        # Calculate number of output files
        num_files = (total_pages + pages_per_file - 1) // pages_per_file

        for file_idx in range(num_files):
            # Calculate page range for this file
            start_idx = file_idx * pages_per_file
            end_idx = min(start_idx + pages_per_file, total_pages)

            # Create writer object
            writer = PdfWriter()

            # Add pages to writer
            for page_idx in range(start_idx, end_idx):
                writer.add_page(reader.pages[page_idx])
                if progress_callback:
                    progress_callback()

            # Generate output filename (1-indexed for user-facing names)
            start_page = start_idx + 1
            end_page = end_idx
            output_filename = f"{input_file.stem}_pages_{start_page}-{end_page}{input_file.suffix}"
            output_path = output_dir / output_filename

            # Write the output file
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            created_files.append(output_path)

        return created_files

    @staticmethod
    def get_pdf_info(pdf_path: Path) -> dict:
        """
        Get information about a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing PDF information
        """
        try:
            reader = PdfReader(pdf_path)
            
            # Check if PDF is encrypted
            is_encrypted = reader.is_encrypted
            can_be_decrypted = False
            
            if is_encrypted:
                try:
                    # Try to decrypt with empty password
                    can_be_decrypted = reader.decrypt("")
                except Exception:
                    pass
            
            return {
                "path": pdf_path,
                "filename": pdf_path.name,
                "pages": len(reader.pages),
                "is_encrypted": is_encrypted,
                "can_be_decrypted": can_be_decrypted,
                "metadata": reader.metadata if hasattr(reader, "metadata") else None
            }
        except Exception as e:
            raise ValueError(f"Failed to get PDF information: {e}")
