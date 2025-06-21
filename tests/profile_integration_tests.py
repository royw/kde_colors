#!/usr/bin/env python3
"""Profile the integration tests to identify performance bottlenecks."""

from __future__ import annotations

import cProfile
import pstats
import sys


def run_tests() -> None:
    """Run the integration tests."""
    import pytest

    sys.exit(pytest.main(["-v", "tests/integration/"]))


def profile_integration_tests(output_file: str = "profile_results.prof") -> None:
    """Profile the integration tests and display results.

    Args:
        output_file: Path to save profiling results
    """
    print("Profiling integration tests...")
    print(f"Output will be saved to: {output_file}")

    # Run with cProfile
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        run_tests()
    except SystemExit:
        pass
    finally:
        profiler.disable()
        profiler.dump_stats(output_file)

    # Display results
    stats = pstats.Stats(output_file)

    print("\n=== Top 20 functions by cumulative time ===")
    stats.sort_stats("cumtime").print_stats(20)

    print("\n=== Top 20 functions by time per call ===")
    stats.sort_stats("tottime").print_stats(20)

    print("\n=== Top 20 functions by number of calls ===")
    stats.sort_stats("ncalls").print_stats(20)

    print(f"\nFull profile data saved to: {output_file}")
    print("To analyze with snakeviz, run: snakeviz", output_file)


if __name__ == "__main__":
    profile_integration_tests("integration_tests_profile.prof")
