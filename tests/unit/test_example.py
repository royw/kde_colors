"""Tests for the example module."""

from __future__ import annotations

import pytest

# Constants
TEST_VALUE = 42
HALF_TEST_VALUE = 21

from kde_colors.example import Example, InvalidValueError  # noqa: E402


def test_example_initialization() -> None:
    """Test Example class initialization."""
    example = Example("test", TEST_VALUE)
    assert example.name == "test"
    assert example.value == TEST_VALUE


def test_example_process() -> None:
    """Test Example.process method."""
    example = Example("test", HALF_TEST_VALUE)
    result = example.process()
    assert result == TEST_VALUE


def test_example_process_invalid() -> None:
    """Test Example.process method with invalid value."""
    example = Example("test", None)
    with pytest.raises(InvalidValueError):
        example.process()
