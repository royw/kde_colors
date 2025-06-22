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

    def write_text(self, path: Path | str, content: str) -> None:
        """
        Write text content to a file.

        Args:
            path: Path to the file to write to
            content: Text content to write to the file

        Raises:
            FileNotFoundError: If the parent directory does not exist
            PermissionError: If the file cannot be written due to permissions
        """
        # Convert to Path if it's a string
        if isinstance(path, str):
            path = Path(path)

        # Write the content
        path.write_text(content, encoding="utf-8")

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if the path exists and is a file, False otherwise
        """
        return Path(path).is_file()

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
            path: Root path to start walking from

        Returns:
            Iterator yielding tuples of (dirpath, dirnames, filenames)
        """
        return os.walk(path)

    def resolve_path(self, path: str) -> str:
        """
        Resolve a path to its absolute form.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute path
        """
        return str(Path(path).resolve())

    def expand_path(self, path: str) -> str:
        """
        Expand user and environment variables in path.

        Args:
            path: Path to expand

        Returns:
            Expanded path
        """
        # Handle environment variables first
        expanded = os.path.expandvars(path)
        # Then expand user directory
        return str(Path(expanded).expanduser())

    def list_files(self, path: str) -> list[str]:
        """
        List files in a directory.

        Args:
            path: Directory to list files from

        Returns:
            List of filenames in the directory
        """
        path_obj = Path(path)
        return [p.name for p in path_obj.iterdir() if p.is_file()]

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
