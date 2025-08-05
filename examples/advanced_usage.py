#!/usr/bin/env python3
"""
Advanced Usage Example for Minicast
Demonstrates custom configuration, client tracking, and monitoring.
"""

import os
import sys
import time
import threading
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import minicast
sys.path.insert(0, str(Path(__file__).parent.parent))

from minicast import MinicastTranscoder, MinicastServer


class AdvancedMinicastExample:
    """Advanced example with custom configuration and monitoring."""
    
    def __init__(self):
        self.server = None
        self.monitoring = False
    
    def custom_transcode_config(self):
        """Demonstrate custom transcoding configuration."""
        print("🎨 Custom Transcoding Configuration")
        print("-" * 35)
        
        # Custom transcoding settings for different use cases
        configs = {
            'ultra_low_bandwidth': {
                'resolution': '120x90',
                'fps': 1,
                'bitrate': '20k',
                'crf': 35,
                'description': 'Ultra-low bandwidth (dial-up speeds)'
            },
            'mobile_optimized': {
                'resolution': '240x180',
                'fps': 3,
                'bitrate': '50k',
                'crf': 28,
                'description': 'Mobile-optimized (3G speeds)'
            },
            'high_quality': {
                'resolution': '320x240',
                'fps': 5,
                'bitrate': '100k',
                'crf': 23,
                'description': 'High quality (broadband)'
            }
        }
        
        for name, config in configs.items():
            print(f"\n📊 {config['description']}:")
            print(f"   Resolution: {config['resolution']}")
            print(f"   FPS: {config['fps']}")
            print(f"   Bitrate: {config['bitrate']}")
            print(f"   CRF: {config['crf']}")
        
        return configs
    
    def transcode_with_custom_config(self, input_path: str, config_name: str = 'mobile_optimized'):
        """Transcode with custom configuration."""
        configs = self.custom_transcode_config()
        
        if config_name not in configs:
            print(f"❌ Unknown config: {config_name}")
            return None
        
        config = configs[config_name]
        print(f"\n🔄 Transcoding with {config_name} configuration...")
        
        transcoder = MinicastTranscoder()
        output_path = f"streams/custom_{config_name}.mp4"
        
        # Ensure streams directory exists
        os.makedirs("streams", exist_ok=True)
        
        success = transcoder.transcode_gif(input_path, output_path, config)
        
        if success:
            print(f"✅ Custom transcoding complete: {output_path}")
            return output_path
        else:
            print("❌ Custom transcoding failed")
            return None
    
    def start_monitoring(self):
        """Start client monitoring in a separate thread."""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring and self.server:
                try:
                    stats = self.server.get_client_stats()
                    
                    print(f"\n📊 Client Statistics ({datetime.now().strftime('%H:%M:%S')})")
                    print(f"   Active Clients: {stats['total_clients']}")
                    
                    for client in stats['clients']:
                        print(f"   📱 {client['id']} ({client['ip']})")
                        print(f"      Bytes Sent: {client['bytes_sent']:,}")
                        print(f"      Frames Sent: {client['frames_sent']}")
                        print(f"      Lag Detected: {'Yes' if client['lag_detected'] else 'No'}")
                        print(f"      Catch-up Mode: {'Yes' if client['catch_up_mode'] else 'No'}")
                        if client['catch_up_mode']:
                            print(f"      Stream Scale: {client['stream_scale']}x")
                    
                    time.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    break
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def custom_server_config(self):
        """Demonstrate custom server configuration."""
        print("\n⚙️ Custom Server Configuration")
        print("-" * 30)
        
        config = {
            'rtsp_port': 8554,
            'rtsp_path': '/minicast/advanced',
            'max_clients': 20,
            'lag_threshold_ms': 150,  # More sensitive lag detection
            'catch_up_scale': 1.5,    # Gentler catch-up
            'stats_interval': 2,      # More frequent stats
            'enable_catch_up': True,
            'byte_tracking': True
        }
        
        print("Server Settings:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        return config
    
    def run_advanced_example(self, input_path: str):
        """Run the complete advanced example."""
        print("🚀 Advanced Minicast Example")
        print("=" * 40)
        
        # Step 1: Custom transcoding
        output_path = self.transcode_with_custom_config(input_path, 'mobile_optimized')
        if not output_path:
            return
        
        # Step 2: Custom server configuration
        config = self.custom_server_config()
        
        # Step 3: Start server with monitoring
        print(f"\n📡 Starting advanced server...")
        self.server = MinicastServer(config)
        
        # Start monitoring
        monitor_thread = self.start_monitoring()
        
        print(f"📺 RTSP URL: rtsp://localhost:{config['rtsp_port']}{config['rtsp_path']}")
        print("💡 Open VLC and connect to the RTSP URL above")
        print("📊 Client monitoring is active - check the stats above")
        print("Press Ctrl+C to stop the server")
        
        try:
            # Start the server
            self.server.start(output_path)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping advanced server...")
        finally:
            self.monitoring = False
            if self.server:
                self.server.stop()


def main():
    """Main function for advanced example."""
    # Example GIF path
    gif_path = "gifs/example.gif"
    
    # Check if example GIF exists
    if not os.path.exists(gif_path):
        print(f"❌ Example GIF not found: {gif_path}")
        print("Please add a GIF file to the gifs/ directory")
        return
    
    # Run advanced example
    example = AdvancedMinicastExample()
    example.run_advanced_example(gif_path)


if __name__ == "__main__":
    main() 