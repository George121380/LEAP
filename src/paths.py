"""
Path utilities for the VirtualHome LEAP project.

This module centralizes frequently used directories and provides helpers
to construct absolute paths robust to current working directory.
"""

from __future__ import annotations

import os
import sys
from typing import Optional


# Directory anchors
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SRC_DIR, '..'))


def project_root() -> str:
    return ROOT_DIR


def dataset_root() -> str:
    return os.path.join(ROOT_DIR, 'VirtualHome-HG')


def dataset_scripts_dir() -> str:
    return os.path.join(dataset_root(), 'scripts')


def dataset_scenes_dir() -> str:
    return os.path.join(dataset_root(), 'scenes')


def dataset_tasks_dir() -> str:
    return os.path.join(dataset_root(), 'dataset')


def cooking_tasks_dir() -> str:
    return os.path.join(dataset_root(), 'cooking')


def simulator_dir() -> str:
    return os.path.join(SRC_DIR, 'simulator')


def domain_dir() -> str:
    return os.path.join(SRC_DIR, 'domain')


def ensure_on_sys_path(path: str) -> None:
    if path not in sys.path:
        sys.path.append(path)


def ensure_dataset_scripts_on_path() -> None:
    """Ensure VirtualHome dataset scripts are importable."""
    ensure_on_sys_path(dataset_scripts_dir())


