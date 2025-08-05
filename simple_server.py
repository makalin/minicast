#!/usr/bin/env python3
"""
Simple HTTP Streaming Server for Minicast
A basic HTTP server that streams video files for demonstration.
"""

import os
import time
import threading
import logging
from pathlib import Path
from flask import Flask, Response, render_template_string
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleStreamingServer:
    """Simple HTTP streaming server for video files."""
    
    def __init__(self, video_file: str, port: int = 8080):
        self.video_file = video_file
        self.port = port
        self.running = False
        
    def validate_video_file(self) -> bool:
        """Validate that the video file exists."""
        if not os.path.exists(self.video_file):
            logger.error(f"Video file not found: {self.video_file}")
            return False
        
        logger.info(f"Video file validated: {self.video_file}")
        return True
    
    def get_video_info(self) -> dict:
        """Get video file information using ffprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                self.video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            import json
            data = json.loads(result.stdout)
            
            video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)
            
            return {
                'duration': float(data.get('format', {}).get('duration', 0)),
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'fps': video_stream.get('r_frame_rate', '0/1') if video_stream else '0/1',
                'bitrate': data.get('format', {}).get('bit_rate', 0),
                'size': int(data.get('format', {}).get('size', 0))
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    def start(self) -> bool:
        """Start the HTTP streaming server."""
        if not self.validate_video_file():
            return False
        
        video_info = self.get_video_info()
        logger.info(f"Video info: {video_info}")
        
        self.running = True
        
        logger.info(f"🚀 Starting HTTP streaming server on port {self.port}")
        logger.info(f"📺 Video file: {self.video_file}")
        logger.info(f"🌐 Access URL: http://localhost:{self.port}")
        
        try:
            app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the server."""
        logger.info("Stopping HTTP streaming server...")
        self.running = False

# HTML template for the video player
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Minicast - Ultra-Low-Bandwidth Streaming</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 600px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .video-container {
            margin: 20px 0;
        }
        video {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: left;
        }
        .stats h3 {
            margin-top: 0;
            color: #495057;
        }
        .feature-list {
            text-align: left;
            margin: 20px 0;
        }
        .feature-list li {
            margin: 5px 0;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎞️📡 Minicast Streaming</h1>
        <p><strong>Ultra-Low-Bandwidth Reaction GIF Channel</strong></p>
        
        <div class="video-container">
            <video controls autoplay loop muted>
                <source src="/video" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        
        <div class="stats">
            <h3>📊 Stream Information</h3>
            <p><strong>Resolution:</strong> {{ video_info.width }}x{{ video_info.height }}</p>
            <p><strong>Duration:</strong> {{ "%.2f"|format(video_info.duration) }} seconds</p>
            <p><strong>FPS:</strong> {{ video_info.fps }}</p>
            <p><strong>Bitrate:</strong> {{ "%.0f"|format(video_info.bitrate|float/1000) }} kbps</p>
            <p><strong>File Size:</strong> {{ "%.1f"|format(video_info.size/1024) }} KB</p>
        </div>
        
        <div class="feature-list">
            <h3>✨ Features</h3>
            <ul>
                <li>🔁 Ultra-low bandwidth optimization (160×120 @ 2fps)</li>
                <li>🎥 H.264 baseline profile for maximum compatibility</li>
                <li>⏩ Smart frame control (P-frames after initial I-frame)</li>
                <li>📈 Real-time client catch-up mechanics</li>
                <li>🔌 HTTP streaming for easy web access</li>
            </ul>
        </div>
        
        <p><em>Streaming optimized for low-bandwidth scenarios</em></p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with video player."""
    server = app.config.get('server')
    if server:
        video_info = server.get_video_info()
        return render_template_string(HTML_TEMPLATE, video_info=video_info)
    return "Server not configured"

@app.route('/video')
def video():
    """Stream the video file."""
    server = app.config.get('server')
    if not server or not os.path.exists(server.video_file):
        return "Video file not found", 404
    
    def generate():
        with open(server.video_file, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    # Loop the video
                    f.seek(0)
                    chunk = f.read(8192)
                yield chunk
    
    return Response(
        generate(),
        mimetype='video/mp4',
        headers={
            'Content-Disposition': 'inline',
            'Cache-Control': 'no-cache'
        }
    )

@app.route('/stats')
def stats():
    """Get streaming statistics."""
    server = app.config.get('server')
    if server:
        video_info = server.get_video_info()
        return {
            'video_file': server.video_file,
            'video_info': video_info,
            'server_running': server.running
        }
    return {'error': 'Server not configured'}

def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Simple HTTP Streaming Server for Minicast"
    )
    parser.add_argument('--input', '-i', required=True, help='Input MP4 file path')
    parser.add_argument('--port', '-p', type=int, default=8080, help='HTTP port (default: 8080)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create server instance
    server = SimpleStreamingServer(args.input, args.port)
    
    # Store server instance in Flask app config
    app.config['server'] = server
    
    # Start server
    success = server.start()
    
    if not success:
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main() 