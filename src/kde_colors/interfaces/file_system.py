"""
FileSystem interface that abstracts read-only file system operations.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


class FileSystemInterface(Protocol):
    """Abstract Read-only file system operations injector."""

    def read_file(self, path: str) -> str:
        """Read file contents as a string."""
        ...

    def write_text(self, path: Path | str, content: str) -> None:
        """Write text content to a file.

        Args:
            path: Path to the file to write to
            content: Text content to write to the file
        """
        ...

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
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

    def resolve_path(self, path: str) -> str:
        """Resolve a path to its absolute form."""
        ...

    def expand_path(self, path: str) -> str:
        """Expand user and environment variables in path."""
        ...

    def list_files(self, path: str) -> list[str]:
        """List files in a directory."""
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
