"""Unit tests for the FileSystemDouble class."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from kde_colors.interfaces.file_system import FileSystemInterface
from tests.support.file_system_double import FileSystemDouble


class TestFileSystemDouble:
    """Unit tests for FileSystemDouble."""

    def test_implements_interface(self) -> None:
        """Test that FileSystemDouble implements the FileSystemInterface."""
        # This will raise a TypeError if FileSystemDouble doesn't implement the interface
        fs_double: FileSystemInterface = FileSystemDouble()

        # Verify we can call interface methods without errors
        assert isinstance(fs_double, FileSystemInterface)
        assert isinstance(fs_double.root(), Path)

    def test_initialization(self) -> None:
        """Test initialization with different root directories."""
        # Test with default root
        fs1 = FileSystemDouble()
        assert fs1.root() == Path.cwd()

        # Test with custom root as string
        fs2 = FileSystemDouble("/tmp")
        assert fs2.root() == Path("/tmp")

        # Test with custom root as Path
        fs3 = FileSystemDouble(Path.home())
        assert fs3.root() == Path.home()

    def test_in_memory_file_operations(self) -> None:
        """Test in-memory file operations."""
        fs = FileSystemDouble()

        # Write and read a file
        test_path = "test_file.txt"
        test_content = "Hello, World!"
        fs.write_file(test_path, test_content)

        # Check file existence
        assert fs.file_exists(test_path)
        assert fs.exists(test_path)
        assert fs.is_file(test_path)

        # Read file content
        assert fs.read_file(test_path) == test_content

        # Delete file and verify it's gone
        fs.delete_file(test_path)
        assert not fs.file_exists(test_path)
        assert not fs.exists(test_path)
        with pytest.raises(FileNotFoundError):
            fs.read_file(test_path)

    def test_in_memory_directory_operations(self) -> None:
        """Test in-memory directory operations."""
        fs = FileSystemDouble()

        # Create directory
        test_dir = "test_dir"
        fs.mkdir(test_dir)

        # Check directory existence
        assert fs.exists(test_dir)
        assert fs.is_dir(test_dir)
        assert not fs.is_file(test_dir)

        # Create nested directory
        nested_dir_path = Path(test_dir) / "nested"
        nested_dir = str(nested_dir_path)
        fs.mkdir(nested_dir)
        assert fs.is_dir(nested_dir)

        # Create file in directory
        file_in_dir_path = Path(test_dir) / "file.txt"
        file_in_dir = str(file_in_dir_path)
        fs.write_file(file_in_dir, "Content")

        # Check directory listing
        # Check directory listing - extract basenames for comparison
        listed_files = [Path(p).name for p in fs.list_files(test_dir)]
        assert listed_files == ["file.txt"]
        # Check all directory contents (files and dirs)
        dir_contents = [Path(p).name for p in fs.list_dir(test_dir)]
        assert sorted(dir_contents) == ["file.txt", "nested"]

        # Try to remove non-empty directory (should fail)
        with pytest.raises(OSError, match="Directory not empty"):
            fs.rmdir(test_dir)

        # Clean up directory
        fs.delete_file(file_in_dir)
        fs.rmdir(nested_dir)
        fs.rmdir(test_dir)

        assert not fs.exists(test_dir)

    def test_path_resolution(self) -> None:
        """Test path resolution and expansion."""
        # Create with custom root
        with TemporaryDirectory() as temp_dir:
            fs = FileSystemDouble(temp_dir)

            # Test relative path resolution
            rel_path = "relative/path"
            abs_path = fs.resolve_path(rel_path)
            assert abs_path == str(Path(temp_dir) / rel_path)

            # Test absolute path remains unchanged
            orig_abs_path = "/absolute/path"
            resolved_abs_path = fs.resolve_path(orig_abs_path)
            assert resolved_abs_path == orig_abs_path

    def test_glob_patterns(self) -> None:
        """Test glob pattern matching."""
        fs = FileSystemDouble()

        # Create some test files
        fs.write_file("test1.txt", "content")
        fs.write_file("test2.txt", "content")
        fs.write_file("other.log", "content")
        fs.mkdir("subdir")
        fs.write_file("subdir/test3.txt", "content")

        # Test pattern matching
        txt_files = fs.glob("*.txt")
        # Extract basenames for comparison
        txt_files = [Path(p).name for p in fs.glob("*.txt")]
        assert sorted(txt_files) == ["test1.txt", "test2.txt"]

        # Test subdirectory pattern matching
        subdir_files = [Path(p).name for p in fs.glob("subdir/*.txt")]
        assert subdir_files == ["test3.txt"]

        # Clean up
        fs.delete_file("test1.txt")
        fs.delete_file("test2.txt")
        fs.delete_file("other.log")
        fs.delete_file("subdir/test3.txt")
        fs.rmdir("subdir")

    def test_hybrid_operations(self) -> None:
        """Test operations that work with both real and in-memory files."""
        with TemporaryDirectory() as temp_dir:
            # Create a real file on disk
            real_path = Path(temp_dir) / "real_file.txt"
            real_content = "Real file content"

            real_path.write_text(real_content, encoding="utf-8")

            # Initialize FileSystemDouble with the temp directory
            fs = FileSystemDouble(temp_dir)

            # Create an in-memory file
            in_mem_file_path = "in_mem_file.txt"
            in_mem_content = "In-memory content"
            fs.write_file(in_mem_file_path, in_mem_content)

            # Both files should be visible to FileSystemDouble
            assert fs.file_exists("real_file.txt")
            assert fs.file_exists(in_mem_file_path)

            # Contents should be retrievable
            assert fs.read_file("real_file.txt") == real_content
            assert fs.read_file(in_mem_file_path) == in_mem_content

            # Listing should include both files
            file_list = [Path(p).name for p in fs.list_files(".")]
            assert "real_file.txt" in file_list
            assert "in_mem_file.txt" in file_list

            # Clean up in-memory file
            fs.delete_file(in_mem_file_path)
