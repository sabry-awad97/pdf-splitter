"""Command-line interface for the PDF Splitter utility."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.traceback import install

from pdf_splitter.pdf_processor import PDFProcessor

# Install rich traceback handler
install()

# Create console for rich output
console = Console()


@click.group()
@click.version_option()
def cli():
    """PDF Splitter - A command-line utility for splitting PDF files."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory where split PDFs will be saved. Defaults to the same directory as the input file.",
)
@click.option(
    "-r",
    "--ranges",
    type=str,
    help="Page ranges to extract (e.g., '1-5,7,9-end'). Defaults to all pages.",
)
def split_by_range(input_file: Path, output_dir: Optional[Path], ranges: Optional[str]):
    """
    Split a PDF file based on specified page ranges.

    Examples:
        pdf-splitter split-by-range document.pdf --ranges 1-5,7,9-end
        pdf-splitter split-by-range document.pdf --ranges 1-5 --output-dir ./output
    """
    try:
        # Set default output directory if not provided
        if output_dir is None:
            output_dir = input_file.parent / "split_output"

        # Get PDF information
        console.print(f"Reading PDF: [bold]{input_file}[/bold]")
        pdf_info = PDFProcessor.get_pdf_info(input_file)
        total_pages = pdf_info["pages"]
        
        console.print(f"Total pages: [bold]{total_pages}[/bold]")
        
        if pdf_info["is_encrypted"]:
            if pdf_info["can_be_decrypted"]:
                console.print("[yellow]PDF is encrypted but can be processed[/yellow]")
            else:
                console.print("[red]PDF is encrypted and cannot be processed[/red]")
                return 1

        # Parse page ranges
        try:
            page_ranges = PDFProcessor.parse_page_ranges(ranges, total_pages)
        except ValueError as e:
            console.print(f"[red]Error parsing page ranges: {e}[/red]")
            return 1

        # Calculate total operations for progress bar
        total_operations = sum(end - start + 1 for start, end in page_ranges)
        
        # Display the ranges to be processed
        range_display = []
        for start, end in page_ranges:
            if start == end:
                range_display.append(f"{start}")
            else:
                end_str = str(end) if end != float('inf') else "end"
                range_display.append(f"{start}-{end_str}")
        
        console.print(f"Processing ranges: [bold]{', '.join(range_display)}[/bold]")
        console.print(f"Output directory: [bold]{output_dir}[/bold]")

        # Process the PDF with a progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Splitting PDF...", total=total_operations)

            def update_progress():
                progress.update(task, advance=1)

            created_files = PDFProcessor.split_by_range(
                input_file, output_dir, page_ranges, update_progress
            )

        # Display results
        console.print(f"[green]Successfully created {len(created_files)} file(s):[/green]")
        for file_path in created_files:
            console.print(f"  - {file_path}")

        return 0

    except Exception as e:
        console.print(Panel(
            Syntax(str(e), "python", theme="monokai", line_numbers=True),
            title="[red]Error[/red]",
            border_style="red",
        ))
        return 1


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory where split PDFs will be saved. Defaults to the same directory as the input file.",
)
@click.option(
    "-n",
    "--pages-per-file",
    type=int,
    required=True,
    help="Number of pages per output file.",
)
def split_by_count(input_file: Path, output_dir: Optional[Path], pages_per_file: int):
    """
    Split a PDF file into multiple files with a fixed number of pages per file.

    Examples:
        pdf-splitter split-by-count document.pdf --pages-per-file 5
        pdf-splitter split-by-count document.pdf -n 10 --output-dir ./output
    """
    try:
        # Validate pages_per_file
        if pages_per_file <= 0:
            console.print("[red]Error: Pages per file must be a positive integer[/red]")
            return 1

        # Set default output directory if not provided
        if output_dir is None:
            output_dir = input_file.parent / "split_output"

        # Get PDF information
        console.print(f"Reading PDF: [bold]{input_file}[/bold]")
        pdf_info = PDFProcessor.get_pdf_info(input_file)
        total_pages = pdf_info["pages"]
        
        console.print(f"Total pages: [bold]{total_pages}[/bold]")
        
        if pdf_info["is_encrypted"]:
            if pdf_info["can_be_decrypted"]:
                console.print("[yellow]PDF is encrypted but can be processed[/yellow]")
            else:
                console.print("[red]PDF is encrypted and cannot be processed[/red]")
                return 1

        # Calculate number of output files
        num_files = (total_pages + pages_per_file - 1) // pages_per_file
        
        console.print(f"Pages per file: [bold]{pages_per_file}[/bold]")
        console.print(f"Expected output files: [bold]{num_files}[/bold]")
        console.print(f"Output directory: [bold]{output_dir}[/bold]")

        # Process the PDF with a progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Splitting PDF...", total=total_pages)

            def update_progress():
                progress.update(task, advance=1)

            created_files = PDFProcessor.split_by_count(
                input_file, output_dir, pages_per_file, update_progress
            )

        # Display results
        console.print(f"[green]Successfully created {len(created_files)} file(s):[/green]")
        for file_path in created_files:
            console.print(f"  - {file_path}")

        return 0

    except Exception as e:
        console.print(Panel(
            Syntax(str(e), "python", theme="monokai", line_numbers=True),
            title="[red]Error[/red]",
            border_style="red",
        ))
        return 1


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def info(input_file: Path):
    """
    Display information about a PDF file.

    Example:
        pdf-splitter info document.pdf
    """
    try:
        console.print(f"Reading PDF: [bold]{input_file}[/bold]")
        pdf_info = PDFProcessor.get_pdf_info(input_file)
        
        # Display PDF information
        console.print(Panel(
            f"Filename: [bold]{pdf_info['filename']}[/bold]\n"
            f"Path: {pdf_info['path']}\n"
            f"Pages: [bold]{pdf_info['pages']}[/bold]\n"
            f"Encrypted: [{'red' if pdf_info['is_encrypted'] else 'green'}]"
            f"{pdf_info['is_encrypted']}[/{'red' if pdf_info['is_encrypted'] else 'green'}]"
            + (" (can be decrypted)" if pdf_info['is_encrypted'] and pdf_info['can_be_decrypted'] else ""),
            title="PDF Information",
            border_style="blue",
        ))
        
        return 0
        
    except Exception as e:
        console.print(Panel(
            Syntax(str(e), "python", theme="monokai", line_numbers=True),
            title="[red]Error[/red]",
            border_style="red",
        ))
        return 1


def main():
    """Entry point for the PDF Splitter CLI."""
    sys.exit(cli())
