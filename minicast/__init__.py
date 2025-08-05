"""
Minicast - Ultra-Low-Bandwidth Reaction GIF Channel

A lightweight RTSP-compatible streaming service optimized for broadcasting
short, looping reaction GIFs with minimal data usage.
"""

__version__ = "1.0.0"
__author__ = "Minicast Team"
__description__ = "Ultra-Low-Bandwidth Reaction GIF Channel"

from .transcoder import MinicastTranscoder
from .server import MinicastServer, ClientInfo

__all__ = [
    'MinicastTranscoder',
    'MinicastServer', 
    'ClientInfo',
    '__version__',
    '__author__',
    '__description__'
] 