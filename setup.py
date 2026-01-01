#!/usr/bin/env python3

# File: setup.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-01
# Description: 
# License: MIT

from setuptools import setup, find_packages
from pathlib import Path
import os
import traceback
import shutil

NAME = 'pips'

try:
    shutil.copy2("__version__.py", f"{NAME}/__version__.py")
except:
    pass

def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "1.0.0"

version = get_version()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pips",
    version=version,
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    description="Another Python Package Manager - An enhanced alternative to pip",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/pips",
    packages=[NAME],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=10.0.0",
        "envdot>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "pips=pips.pips:main",
        ],
    },
    keywords="pip package manager pypi download install statistics",
    project_urls={
        "Bug Reports": "https://github.com/cumulus13/pips/issues",
        "Source": "https://github.com/cumulus13/pips",
    },
)