"""
Shared pytest fixtures for DVPWA security regression tests.

These tests use source-code inspection (reading .py files directly)
to avoid needing the full DVPWA dependency stack (aiohttp, aiopg, etc.)
installed in the test environment.
"""

import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_source(relative_path: str) -> str:
    """Read a source file from the project and return its contents."""
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    with open(full_path, 'r') as f:
        return f.read()
