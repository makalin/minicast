"""
Unit tests for Minicast Server.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from minicast.server import MinicastServer, ClientInfo


class TestMinicastServer:
    """Test cases for MinicastServer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = MinicastServer()
    
    def test_default_config(self):
        """Test default configuration."""
        config = self.server.config
        assert config['rtsp_port'] == 554
        assert config['rtsp_path'] == '/minicast'
        assert config['max_clients'] == 10
        assert config['lag_threshold_ms'] == 200
        assert config['catch_up_scale'] == 2.0
    
    def test_client_info_dataclass(self):
        """Test ClientInfo dataclass."""
        now = datetime.now()
        client = ClientInfo(
            client_id="test_client",
            ip_address="127.0.0.1",
            port=8080,
            connected_at=now,
            last_activity=now
        )
        
        assert client.client_id == "test_client"
        assert client.ip_address == "127.0.0.1"
        assert client.port == 8080
        assert client.bytes_sent == 0
        assert client.frames_sent == 0
        assert client.lag_detected is False
        assert client.catch_up_mode is False
    
    @patch('os.path.exists')
    def test_validate_input_file_exists(self, mock_exists):
        """Test input file validation when file exists."""
        mock_exists.return_value = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"streams": [{"codec_type": "video"}]}'
            )
            
            result = self.server.validate_input_file('test.mp4')
            assert result is True
    
    @patch('os.path.exists')
    def test_validate_input_file_not_exists(self, mock_exists):
        """Test input file validation when file doesn't exist."""
        mock_exists.return_value = False
        
        result = self.server.validate_input_file('nonexistent.mp4')
        assert result is False
    
    @patch('os.path.exists')
    def test_validate_input_file_no_video_stream(self, mock_exists):
        """Test input file validation when no video stream exists."""
        mock_exists.return_value = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"streams": [{"codec_type": "audio"}]}'
            )
            
            result = self.server.validate_input_file('test.mp3')
            assert result is False
    
    def test_add_client(self):
        """Test adding a client."""
        self.server.add_client("test_client", "127.0.0.1", 8080)
        
        assert "test_client" in self.server.clients
        client = self.server.clients["test_client"]
        assert client.ip_address == "127.0.0.1"
        assert client.port == 8080
    
    def test_add_client_max_limit(self):
        """Test adding client when max limit is reached."""
        # Set max clients to 1
        self.server.config['max_clients'] = 1
        
        # Add first client
        self.server.add_client("client1", "127.0.0.1", 8080)
        assert len(self.server.clients) == 1
        
        # Try to add second client
        self.server.add_client("client2", "127.0.0.2", 8081)
        assert len(self.server.clients) == 1  # Should not add second client
    
    def test_remove_client(self):
        """Test removing a client."""
        # Add a client first
        self.server.add_client("test_client", "127.0.0.1", 8080)
        assert "test_client" in self.server.clients
        
        # Remove the client
        self.server.remove_client("test_client")
        assert "test_client" not in self.server.clients
    
    def test_update_client_activity(self):
        """Test updating client activity."""
        # Add a client first
        self.server.add_client("test_client", "127.0.0.1", 8080)
        
        # Update activity
        self.server.update_client_activity("test_client", bytes_sent=1024, frames_sent=10)
        
        client = self.server.clients["test_client"]
        assert client.bytes_sent == 1024
        assert client.frames_sent == 10
    
    def test_update_client_activity_nonexistent(self):
        """Test updating activity for nonexistent client."""
        # Should not raise an exception
        self.server.update_client_activity("nonexistent", bytes_sent=1024)
    
    def test_get_client_stats(self):
        """Test getting client statistics."""
        # Add a client
        self.server.add_client("test_client", "127.0.0.1", 8080)
        self.server.update_client_activity("test_client", bytes_sent=1024, frames_sent=10)
        
        stats = self.server.get_client_stats()
        assert stats['total_clients'] == 1
        assert len(stats['clients']) == 1
        
        client_stats = stats['clients'][0]
        assert client_stats['id'] == "test_client"
        assert client_stats['ip'] == "127.0.0.1"
        assert client_stats['bytes_sent'] == 1024
        assert client_stats['frames_sent'] == 10
    
    @patch('json.dump')
    @patch('builtins.open', create=True)
    def test_save_stats(self, mock_open, mock_dump):
        """Test saving client statistics."""
        # Add a client
        self.server.add_client("test_client", "127.0.0.1", 8080)
        
        # Save stats
        self.server._save_stats()
        
        mock_open.assert_called_once_with("client_stats.json", 'w')
        mock_dump.assert_called_once()
    
    @patch('json.load')
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_load_stats(self, mock_open, mock_exists, mock_load):
        """Test loading client statistics."""
        mock_exists.return_value = True
        mock_load.return_value = {
            "test_client": {
                "ip_address": "127.0.0.1",
                "connected_at": "2023-01-01T00:00:00",
                "bytes_sent": 1024,
                "frames_sent": 10,
                "lag_detected": False,
                "catch_up_mode": False
            }
        }
        
        self.server._load_stats()
        
        mock_open.assert_called_once_with("client_stats.json", 'r')
        mock_load.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__]) 