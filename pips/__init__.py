#!/usr/bin/env python3

# File: pips/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-02
# Description: 
# License: MIT

from .pips import PipsError, PyPIClient, PackageDownloader, PackageInstaller, StatisticsDisplay, parse_package_spec, get_save_directory, validate_version

from __version__ import version

__all__ = [
	"PipsError",
	"PyPIClient",
	"PackageDownloader",
	"PackageInstaller",
	"StatisticsDisplay",
	"parse_package_spec",
	"get_save_directory",
	"validate_version",
]

__version__ = version