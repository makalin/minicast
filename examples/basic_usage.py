#!/usr/bin/env python3
"""
Basic Usage Example for Minicast
Demonstrates how to transcode a GIF and start a streaming server.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import minicast
sys.path.insert(0, str(Path(__file__).parent.parent))

from minicast import MinicastTranscoder, MinicastServer


def main():
    """Basic usage example."""
    print("🎞️ Minicast Basic Usage Example")
    print("=" * 40)
    
    # Example GIF path (you would replace this with your actual GIF)
    gif_path = "gifs/example.gif"
    
    # Check if example GIF exists
    if not os.path.exists(gif_path):
        print(f"❌ Example GIF not found: {gif_path}")
        print("Please add a GIF file to the gifs/ directory")
        print("You can download a sample GIF from: https://giphy.com/")
        return
    
    print(f"📁 Input GIF: {gif_path}")
    
    # Step 1: Transcode the GIF
    print("\n🔄 Step 1: Transcoding GIF...")
    transcoder = MinicastTranscoder()
    
    # Create stream-ready file
    output_path = transcoder.create_stream_ready_file(gif_path)
    
    if not output_path:
        print("❌ Failed to transcode GIF")
        return
    
    print(f"✅ Transcoding complete: {output_path}")
    
    # Step 2: Start the streaming server
    print("\n📡 Step 2: Starting RTSP server...")
    
    # Configure server
    config = {
        'rtsp_port': 8554,  # Use non-standard port for testing
        'rtsp_path': '/minicast',
        'max_clients': 5,
        'lag_threshold_ms': 200,
        'catch_up_scale': 2.0,
        'stats_interval': 3
    }
    
    server = MinicastServer(config)
    
    print("🚀 Starting server...")
    print("Press Ctrl+C to stop the server")
    print(f"📺 RTSP URL: rtsp://localhost:{config['rtsp_port']}{config['rtsp_path']}")
    print("💡 Open VLC and connect to the RTSP URL above")
    
    try:
        # Start the server
        server.start(output_path)
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    main() 