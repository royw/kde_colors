"""
File system service implementation for FileSystemInterface.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from kde_colors.interfaces.file_system import FileSystemInterface


class StdFileSystem(FileSystemInterface):
    """
    Implementation of FileSystemInterface providing file system operations.

    This service handles all interactions with the file system in a testable way,
    providing read-only operations to access files and directories.
    """

    def __init__(self) -> None:
        """Initialize the file system implementation."""

    def read_file(self, path: str) -> str:
        """
        Read file contents as a string.

        Args:
            path: Path to the file

        Returns:
            The contents of the file as a string

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read due to permissions
        """
        return Path(path).read_text(encoding="utf-8")

    def read_text(self, path: Path | str) -> str:
        """
        Read text content from a file.

        Args:
            path: Path to the file

        Returns:
            The contents of the file as a string

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read due to permissions
        """
        # Convert to Path if it's a string
        file_path = Path(path) if isinstance(path, str) else path
        return file_path.read_text(encoding="utf-8")

    def write_text(self, path: Path | str, content: str) -> None:
        """
        Write text content to a file.

        Args:
            path: Path to the file to write to
            content: Text content to write to the file

        Raises:
            OSError: If there is an error writing to the file
        """
        # Ensure the directory exists
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        path.write_text(content, encoding="utf-8")

    def write_stdout(self, content: str) -> None:
        """
        Write content to standard output.

        Args:
            content: Text content to write to stdout
        """
        print(content)

    def exists(self, path: str) -> bool:
        """
        Check if a path exists (file or directory).

        Args:
            path: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        return Path(path).exists()

    def is_file(self, path: str) -> bool:
        """
        Check if a path is a file.

        Args:
            path: Path to check

        Returns:
            True if the path is a file, False otherwise
        """
        return Path(path).is_file()

    def is_dir(self, path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check

        Returns:
            True if the path is a directory, False otherwise
        """
        return Path(path).is_dir()

    def glob(self, pattern: str) -> list[str]:
        """
        Find paths matching a pattern.

        Args:
            pattern: Glob pattern to match

        Returns:
            List of paths that match the pattern
        """
        # Extract the directory part and pattern part
        path_obj = Path(pattern)
        if "*" in path_obj.name or "?" in path_obj.name:
            # If the pattern is in the basename
            return [str(p) for p in path_obj.parent.glob(path_obj.name)]
        # If no pattern in basename, just glob the entire thing
        return [str(p) for p in Path().glob(pattern)]

    def walk(self, path: str) -> Iterator[tuple[str, list[str], list[str]]]:
        """
        Walk a directory tree.

        Args:
            path: Path to the directory to walk

        Returns:
            Iterator over (dirpath, dirnames, filenames)
        """
        return os.walk(path)

    def list_dir(self, path: str) -> list[str]:
        """
        List all entries in a directory.

        Args:
            path: Directory to list entries from

        Returns:
            List of all entries in the directory
        """
        return [p.name for p in Path(path).iterdir()]

    def home(self) -> Path:
        """
        Return the home directory.

        Returns:
            Path to the user's home directory
        """
        return Path.home()

    def root(self) -> Path:
        """
        Return the root directory.

        Returns:
            Path to the root directory (/ on Unix)
        """
        return Path("/")
