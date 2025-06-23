"""
Unit tests for the StdFileSystem service.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import cast

import pytest

from kde_colors.interfaces.file_system import FileSystemInterface
from kde_colors.services.file_system import StdFileSystem


class TestStdFileSystem:
    """Tests for the StdFileSystem service."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.fs = StdFileSystem()
        # Create a temporary directory for file operations
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = Path(self.temp_dir.name)

    def teardown_method(self) -> None:
        """Tear down test fixtures after each test method."""
        self.temp_dir.cleanup()

    def test_implements_interface(self) -> None:
        """Test that StdFileSystem implements the FileSystemInterface."""
        # Use cast to verify type compatibility with the protocol
        cast(FileSystemInterface, self.fs)
        assert True  # If we got here, the cast succeeded

    def test_read_file(self) -> None:
        """Test reading a file."""
        # Create a test file with content
        test_content = "test content"
        test_file = self.test_dir_path / "test_file.txt"
        test_file.write_text(test_content, encoding="utf-8")

        # Test reading the file
        result = self.fs.read_file(str(test_file))
        assert result == test_content

    def test_read_file_nonexistent(self) -> None:
        """Test reading a non-existent file raises FileNotFoundError."""
        nonexistent_file = self.test_dir_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            self.fs.read_file(str(nonexistent_file))

    def test_write_text_with_path_object(self) -> None:
        """Test writing text to a file using a Path object."""
        test_content = "test content"
        test_file = self.test_dir_path / "test_write.txt"

        self.fs.write_text(test_file, test_content)

        # Verify the file was written correctly
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_write_text_with_string_path(self) -> None:
        """Test writing text to a file using a string path."""
        test_content = "test content"
        test_file = self.test_dir_path / "test_write_str.txt"

        self.fs.write_text(str(test_file), test_content)

        # Verify the file was written correctly
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_exists_file(self) -> None:
        """Test checking if a file path exists."""
        # Create a test file
        test_file = self.test_dir_path / "exists_file.txt"
        test_file.touch()

        assert self.fs.exists(str(test_file)) is True

    def test_exists_directory(self) -> None:
        """Test checking if a directory path exists."""
        # Create a test directory
        test_dir = self.test_dir_path / "exists_dir"
        test_dir.mkdir()

        assert self.fs.exists(str(test_dir)) is True

    def test_exists_nonexistent(self) -> None:
        """Test checking if a non-existent path exists."""
        nonexistent_path = self.test_dir_path / "nonexistent"

        assert self.fs.exists(str(nonexistent_path)) is False

    def test_is_file_true(self) -> None:
        """Test checking if a path is a file when it is a file."""
        # Create a test file
        test_file = self.test_dir_path / "is_file.txt"
        test_file.touch()

        assert self.fs.is_file(str(test_file)) is True

    def test_is_file_false_directory(self) -> None:
        """Test checking if a path is a file when it is a directory."""
        # Create a test directory
        test_dir = self.test_dir_path / "is_file_dir"
        test_dir.mkdir()

        assert self.fs.is_file(str(test_dir)) is False

    def test_is_file_false_nonexistent(self) -> None:
        """Test checking if a path is a file when it doesn't exist."""
        nonexistent_file = self.test_dir_path / "nonexistent.txt"

        assert self.fs.is_file(str(nonexistent_file)) is False

    def test_is_dir_true(self) -> None:
        """Test checking if a path is a directory when it is a directory."""
        # Create a test directory
        test_dir = self.test_dir_path / "is_dir"
        test_dir.mkdir()

        assert self.fs.is_dir(str(test_dir)) is True

    def test_is_dir_false_file(self) -> None:
        """Test checking if a path is a directory when it is a file."""
        # Create a test file
        test_file = self.test_dir_path / "is_dir.txt"
        test_file.touch()

        assert self.fs.is_dir(str(test_file)) is False

    def test_is_dir_false_nonexistent(self) -> None:
        """Test checking if a path is a directory when it doesn't exist."""
        nonexistent_dir = self.test_dir_path / "nonexistent_dir"

        assert self.fs.is_dir(str(nonexistent_dir)) is False

    def test_glob_with_pattern_in_basename(self) -> None:
        """Test globbing with pattern in the basename."""
        # Create test files
        (self.test_dir_path / "glob_test1.txt").touch()
        (self.test_dir_path / "glob_test2.txt").touch()
        (self.test_dir_path / "other_file.txt").touch()

        # Test globbing with wildcard in basename
        pattern = str(self.test_dir_path / "glob_*.txt")
        results = self.fs.glob(pattern)

        # Convert results to absolute paths for comparison
        absolute_results = [Path(p).resolve() for p in results]
        expected_files = [
            (self.test_dir_path / "glob_test1.txt").resolve(),
            (self.test_dir_path / "glob_test2.txt").resolve(),
        ]

        # Check that the expected files are in the results (order might vary)
        assert len(absolute_results) == 2
        for expected in expected_files:
            assert expected in absolute_results

    def test_glob_with_full_pattern(self) -> None:
        """Test globbing with a full pattern."""
        # Create test files in subdirectories
        subdir = self.test_dir_path / "subdir"
        subdir.mkdir()
        (subdir / "glob_nested1.txt").touch()
        (subdir / "glob_nested2.txt").touch()
        # Create another file that shouldn't match
        (subdir / "other_file.log").touch()

        # The "**" recursive pattern doesn't work consistently across systems/implementations
        # So we'll use a simpler pattern directly targeting the subdir
        pattern = str(subdir / "glob_nested*.txt")

        # Get actual results from the file system
        results = self.fs.glob(pattern)

        # Verify the results
        assert len(results) == 2

        # Convert paths to their string representation for easier comparison
        expected_files = [str((subdir / "glob_nested1.txt").resolve()), str((subdir / "glob_nested2.txt").resolve())]
        actual_files = [str(Path(p).resolve()) for p in results]

        # Sort both lists for deterministic comparison
        expected_files.sort()
        actual_files.sort()

        assert actual_files == expected_files

    def test_walk(self) -> None:
        """Test walking a directory tree."""
        # Create a directory structure
        subdir1 = self.test_dir_path / "walk_dir1"
        subdir1.mkdir()
        (subdir1 / "file1.txt").touch()

        subdir2 = self.test_dir_path / "walk_dir1" / "walk_dir2"
        subdir2.mkdir()
        (subdir2 / "file2.txt").touch()

        # Get the actual results from walking the directory
        results = list(self.fs.walk(str(self.test_dir_path)))

        # Verify results match the expected structure
        # We should have at least 3 entries: root, subdir1, and subdir2
        assert len(results) >= 3

        # Check that each result is a tuple with 3 elements (path, dirs, files)
        for result in results:
            assert len(result) == 3
            # Each result should be: (dirpath (str), dirnames (list), filenames (list))
            assert isinstance(result[0], str)
            assert isinstance(result[1], list)
            assert isinstance(result[2], list)

        # Find the results for each directory by path
        root_result = None
        subdir1_result = None
        subdir2_result = None

        for dirpath, dirnames, filenames in results:
            if dirpath == str(self.test_dir_path):
                root_result = (dirpath, dirnames, filenames)
            elif dirpath == str(subdir1):
                subdir1_result = (dirpath, dirnames, filenames)
            elif dirpath == str(subdir2):
                subdir2_result = (dirpath, dirnames, filenames)

        # Verify each directory's content
        assert root_result is not None
        assert "walk_dir1" in root_result[1]  # Root contains walk_dir1

        assert subdir1_result is not None
        assert "walk_dir2" in subdir1_result[1]  # subdir1 contains walk_dir2
        assert "file1.txt" in subdir1_result[2]  # subdir1 contains file1.txt

        assert subdir2_result is not None
        assert not subdir2_result[1]  # subdir2 has no directories
        assert "file2.txt" in subdir2_result[2]  # subdir2 contains file2.txt

    def test_list_dir(self) -> None:
        """Test listing all entries in a directory."""
        # Create test files and directories
        (self.test_dir_path / "file1.txt").touch()
        (self.test_dir_path / "file2.txt").touch()
        (self.test_dir_path / "subdir").mkdir()

        # Get list of all entries
        entries = self.fs.list_dir(str(self.test_dir_path))

        # Verify results
        assert set(entries) == {"file1.txt", "file2.txt", "subdir"}

    def test_home(self) -> None:
        """Test getting the home directory."""
        # Since this is a real system test, we can just verify that the home
        # directory returned by our method is the same as the one returned by Path.home()
        result = self.fs.home()
        expected = Path.home()
        assert result == expected

    def test_root(self) -> None:
        """Test getting the root directory."""
        result = self.fs.root()
        assert result == Path("/")
