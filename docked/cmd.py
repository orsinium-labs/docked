"""
Collection of useful function that generate CLI commands for using inside of RUN.

The commands here are the ones that are the most often used in Docker images
and require certain flags for producing safe and small images.
"""
from __future__ import annotations


def pip_install(*pkgs: str) -> str:
    """Install Python packages from pypi.org.
    """
    suffix = ' '.join(pkgs)
    flags = '--disable-pip-version-check --no-cache-dir'
    return f'python3 -m pip {flags} install {suffix}'


def apt_install(*pkgs: str) -> str:
    """Install system packages from Debian repositories.
    """
    if len(pkgs) <= 2:
        suffix = ' '.join(pkgs)
    else:
        sep = ' \\\n    '
        suffix = sep + sep.join(sorted(pkgs))
    return f'apt-get update && apt-get install -y --no-install-recommends {suffix}'
