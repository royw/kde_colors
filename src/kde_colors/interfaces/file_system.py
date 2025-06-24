"""
File system interface module.

This module defines the FileSystemInterface protocol that establishes the contract
for file system operations used throughout the application. It serves as an abstraction
layer between the application logic and the actual file system implementation.

Why this interface exists:
- Decouples the application from direct file system dependencies
- Enables thorough unit testing using test doubles instead of real file system
- Provides a consistent API for file operations across the application
- Supports the dependency inversion principle of clean architecture

Implementations of this interface are responsible for:
- Reading and writing text files
- Checking if files or directories exist
- Creating directories
- Listing directory contents
- Finding files that match glob patterns
- Manipulating paths (absolute paths, joining paths, etc.)

The @runtime_checkable decorator allows runtime type checking of objects
that implement this protocol through isinstance() checks.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class FileSystemInterface(Protocol):
    """Abstract Read-only file system operations injector."""

    def read_file(self, path: str) -> str:
        """Read file contents as a string."""
        ...

    def read_text(self, path: Path | str) -> str:
        """Read text content from a file.

        Args:
            path: Path to the file

        Returns:
            The contents of the file as a string
        """
        ...

    def write_text(self, path: Path | str, content: str) -> None:
        """Write text content to a file.

        Args:
            path: Path to the file
            content: Text content to write
        """
        ...

    def write_stdout(self, content: str) -> None:
        """Write content to standard output.

        This abstraction allows for testing output without capturing stdout.

        Args:
            content: Text content to write to stdout
        """
        ...

    def exists(self, path: str) -> bool:
        """Check if a path exists (file or directory)."""
        ...

    def is_file(self, path: str) -> bool:
        """Check if a path is a file."""
        ...

    def is_dir(self, path: str) -> bool:
        """Check if a path is a directory."""
        ...

    def glob(self, pattern: str) -> list[str]:
        """Find paths matching a pattern."""
        ...

    def walk(self, path: str) -> Iterator[tuple[str, list[str], list[str]]]:
        """Walk a directory tree."""
        ...

    def list_dir(self, path: str) -> list[str]:
        """List all entries in a directory."""
        ...

    def home(self) -> Path:
        """Return the home directory."""
        ...

    def root(self) -> Path:
        """Return the root directory."""
        ...
