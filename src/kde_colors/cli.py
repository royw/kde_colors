"""Command-line interface for the package."""

from __future__ import annotations

from kde_colors.example import Example


def main() -> None:
    """Run the main CLI program."""
    example = Example("test", 42)
    print(example.process())


if __name__ == "__main__":
    main()
