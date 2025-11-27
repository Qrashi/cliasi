"""Command line utility for coloring text and writing pretty things."""
__author__ = "Qrashi"

from .cliasi import Cliasi, NonBlockingProgressTask, NonBlockingAnimationTask
from .__about__ import __version__

SYMBOLS = {
    "success": "✔",
    "download": "⤓",
}

__all__ = ['SYMBOLS', 'Cliasi', 'NonBlockingProgressTask', 'NonBlockingAnimationTask', 'cli']

cli = Cliasi("CLI")