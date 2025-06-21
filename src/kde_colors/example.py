"""Example module to demonstrate docstring formatting.

This module shows how to format docstrings for good documentation generation
using Google style and mkdocstrings.
"""

from __future__ import annotations

from typing import Any


class InvalidValueError(ValueError):
    """Raised when a value is invalid."""

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Invalid value")


class Example:
    """A class to demonstrate docstring formatting.

    This class shows various ways to document classes, methods, and attributes
    using Google style docstrings.

    Attributes:
        name: The name of the example
        value: The value to store

    Example:
        ```python
        example = Example("test", 42)
        result = example.process()
        ```
    """

    def __init__(self, name: str, value: Any) -> None:
        """Initialize the Example.

        Args:
            name: The name of the example
            value: The value to store
        """
        self.name = name
        self.value = value

    def process(self) -> Any:
        """Process the stored value.

        This method demonstrates how to document a method that returns a value.

        Returns:
            The processed value

        Raises:
            ValueError: If the value is invalid
        """
        if not self.value:
            raise InvalidValueError
        return self.value * 2
