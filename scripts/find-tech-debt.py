#!/usr/bin/env python3
"""
Find technical debt markers (TODO, FIXME, TBD, etc.) in Python source files.

Usage:
    find-tech-debt.py [OPTIONS] [PATHS...]

Options:
    -m, --markers TEXT    Comma-separated list of markers to search for
                          (default: TODO,FIXME,TBD,HACK,BUG,WARNING,DEPRECATED)
    -h, --help            Show this message and exit.

PATHS can be either directories or individual Python files.
If no paths are provided, searches in 'src/' directory by default.

Exit status is 0 if no technical debt is found, 1 otherwise.
"""

from __future__ import annotations

import ast
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set, Pattern, cast
from typing_extensions import TypeAlias

# Default technical debt markers
DEFAULT_MARKERS = [
    'TODO', 'FIXME', 'TBD','HACK', 'BUG', 'WARNING', 'DEPRECATED'
]

# Set to keep track of processed files for duplicate checking
PROCESSED_FILES: Set[Path] = set()

# Global variable to store the marker pattern
tech_debt_pattern: Pattern[str] = re.compile('')  # Will be set in main()

# Global set to track processed lines to avoid duplicates
# Using a type alias for better readability
ProcessedLinesType = Set[Tuple[Path, int]]
processed_lines: ProcessedLinesType = set()

# Type aliases for better readability
LineInfo: TypeAlias = Tuple[Path, int]  # (filepath, line_number)
TechDebtItem: TypeAlias = Tuple[Path, int, str, str]  # (filepath, line_num, line_type, comment)

def find_python_files(directory: Path) -> List[Path]:
    """
    Recursively find all Python files in the given directory.

    Args:
        directory: Directory to search for Python files

    Returns:
        List of Path objects for all .py files found
    """
    return list(directory.glob("**/*.py"))


def is_comment(line: str) -> bool:
    """
    Check if a line is a comment.

    Args:
        line: Line of text to check

    Returns:
        True if the line starts with '#' after removing leading whitespace
    """
    stripped = line.lstrip()
    return stripped.startswith('#')

def find_tech_debt_comments(filepath: Path, processed_lines: Set[LineInfo]) -> List[Tuple[int, str, str]]:  # noqa: C901
    """
    Find technical debt markers in a Python file.

    Args:
        filepath: Path to the Python file to analyze
        processed_lines: Set of (filepath, line_num) tuples to track processed lines

    Returns:
        List of tuples containing (line_number, marker_type, comment)
    """
    results = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the file to get the AST
        tree = ast.parse(source, filename=str(filepath))

        # Track docstring line ranges and content
        docstring_info = []  # (start_line, end_line, content)

        # Process all nodes to find docstrings
        for node in ast.walk(tree):
            if not hasattr(node, 'body') or not node.body:
                continue

            # Get the docstring if it exists
            try:
                if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node, clean=False)
                    if docstring and hasattr(node, 'lineno'):
                        start_line = node.lineno
                        # Estimate end line (start_line + num_lines - 1)
                        end_line = start_line + len(docstring.split('\n')) - 1
                        docstring_info.append((start_line, end_line, docstring))
            except (TypeError, AttributeError):
                continue

        # Process the file line by line
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            if (filepath, line_num) in processed_lines:
                continue

            # Check if this line is in a docstring
            in_docstring = False
            docstring_content = ""
            for start, end, content in docstring_info:
                if start <= line_num <= end:
                    in_docstring = True
                    docstring_content = content
                    break

            # Check for comments (lines starting with #)
            is_comment_line = is_comment(line)

            # Only process comment lines or docstring lines
            if is_comment_line or in_docstring:
                # For docstrings, we need to extract the specific line
                if in_docstring:
                    doc_lines = docstring_content.split('\n')
                    doc_line_num = line_num - start
                    if 0 <= doc_line_num < len(doc_lines):
                        line_content = doc_lines[doc_line_num]
                    else:
                        line_content = line
                else:
                    # For regular comments, strip the comment character and leading whitespace
                    line_content = line.lstrip('#').lstrip()

                # Check for tech debt markers in this line
                match = tech_debt_pattern.search(line_content)
                if match:
                    marker = match.group(1).upper()
                    comment = match.group(2).strip()
                    line_type = "Docstring" if in_docstring else "Comment"

                    # Add to results
                    results.append((line_num, line_type, f"{marker}: {comment}"))
                    processed_lines.add((filepath, line_num))

    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)

    return results


def format_output(relative_path: Path, line_num: int, comment: str, max_width: int = 100) -> str:
    """
    Format a line of output with consistent alignment.

    Args:
        relative_path: Path to the file (will be shown relative to cwd)
        line_num: Line number where the technical debt was found
        comment: The technical debt comment text
        max_width: Maximum width of the output line

    Returns:
        Formatted string with file:line and comment aligned in columns
    """
    file_line = f"{relative_path}:{line_num}"
    if len(comment) > max_width - 40:  # Leave room for file:line and type
        comment = comment[:max_width - 43] + "..."
    return f"{file_line:<40} {comment}"


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments and find Python files.

    Returns:
        Tuple of (parsed_args, python_files) where parsed_args contains the command line
        arguments and python_files is a list of Path objects for all found Python files.
    """
    parser = argparse.ArgumentParser(description='Find technical debt in Python files.')
    parser.add_argument('paths', nargs='*', default=['src/'],
                        help='Files or directories to search (default: %(default)s)')
    parser.add_argument('-m', '--markers', default=','.join(DEFAULT_MARKERS),
                        help=f'Comma-separated list of markers to search for (default: {",".join(DEFAULT_MARKERS)})')

    args = parser.parse_args()
    return args

def get_python_files(paths: list[str]) -> list[Path]:
    """
    Find all Python files in the given paths.

    Args:
        paths: List of file or directory paths to search

    Returns:
        List of Path objects for all found Python files

    Note:
        Prints warnings to stderr for non-existent paths or directories
        without Python files.
    """
    python_files = []

    for path_str in paths:
        try:
            path = Path(path_str).resolve()

            # If it's a file and has a .py extension, add it directly
            if path.is_file() and path.suffix == '.py':
                python_files.append(path)
                continue

            # Otherwise treat as a directory
            if not path.exists():
                print(f"Warning: Path does not exist: {path}", file=sys.stderr)
                continue

            if not path.is_dir():
                print(f"Warning: Not a directory: {path}", file=sys.stderr)
                continue

            # Find Python files in the directory
            found_files = find_python_files(path)
            if not found_files:
                print(f"Warning: No Python files found in directory: {path}", file=sys.stderr)
            python_files.extend(found_files)

        except Exception as e:
            print(f"Error processing {path_str}: {e}", file=sys.stderr)

    return python_files


def main() -> None:
    """
    Main entry point for the technical debt finder.

    Scans Python files for technical debt markers, prints findings to stdout,
    and exits with status code 1 if any technical debt is found.
    """
    args = parse_args()

    # Clear processed files and lines from previous runs
    PROCESSED_FILES.clear()
    global processed_lines
    processed_lines.clear()

    # Set up the tech debt pattern with the specified markers
    global tech_debt_pattern

    # Get markers from args or use defaults
    markers_str = getattr(args, 'markers', '')
    marker_list = [m.strip() for m in markers_str.split(',') if m.strip()] if markers_str else DEFAULT_MARKERS

    # Create a regex pattern that matches any of the markers
    markers_pattern = '|'.join(re.escape(marker) for marker in marker_list)
    tech_debt_pattern = re.compile(
        fr'\b({markers_pattern})\b[\s:]*([^\n]*)',
        re.IGNORECASE
    )

    # Get Python files from the specified paths
    paths = getattr(args, 'paths', ['src/'])
    python_files = get_python_files(paths)

    if not python_files:
        print("No Python files found to process.", file=sys.stderr)
        print("Searched in:", ', '.join(f'"{p}"' for p in args.paths), file=sys.stderr)
        return

    # Process each file and collect results
    all_results: List[Tuple[Path, int, str, str]] = []
    cwd = Path.cwd()
    local_processed_lines: Set[Tuple[Path, int]] = set()

    for filepath in python_files:
        try:
            # Handle both file and directory paths
            if filepath.is_file():
                files_to_process = [filepath]
            else:
                files_to_process = find_python_files(filepath)

            for f in files_to_process:
                try:
                    relative_path = f.relative_to(cwd)
                except ValueError:
                    # If file is not relative to cwd, use absolute path
                    relative_path = f

                # Process the file and collect results
                results = find_tech_debt_comments(f, local_processed_lines)
                for line_num, line_type, comment in results:
                    all_results.append((relative_path, line_num, line_type, comment))

        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)

    # Sort results by file path and line number
    all_results.sort(key=lambda x: (str(x[0]).lower(), x[1]))

    # Print the results
    if all_results:
        print("-" * 120)
        print(f"{'File:Line':<40} {'Type':<10} {'Technical Debt'}")
        print("-" * 120)

        for filepath, line_num, line_type, comment in all_results:
            print(f"{str(filepath)}:{line_num:<4} {line_type + ':':<10} {comment}")
        print("-" * 120)

    # Print summary
    print(f"Found {len(all_results)} technical debt items in {len(set(r[0] for r in all_results))} Python files")
    print(f"Markers searched: {', '.join(marker_list)}")
    if all_results:
        print("-" * 120)

    # Exit with non-zero status if technical debt was found
    if len(all_results) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
