"""Command line utility for coloring text and writing pretty things."""
__author__ = "Qrashi"

from .cliasi import Cliasi, cli
from .constants import TextColor
from .__about__ import __version__

SYMBOLS = {
    "success": "✔",
    "download": "⤓",
}

__all__ = ['SYMBOLS', 'Cliasi', 'cli', 'TextColor']
