"""Top-level package for wordcard_maker."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """card-maker"""
__email__ = "feishengfei@126.com"
__version__ = "0.0.1"

from .src.wordcard_maker.nodes import NODE_CLASS_MAPPINGS
from .src.wordcard_maker.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
