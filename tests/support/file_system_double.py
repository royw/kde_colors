"""
File system test double that implements the FileSystemInterface
and adds write operations for testing.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from fnmatch import fnmatch
from pathlib import Path

from kde_colors.interfaces.file_system import FileSystemInterface


class FileSystemDouble(FileSystemInterface):
    """
    Mock implementation of the FileSystemInterface for testing.

    Adds write operations to enable test setup and verification.
    """

    def __init__(self, root_dir: str | Path | None = None):
        """
        Initialize the file system double.

        Args:
            root_dir: Optional root directory for relative paths
        """
        self._root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.stdout_capture = ""  # To capture stdout content for testing
        self._in_memory_files: dict[str, str] = {}
        self._directories: set[str] = {str(self._root_dir)}

    def _resolve_path(self, path: str | Path) -> Path:
        """
        Convert path to absolute path if it's not already.

        Args:
            path: Path to resolve

        Returns:
            Absolute Path object
        """
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self._root_dir / path_obj
        return path_obj

    def read_file(self, path: str) -> str:
        """
        Read a file from the mock filesystem.

        Args:
            path: The path to the file to read

        Returns:
            The contents of the file as a string

        Raises:
            FileNotFoundError: If the file does not exist
        """
        path_obj = self._resolve_path(path)
        path_str = str(path_obj)

        # Check if it's in our in-memory files first
        if path_str in self._in_memory_files:
            return self._in_memory_files[path_str]

        # If not in memory, try to read from the real filesystem
        try:
            with path_obj.open(encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as e:
            error_msg = f"File not found: {path_str}"
            raise FileNotFoundError(error_msg) from e

    def read_text(self, path: Path | str) -> str:
        """Read text from a file in the mock filesystem.

        Args:
            path: Path to the file to read

        Returns:
            The contents of the file as a string

        Raises:
            FileNotFoundError: If the file does not exist
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_str = str(path_obj)

        # Check if it's in our in-memory files first
        if path_str in self._in_memory_files:
            return self._in_memory_files[path_str]

        # If not in memory, try to read from the real filesystem
        try:
            with path_obj.open(encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as e:
            error_msg = f"File not found: {path_str}"
            raise FileNotFoundError(error_msg) from e

    def write_text(self, path: Path | str, content: str) -> None:
        """Write text to a file in the mock filesystem.

        Args:
            path: Path to the file
            content: Text content to write to the file
        """
        # Use _resolve_path to get an absolute Path object
        path_obj = self._resolve_path(path)
        path_str = str(path_obj)

        # Ensure parent directory exists
        parent_path = path_obj.parent
        parent_str = str(parent_path)
        if parent_str and not self.is_dir(parent_str):
            self.mkdir(parent_str)

        self._in_memory_files[path_str] = content

    def write_stdout(self, content: str) -> None:
        """Capture content meant for stdout in the stdout_capture attribute.

        Args:
            content: Text content meant for stdout
        """
        self.stdout_capture += content

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if the path exists and is a file, False otherwise
        """
        path_str = str(self._resolve_path(path))
        return path_str in self._in_memory_files or Path(path_str).is_file()

    def exists(self, path: str) -> bool:
        """
        Check if a path exists (file or directory).

        Args:
            path: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        path_str = str(self._resolve_path(path))
        return path_str in self._in_memory_files or path_str in self._directories or Path(path_str).exists()

    def is_file(self, path: str) -> bool:
        """
        Check if a path is a file.

        Args:
            path: Path to check

        Returns:
            True if the path is a file, False otherwise
        """
        path_str = str(self._resolve_path(path))
        return path_str in self._in_memory_files or Path(path_str).is_file()

    def is_dir(self, path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check

        Returns:
            True if the path is a directory, False otherwise
        """
        path_str = str(self._resolve_path(path))
        return path_str in self._directories or Path(path_str).is_dir()

    def glob(self, pattern: str) -> list[str]:
        """
        Find paths matching a pattern.

        Args:
            pattern: The pattern to match

        Returns:
            A list of paths that match the pattern
        """
        # Handle different pattern types
        pattern_path = Path(pattern)
        pattern_is_relative = str(pattern_path.parent) == "."

        # Determine the base path to search from
        base_path = self._root_dir if pattern_is_relative else self._resolve_path(str(pattern_path.parent))
        base_path_obj = Path(base_path)

        # Get files from real filesystem if the base path exists
        real_files = []
        if base_path_obj.exists() and base_path_obj.is_dir():
            # For simple patterns like '*.txt', don't search recursively
            real_files = [str(p) for p in base_path_obj.glob(pattern_path.name)]

        # Get matching in-memory files
        in_memory_matches = []
        for path in self._in_memory_files:
            path_obj = Path(path)

            if pattern_is_relative:
                # For patterns without directory components (like *.txt),
                # only consider files in the base directory
                if path_obj.parent == base_path_obj and fnmatch(path_obj.name, pattern_path.name):
                    in_memory_matches.append(path)
            else:
                # For patterns with directory components (like subdir/*.txt)
                # Check if the path's parent matches the pattern's parent
                pattern_parent = str(pattern_path.parent)
                path_parent = str(path_obj.parent)

                # Handle both absolute and relative paths
                if pattern_parent.startswith("/"):
                    # Absolute pattern path
                    if path_parent == pattern_parent and fnmatch(path_obj.name, pattern_path.name):
                        in_memory_matches.append(path)
                else:
                    # Relative pattern path (e.g., 'subdir/*.txt')
                    # Check if the path ends with the pattern parent
                    target_dir = Path(self._root_dir) / pattern_parent
                    if path_obj.parent == target_dir and fnmatch(path_obj.name, pattern_path.name):
                        in_memory_matches.append(path)

        return list(set(real_files + in_memory_matches))

    def _matches_glob(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a glob pattern.

        Args:
            path: The path to check
            pattern: The pattern to match

        Returns:
            True if the path matches the pattern, False otherwise
        """
        # Handle patterns with directory parts (e.g., subdir/*.txt)
        pattern_path = Path(pattern)
        path_obj = Path(path)

        # If pattern has a parent, make sure it matches the path's parent
        if str(pattern_path.parent) != ".":
            if not fnmatch(str(path_obj.parent), str(pattern_path.parent)):
                return False
            # Match just the filename part against the pattern name
            return fnmatch(path_obj.name, pattern_path.name)

        # For simple patterns like *.txt, only match files in the current directory
        # not in subdirectories
        if "/" not in pattern and "/" in path:
            return False

        # Otherwise use basic fnmatch
        return fnmatch(path, pattern)

    def walk(self, path: str) -> Iterator[tuple[str, list[str], list[str]]]:
        """
        Walk a directory tree.

        Args:
            path: The root directory to walk

        Yields:
            A tuple of (dirpath, dirnames, filenames)
        """
        real_path = str(self._resolve_path(path))

        # If the path isn't a real directory, use our in-memory structure
        if not Path(real_path).is_dir() and real_path in self._directories:
            # Find all direct child directories
            child_dirs = [Path(d).name for d in self._directories if Path(d).parent == Path(real_path)]

            # Find all direct child files
            child_files = [Path(f).name for f in self._in_memory_files if Path(f).parent == Path(real_path)]

            yield real_path, child_dirs, child_files

            # Recursively walk child directories
            for child_dir in child_dirs:
                child_path = Path(real_path) / child_dir
                yield from self.walk(str(child_path))
        else:
            # Fall back to os.walk for real directories
            for dirpath, dirnames, filenames in os.walk(real_path):
                # Add any in-memory files for this directory
                in_memory_files = [Path(f).name for f in self._in_memory_files if Path(f).parent == Path(dirpath)]

                yield dirpath, dirnames, list(set(filenames + in_memory_files))

    def resolve_path(self, path: str) -> str:
        """
        Resolve a path to its absolute form.

        Args:
            path: Path to resolve

        Returns:
            The absolute path as a string
        """
        return str(self._resolve_path(path))

    def expand_path(self, path: str) -> str:
        """
        Expand user and environment variables in path.

        Args:
            path: Path with variables to expand

        Returns:
            Path with expanded variables
        """
        return Path(os.path.expandvars(path)).expanduser().as_posix()

    def list_files(self, path: str) -> list[str]:
        """
        List files in a directory.

        Args:
            path: Directory to list files from

        Returns:
            List of file paths in the directory

        Raises:
            FileNotFoundError: If the directory doesn't exist
            NotADirectoryError: If the path is not a directory
        """
        real_path = self._resolve_path(path)

        if not self.exists(str(real_path)):
            error_msg = "Directory not found: " + str(path)
            raise FileNotFoundError(error_msg)

        if not self.is_dir(str(real_path)):
            error_msg = "Not a directory: " + str(path)
            raise NotADirectoryError(error_msg)

        # Get real files first
        files = []
        if real_path.exists() and real_path.is_dir():
            files = [str(p) for p in real_path.iterdir() if p.is_file()]

        # Add in-memory files
        in_memory_files = [p for p in self._in_memory_files if Path(p).parent == real_path]

        return list(set(files + in_memory_files))

    def list_dir(self, path: str) -> list[str]:
        """
        List all entries in a directory.

        Args:
            path: Directory to list

        Returns:
            List of basenames (filenames/dirnames without the path) in the directory,
            similar to os.listdir behavior.

        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        real_path = self._resolve_path(path)

        if not self.exists(str(real_path)):
            error_msg = "Directory not found: " + str(path)
            raise FileNotFoundError(error_msg)

        # Get real entries first
        entries = []
        if real_path.exists() and real_path.is_dir():
            entries = [p.name for p in real_path.iterdir()]

        # Add in-memory entries
        # We need to extract just the basenames from the full paths
        in_memory_entries = [Path(p).name for p in self._in_memory_files if Path(p).parent == real_path] + [
            Path(d).name for d in self._directories if Path(d).parent == real_path and d != str(real_path)
        ]

        return list(set(entries + in_memory_entries))

    def home(self) -> Path:
        """
        Return the home directory.

        Returns:
            Path to the home directory
        """
        return Path.home()

    def root(self) -> Path:
        """
        Return the root directory.

        Returns:
            Path to the root directory
        """
        return self._root_dir

    # Additional methods for testing

    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file.

        Args:
            path: Path to write to
            content: Content to write
        """
        self.write_text(path, content)

    def mkdir(self, path: str, parents: bool = True) -> None:
        """
        Create a directory.

        Args:
            path: Path of the directory to create
            parents: If True, create parent directories as needed
        """
        path_obj = self._resolve_path(path)
        path_str = str(path_obj)

        # Check if path exists
        if path_str in self._directories:
            return  # Directory already exists

        # Create parent directories if requested
        if parents and path_obj.parent != path_obj:  # Not root
            parent_str = str(path_obj.parent)
            if parent_str not in self._directories and not Path(parent_str).exists():
                self.mkdir(parent_str, parents=True)

        # Add the directory
        self._directories.add(path_str)

    def _set_directory_entries(self, path: str, entries: list[str]) -> None:
        """
        Set the directory entries for a directory in the in-memory file system.
        This is a helper method for testing that allows explicit control of what
        list_dir() will return for a specific directory.

        Args:
            path: Path of the directory
            entries: List of entry names (not full paths) that the directory should contain
        """
        # Ensure path is absolute and normalized
        dir_path = self._resolve_path(path)
        dir_path_str = str(dir_path)

        # Make sure the directory exists
        if dir_path_str not in self._directories and not Path(dir_path_str).is_dir():
            self.mkdir(dir_path_str)

        # For each entry, add a placeholder entry in our internal structures
        for entry in entries:
            entry_path = dir_path / entry
            entry_path_str = str(entry_path)

            # If the entry ends with a path separator, treat it as a directory
            if entry.endswith(os.path.sep):
                if entry_path_str not in self._directories:
                    self._directories.add(entry_path_str)
            # Otherwise assume it's a file unless it already exists as a directory
            elif entry_path_str not in self._directories and entry_path_str not in self._in_memory_files:
                # Add empty content for files that don't have content yet
                self._in_memory_files[entry_path_str] = ""

    def delete_file(self, path: str) -> None:
        """
        Delete a file.

        Args:
            path: File to delete

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path_str = str(self._resolve_path(path))

        if path_str in self._in_memory_files:
            del self._in_memory_files[path_str]
        elif Path(path_str).is_file():
            Path(path_str).unlink()
        else:
            error_msg = "File not found: " + str(path)
            raise FileNotFoundError(error_msg)

    def rmdir(self, path: str) -> None:
        """
        Remove a directory.

        Args:
            path: Directory to remove

        Raises:
            FileNotFoundError: If the directory doesn't exist
            OSError: If the directory is not empty
        """
        path_str = str(self._resolve_path(path))

        # Remove from in-memory structure
        if path_str in self._directories:
            # Check if directory is empty
            for file in self._in_memory_files:
                if Path(file).parent == Path(path_str):
                    error_msg = "Directory not empty: " + str(path)
                    raise OSError(error_msg)

            for dir_path in self._directories:
                if Path(dir_path).parent == Path(path_str):
                    error_msg = "Directory not empty: " + str(path)
                    raise OSError(error_msg)

            self._directories.remove(path_str)

        # Remove real directory if it exists
        if Path(path_str).is_dir():
            Path(path_str).rmdir()
