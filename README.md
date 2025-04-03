# PDF Splitter

A command-line utility for splitting PDF files based on page ranges, individual pages, and fixed page counts.

## Features

- Split PDFs by page ranges (e.g., "1-5,7,9-end")
- Split PDFs into multiple files with a fixed number of pages per file
- Display information about PDF files
- Progress bar for tracking splitting operations
- Handles encrypted PDFs (attempts to remove password)
- Consistent output file naming convention

## Installation

```bash
# Clone the repository
git clone https://github.com/sabry-awad97/pdf-splitter.git
cd pdf-splitter

# Install the package
pip install -e .
```

## Usage

### Split by Page Ranges

```bash
# Split a PDF file based on specified page ranges
pdf-splitter split-by-range document.pdf --ranges 1-5,7,9-end

# Specify an output directory
pdf-splitter split-by-range document.pdf --ranges 1-5 --output-dir ./output
```

### Split by Page Count

```bash
# Split a PDF file into multiple files with 5 pages per file
pdf-splitter split-by-count document.pdf --pages-per-file 5

# Specify an output directory
pdf-splitter split-by-count document.pdf -n 10 --output-dir ./output
```

### Display PDF Information

```bash
# Display information about a PDF file
pdf-splitter info document.pdf
```

### Help

```bash
# Display general help
pdf-splitter --help

# Display help for a specific command
pdf-splitter split-by-range --help
```

## Output File Naming

Output files follow the naming convention: `original_filename_pages_X-Y.pdf`, where `X` and `Y` are the start and end page numbers.

## Requirements

- Python 3.8 or higher
- click
- rich
- PyPDF2

## License

MIT
