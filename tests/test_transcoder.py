"""
Unit tests for Minicast Transcoder.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from minicast.transcoder import MinicastTranscoder


class TestMinicastTranscoder:
    """Test cases for MinicastTranscoder class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transcoder = MinicastTranscoder()
    
    def test_default_config(self):
        """Test default configuration."""
        config = self.transcoder.config
        assert config['resolution'] == '160x120'
        assert config['fps'] == 2
        assert config['bitrate'] == '50k'
        assert config['profile'] == 'baseline'
    
    @patch('subprocess.run')
    def test_validate_ffmpeg_success(self, mock_run):
        """Test successful FFmpeg validation."""
        mock_run.return_value = MagicMock(returncode=0)
        self.transcoder._validate_ffmpeg()
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_validate_ffmpeg_failure(self, mock_run):
        """Test FFmpeg validation failure."""
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="FFmpeg not available"):
            self.transcoder._validate_ffmpeg()
    
    @patch('subprocess.run')
    def test_get_gif_info(self, mock_run):
        """Test GIF info extraction."""
        mock_info = {
            'format': {'duration': '3.0', 'size': '1024'},
            'streams': [{
                'codec_type': 'video',
                'width': 320,
                'height': 240,
                'r_frame_rate': '10/1'
            }]
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"format": {"duration": "3.0", "size": "1024"}, "streams": [{"codec_type": "video", "width": 320, "height": 240, "r_frame_rate": "10/1"}]}'
        )
        
        info = self.transcoder.get_gif_info('test.gif')
        assert info['duration'] == 3.0
        assert info['width'] == 320
        assert info['height'] == 240
        assert info['fps'] == 10.0
    
    def test_parse_fps(self):
        """Test FPS parsing."""
        assert self.transcoder._parse_fps('10/1') == 10.0
        assert self.transcoder._parse_fps('30/1') == 30.0
        assert self.transcoder._parse_fps('15/2') == 7.5
        assert self.transcoder._parse_fps('invalid') == 0
    
    def test_build_video_filter(self):
        """Test video filter building."""
        config = {
            'resolution': '160x120',
            'fps': 2,
            'duration': 3
        }
        filter_str = self.transcoder._build_video_filter(config)
        assert 'scale=160x120' in filter_str
        assert 'fps=2' in filter_str
        assert 'trim=duration=3' in filter_str
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_transcode_gif_success(self, mock_getsize, mock_exists, mock_run):
        """Test successful GIF transcoding."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch.object(self.transcoder, 'get_gif_info') as mock_info:
            mock_info.return_value = {
                'duration': 3.0,
                'width': 320,
                'height': 240,
                'fps': 10.0,
                'size': 1024
            }
            
            result = self.transcoder.transcode_gif('input.gif', 'output.mp4')
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_transcode_gif_failure(self, mock_run):
        """Test GIF transcoding failure."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg')
        
        with patch.object(self.transcoder, 'get_gif_info') as mock_info:
            mock_info.return_value = {
                'duration': 3.0,
                'width': 320,
                'height': 240,
                'fps': 10.0,
                'size': 1024
            }
            
            result = self.transcoder.transcode_gif('input.gif', 'output.mp4')
            assert result is False
    
    @patch('pathlib.Path.mkdir')
    @patch.object(MinicastTranscoder, 'transcode_gif')
    def test_create_stream_ready_file(self, mock_transcode, mock_mkdir):
        """Test stream-ready file creation."""
        mock_transcode.return_value = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.transcoder.create_stream_ready_file(
                'test.gif', 
                temp_dir
            )
            assert result == os.path.join(temp_dir, 'test_stream.mp4')
            mock_transcode.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__]) 