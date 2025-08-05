"""
Minicast Transcoder Module
Converts GIFs to ultra-low-bandwidth H.264 streams optimized for RTSP broadcasting.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MinicastTranscoder:
    """Transcodes GIFs to low-bandwidth H.264 streams."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self._validate_ffmpeg()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default transcoding configuration."""
        return {
            'resolution': '160x120',
            'fps': 2,
            'bitrate': '50k',
            'profile': 'baseline',
            'level': '3.0',
            'keyframe_interval': 30,  # 15 seconds at 2fps
            'gop_size': 4,  # Group of Pictures size
            'preset': 'ultrafast',
            'crf': 28,  # Constant Rate Factor (higher = lower quality, smaller file)
            'audio': False,
            'loop': True,
            'duration': 3  # Target duration in seconds
        }
    
    def _validate_ffmpeg(self) -> None:
        """Validate that FFmpeg is available."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("FFmpeg found and working")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg not found. Please install FFmpeg first.")
            raise RuntimeError("FFmpeg not available")
    
    def get_gif_info(self, input_path: str) -> Dict[str, Any]:
        """Extract information about the input GIF."""
        try:
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
            
            # Extract relevant info
            format_info = info.get('format', {})
            video_stream = next((s for s in info.get('streams', []) if s['codec_type'] == 'video'), None)
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'fps': self._parse_fps(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
                'size': int(format_info.get('size', 0))
            }
        except Exception as e:
            logger.error(f"Error getting GIF info: {e}")
            return {}
    
    def _parse_fps(self, fps_str: str) -> float:
        """Parse FPS string like '10/1' to float."""
        try:
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                return num / den if den != 0 else 0
            return float(fps_str)
        except:
            return 0
    
    def transcode_gif(self, input_path: str, output_path: str, 
                     custom_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transcode GIF to low-bandwidth H.264 MP4.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path for output MP4 file
            custom_config: Optional custom configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        config = {**self.config, **(custom_config or {})}
        
        # Get input info
        gif_info = self.get_gif_info(input_path)
        if not gif_info:
            logger.error("Could not get GIF information")
            return False
        
        logger.info(f"Transcoding {input_path} -> {output_path}")
        logger.info(f"Input: {gif_info['width']}x{gif_info['height']} @ {gif_info['fps']:.2f}fps, {gif_info['duration']:.2f}s")
        logger.info(f"Output: {config['resolution']} @ {config['fps']}fps, {config['bitrate']} bitrate")
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', input_path,
            '-vf', self._build_video_filter(config),
            '-c:v', 'libx264',
            '-preset', config['preset'],
            '-crf', str(config['crf']),
            '-b:v', config['bitrate'],
            '-maxrate', config['bitrate'],
            '-bufsize', str(int(config['bitrate'].replace('k', '')) * 2) + 'k',
            '-profile:v', config['profile'],
            '-level', config['level'],
            '-g', str(config['gop_size']),
            '-keyint_min', str(config['keyframe_interval']),
            '-sc_threshold', '0',  # Disable scene change detection
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-f', 'mp4'
        ]
        
        # Add audio settings if needed
        if config['audio']:
            cmd.extend(['-c:a', 'aac', '-b:a', '32k'])
        else:
            cmd.extend(['-an'])  # No audio
        
        # Add loop if requested
        if config['loop']:
            cmd.extend(['-stream_loop', '-1'])
        
        cmd.append(output_path)
        
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify output
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f"Transcoding successful! Output size: {output_size / 1024:.1f}KB")
                return True
            else:
                logger.error("Output file not created")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e}")
            logger.error(f"FFmpeg stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def _build_video_filter(self, config: Dict[str, Any]) -> str:
        """Build FFmpeg video filter string."""
        filters = []
        
        # Scale to target resolution
        filters.append(f"scale={config['resolution']}")
        
        # Set framerate
        filters.append(f"fps={config['fps']}")
        
        # Add duration limit if specified
        if config.get('duration'):
            filters.append(f"trim=duration={config['duration']}")
        
        return ','.join(filters)
    
    def create_stream_ready_file(self, input_path: str, output_dir: str = "streams") -> Optional[str]:
        """
        Create a stream-ready file optimized for RTSP broadcasting.
        
        Args:
            input_path: Path to input GIF
            output_dir: Directory for output files
            
        Returns:
            str: Path to created file, or None if failed
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        input_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{input_name}_stream.mp4")
        
        # Optimize config for streaming
        stream_config = {
            'resolution': '160x120',
            'fps': 2,
            'bitrate': '30k',  # Even lower for streaming
            'crf': 30,
            'gop_size': 4,
            'keyframe_interval': 8,  # More frequent keyframes for streaming
            'loop': True
        }
        
        if self.transcode_gif(input_path, output_path, stream_config):
            logger.info(f"Stream-ready file created: {output_path}")
            return output_path
        else:
            logger.error("Failed to create stream-ready file")
            return None 