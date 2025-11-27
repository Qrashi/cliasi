"""Command line utility for coloring text and writing pretty things."""
__version__ = "0.1.0"
__author__ = "qrashi"

from .clisi import Clisi, NonBlockingProgressTask, NonBlockingAnimationTask

SYMBOLS = {
    "success": "✔",
    "download": "⤓",
}

__all__ = ['SYMBOLS', 'Clisi', 'NonBlockingProgressTask', 'NonBlockingAnimationTask']

packageinstance = Clisi("CLI")

# automatically export all public methods from clisi
for attr_name in dir(packageinstance):
    if not attr_name.startswith('_'):  # skip private/internal methods
        attr = getattr(packageinstance, attr_name)
        if callable(attr):
            globals()[attr_name] = attr
            __all__.append(attr_name)
