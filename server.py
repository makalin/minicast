#!/usr/bin/env python3
"""
Minicast RTSP Server
Ultra-low-bandwidth RTSP streaming server with client catch-up mechanics.
"""

import os
import sys
import time
import json
import socket
import threading
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import subprocess
import signal
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ClientInfo:
    """Information about a connected RTSP client."""
    client_id: str
    ip_address: str
    port: int
    connected_at: datetime
    last_activity: datetime
    bytes_sent: int = 0
    frames_sent: int = 0
    lag_detected: bool = False
    catch_up_mode: bool = False
    catch_up_start: Optional[datetime] = None
    stream_scale: float = 1.0

class MinicastServer:
    """RTSP server with client tracking and adaptive streaming."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.clients: Dict[str, ClientInfo] = {}
        self.clients_lock = threading.Lock()
        self.running = False
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        self.stats_file = "client_stats.json"
        self._load_stats()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _default_config(self) -> Dict:
        """Default server configuration."""
        return {
            'rtsp_port': 554,
            'rtsp_path': '/minicast',
            'input_file': None,
            'max_clients': 10,
            'lag_threshold_ms': 200,
            'catch_up_scale': 2.0,
            'stats_interval': 5,  # seconds
            'log_level': 'INFO',
            'ffmpeg_binary': 'ffmpeg',
            'enable_catch_up': True,
            'byte_tracking': True
        }
    
    def _load_stats(self) -> None:
        """Load client statistics from file."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} client records from stats file")
        except Exception as e:
            logger.warning(f"Could not load stats file: {e}")
    
    def _save_stats(self) -> None:
        """Save client statistics to file."""
        try:
            with self.clients_lock:
                stats_data = {
                    client_id: {
                        'ip_address': client.ip_address,
                        'connected_at': client.connected_at.isoformat(),
                        'bytes_sent': client.bytes_sent,
                        'frames_sent': client.frames_sent,
                        'lag_detected': client.lag_detected,
                        'catch_up_mode': client.catch_up_mode
                    }
                    for client_id, client in self.clients.items()
                }
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save stats: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def validate_input_file(self, input_path: str) -> bool:
        """Validate that the input file exists and is a valid video file."""
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return False
        
        try:
            # Use ffprobe to validate the file
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            # Check if it has video stream
            video_streams = [s for s in info.get('streams', []) if s['codec_type'] == 'video']
            if not video_streams:
                logger.error("Input file has no video stream")
                return False
            
            logger.info(f"Input file validated: {input_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating input file: {e}")
            return False
    
    def start_ffmpeg_stream(self, input_file: str) -> bool:
        """Start FFmpeg RTSP streaming process."""
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            logger.warning("FFmpeg process already running")
            return True
        
        try:
            # Build FFmpeg command for RTSP streaming
            cmd = [
                self.config['ffmpeg_binary'],
                '-re',  # Read input at native frame rate
                '-stream_loop', '-1',  # Loop the input file
                '-i', input_file,
                '-c:v', 'copy',  # Copy video codec (no re-encoding)
                '-c:a', 'copy',  # Copy audio codec if present
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                f'rtsp://0.0.0.0:{self.config["rtsp_port"]}{self.config["rtsp_path"]}'
            ]
            
            logger.info(f"Starting FFmpeg RTSP stream: {' '.join(cmd)}")
            
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts successfully
            time.sleep(2)
            if self.ffmpeg_process.poll() is not None:
                logger.error("FFmpeg process failed to start")
                return False
            
            logger.info("FFmpeg RTSP stream started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting FFmpeg stream: {e}")
            return False
    
    def stop_ffmpeg_stream(self) -> None:
        """Stop the FFmpeg streaming process."""
        if self.ffmpeg_process:
            logger.info("Stopping FFmpeg stream...")
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg process didn't terminate gracefully, killing...")
                self.ffmpeg_process.kill()
            except Exception as e:
                logger.error(f"Error stopping FFmpeg: {e}")
            finally:
                self.ffmpeg_process = None
    
    def add_client(self, client_id: str, ip_address: str, port: int) -> None:
        """Add a new client to tracking."""
        with self.clients_lock:
            if len(self.clients) >= self.config['max_clients']:
                logger.warning(f"Maximum clients reached ({self.config['max_clients']})")
                return
            
            client = ClientInfo(
                client_id=client_id,
                ip_address=ip_address,
                port=port,
                connected_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.clients[client_id] = client
            logger.info(f"Client connected: {client_id} ({ip_address}:{port})")
    
    def remove_client(self, client_id: str) -> None:
        """Remove a client from tracking."""
        with self.clients_lock:
            if client_id in self.clients:
                client = self.clients[client_id]
                duration = datetime.now() - client.connected_at
                logger.info(f"Client disconnected: {client_id} (duration: {duration})")
                del self.clients[client_id]
    
    def update_client_activity(self, client_id: str, bytes_sent: int = 0, frames_sent: int = 0) -> None:
        """Update client activity and check for lag."""
        with self.clients_lock:
            if client_id not in self.clients:
                return
            
            client = self.clients[client_id]
            client.last_activity = datetime.now()
            client.bytes_sent += bytes_sent
            client.frames_sent += frames_sent
            
            # Check for lag (simplified - in real implementation, you'd track actual lag)
            if self.config['enable_catch_up'] and not client.catch_up_mode:
                # Simulate lag detection (in real implementation, this would be based on actual client feedback)
                if frames_sent > 0 and frames_sent % 10 == 0:  # Check every 10 frames
                    self._check_client_lag(client)
    
    def _check_client_lag(self, client: ClientInfo) -> None:
        """Check if client is lagging and initiate catch-up if needed."""
        # This is a simplified implementation
        # In a real system, you'd track actual client playback position vs server position
        
        # Simulate lag detection (random for demo purposes)
        import random
        if random.random() < 0.1:  # 10% chance of detecting lag
            client.lag_detected = True
            client.catch_up_mode = True
            client.catch_up_start = datetime.now()
            client.stream_scale = self.config['catch_up_scale']
            
            logger.info(f"Lag detected for client {client.client_id}, enabling catch-up mode (scale: {client.stream_scale})")
            
            # In a real implementation, you'd send RTSP PLAY command with scale parameter
            self._send_catch_up_command(client)
    
    def _send_catch_up_command(self, client: ClientInfo) -> None:
        """Send RTSP catch-up command to client."""
        # This is a placeholder for the actual RTSP command implementation
        # In a real system, you'd send an RTSP PLAY command with scale parameter
        logger.info(f"Sending catch-up command to {client.client_id} with scale {client.stream_scale}")
        
        # Simulate catch-up completion after some time
        def reset_catch_up():
            time.sleep(2)  # Simulate catch-up duration
            with self.clients_lock:
                if client.client_id in self.clients:
                    client.catch_up_mode = False
                    client.stream_scale = 1.0
                    logger.info(f"Catch-up completed for client {client.client_id}")
        
        threading.Thread(target=reset_catch_up, daemon=True).start()
    
    def get_client_stats(self) -> Dict:
        """Get current client statistics."""
        with self.clients_lock:
            return {
                'total_clients': len(self.clients),
                'clients': [
                    {
                        'id': client.client_id,
                        'ip': client.ip_address,
                        'connected_at': client.connected_at.isoformat(),
                        'bytes_sent': client.bytes_sent,
                        'frames_sent': client.frames_sent,
                        'lag_detected': client.lag_detected,
                        'catch_up_mode': client.catch_up_mode,
                        'stream_scale': client.stream_scale
                    }
                    for client in self.clients.values()
                ]
            }
    
    def start_stats_monitor(self) -> None:
        """Start periodic stats monitoring and saving."""
        def monitor_loop():
            while self.running:
                try:
                    stats = self.get_client_stats()
                    logger.info(f"Active clients: {stats['total_clients']}")
                    
                    # Log detailed stats for each client
                    for client in stats['clients']:
                        if client['bytes_sent'] > 0:
                            logger.debug(f"Client {client['id']}: {client['bytes_sent']} bytes, {client['frames_sent']} frames")
                    
                    # Save stats periodically
                    self._save_stats()
                    
                    time.sleep(self.config['stats_interval'])
                    
                except Exception as e:
                    logger.error(f"Error in stats monitor: {e}")
                    time.sleep(1)
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def start(self, input_file: str) -> bool:
        """Start the Minicast server."""
        if not self.validate_input_file(input_file):
            return False
        
        logger.info("Starting Minicast RTSP server...")
        logger.info(f"Configuration: {self.config}")
        
        # Start FFmpeg stream
        if not self.start_ffmpeg_stream(input_file):
            return False
        
        self.running = True
        
        # Start stats monitor
        self.start_stats_monitor()
        
        logger.info(f"✅ Minicast server started successfully!")
        logger.info(f"RTSP URL: rtsp://localhost:{self.config['rtsp_port']}{self.config['rtsp_path']}")
        logger.info("Press Ctrl+C to stop the server")
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
                # Check if FFmpeg process is still running
                if self.ffmpeg_process and self.ffmpeg_process.poll() is not None:
                    logger.error("FFmpeg process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()
        
        return True
    
    def stop(self) -> None:
        """Stop the Minicast server."""
        logger.info("Stopping Minicast server...")
        self.running = False
        
        # Stop FFmpeg stream
        self.stop_ffmpeg_stream()
        
        # Save final stats
        self._save_stats()
        
        logger.info("Minicast server stopped")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Minicast RTSP Server - Ultra-low-bandwidth streaming with client catch-up"
    )
    parser.add_argument('--input', '-i', required=True, help='Input MP4 file path')
    parser.add_argument('--port', '-p', type=int, default=554, help='RTSP port (default: 554)')
    parser.add_argument('--path', default='/minicast', help='RTSP path (default: /minicast)')
    parser.add_argument('--max-clients', type=int, default=10, help='Maximum clients (default: 10)')
    parser.add_argument('--lag-threshold', type=int, default=200, help='Lag threshold in ms (default: 200)')
    parser.add_argument('--catch-up-scale', type=float, default=2.0, help='Catch-up speed multiplier (default: 2.0)')
    parser.add_argument('--stats-interval', type=int, default=5, help='Stats logging interval in seconds (default: 5)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-catch-up', action='store_true', help='Disable client catch-up mechanics')
    parser.add_argument('--no-byte-tracking', action='store_true', help='Disable byte tracking')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Build configuration
    config = {
        'rtsp_port': args.port,
        'rtsp_path': args.path,
        'max_clients': args.max_clients,
        'lag_threshold_ms': args.lag_threshold,
        'catch_up_scale': args.catch_up_scale,
        'stats_interval': args.stats_interval,
        'enable_catch_up': not args.no_catch_up,
        'byte_tracking': not args.no_byte_tracking,
        'ffmpeg_binary': 'ffmpeg'
    }
    
    # Create and start server
    server = MinicastServer(config)
    success = server.start(args.input)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 