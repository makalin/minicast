# Minicast API Documentation

## Overview

Minicast provides a Python library for ultra-low-bandwidth RTSP streaming of reaction GIFs. The library consists of two main components:

1. **MinicastTranscoder** - Converts GIFs to optimized H.264 streams
2. **MinicastServer** - RTSP server with client tracking and adaptive streaming

## Installation

```bash
pip install minicast
```

## Quick Start

```python
from minicast import MinicastTranscoder, MinicastServer

# Transcode a GIF
transcoder = MinicastTranscoder()
output_path = transcoder.create_stream_ready_file("input.gif")

# Start streaming server
server = MinicastServer()
server.start(output_path)
```

## MinicastTranscoder

The `MinicastTranscoder` class handles conversion of GIF files to low-bandwidth H.264 streams optimized for RTSP broadcasting.

### Constructor

```python
MinicastTranscoder(config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `config` (Optional[Dict]): Custom transcoding configuration

### Default Configuration

```python
{
    'resolution': '160x120',
    'fps': 2,
    'bitrate': '50k',
    'profile': 'baseline',
    'level': '3.0',
    'keyframe_interval': 30,
    'gop_size': 4,
    'preset': 'ultrafast',
    'crf': 28,
    'audio': False,
    'loop': True,
    'duration': 3
}
```

### Methods

#### `transcode_gif(input_path: str, output_path: str, custom_config: Optional[Dict] = None) -> bool`

Transcodes a GIF file to H.264 MP4 format.

**Parameters:**
- `input_path` (str): Path to input GIF file
- `output_path` (str): Path for output MP4 file
- `custom_config` (Optional[Dict]): Custom configuration override

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
transcoder = MinicastTranscoder()
success = transcoder.transcode_gif("input.gif", "output.mp4", {
    'resolution': '240x180',
    'fps': 3,
    'bitrate': '75k'
})
```

#### `create_stream_ready_file(input_path: str, output_dir: str = "streams") -> Optional[str]`

Creates a stream-ready file optimized for RTSP broadcasting.

**Parameters:**
- `input_path` (str): Path to input GIF file
- `output_dir` (str): Directory for output files

**Returns:**
- `Optional[str]`: Path to created file, or None if failed

**Example:**
```python
transcoder = MinicastTranscoder()
output_path = transcoder.create_stream_ready_file("input.gif", "my_streams")
```

#### `get_gif_info(input_path: str) -> Dict[str, Any]`

Extracts information about a GIF file.

**Parameters:**
- `input_path` (str): Path to GIF file

**Returns:**
- `Dict[str, Any]`: File information including duration, dimensions, FPS, and size

**Example:**
```python
transcoder = MinicastTranscoder()
info = transcoder.get_gif_info("input.gif")
print(f"Duration: {info['duration']}s")
print(f"Resolution: {info['width']}x{info['height']}")
print(f"FPS: {info['fps']}")
```

## MinicastServer

The `MinicastServer` class provides RTSP streaming with client tracking and adaptive streaming capabilities.

### Constructor

```python
MinicastServer(config: Optional[Dict] = None)
```

**Parameters:**
- `config` (Optional[Dict]): Custom server configuration

### Default Configuration

```python
{
    'rtsp_port': 554,
    'rtsp_path': '/minicast',
    'max_clients': 10,
    'lag_threshold_ms': 200,
    'catch_up_scale': 2.0,
    'stats_interval': 5,
    'ffmpeg_binary': 'ffmpeg',
    'enable_catch_up': True,
    'byte_tracking': True
}
```

### Methods

#### `start(input_file: str) -> bool`

Starts the RTSP streaming server.

**Parameters:**
- `input_file` (str): Path to input MP4 file

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
server = MinicastServer()
success = server.start("stream.mp4")
```

#### `stop()`

Stops the RTSP streaming server.

**Example:**
```python
server.stop()
```

#### `add_client(client_id: str, ip_address: str, port: int)`

Adds a new client to tracking.

**Parameters:**
- `client_id` (str): Unique client identifier
- `ip_address` (str): Client IP address
- `port` (int): Client port

**Example:**
```python
server.add_client("client_001", "192.168.1.100", 8080)
```

#### `remove_client(client_id: str)`

Removes a client from tracking.

**Parameters:**
- `client_id` (str): Client identifier to remove

**Example:**
```python
server.remove_client("client_001")
```

#### `update_client_activity(client_id: str, bytes_sent: int = 0, frames_sent: int = 0)`

Updates client activity and checks for lag.

**Parameters:**
- `client_id` (str): Client identifier
- `bytes_sent` (int): Number of bytes sent to client
- `frames_sent` (int): Number of frames sent to client

**Example:**
```python
server.update_client_activity("client_001", bytes_sent=1024, frames_sent=5)
```

#### `get_client_stats() -> Dict`

Gets current client statistics.

**Returns:**
- `Dict`: Client statistics including total clients and per-client data

**Example:**
```python
stats = server.get_client_stats()
print(f"Active clients: {stats['total_clients']}")
for client in stats['clients']:
    print(f"Client {client['id']}: {client['bytes_sent']} bytes")
```

## ClientInfo Dataclass

The `ClientInfo` dataclass represents information about a connected RTSP client.

### Fields

- `client_id` (str): Unique client identifier
- `ip_address` (str): Client IP address
- `port` (int): Client port
- `connected_at` (datetime): Connection timestamp
- `last_activity` (datetime): Last activity timestamp
- `bytes_sent` (int): Total bytes sent to client
- `frames_sent` (int): Total frames sent to client
- `lag_detected` (bool): Whether lag was detected
- `catch_up_mode` (bool): Whether client is in catch-up mode
- `catch_up_start` (Optional[datetime]): Catch-up start timestamp
- `stream_scale` (float): Current stream scale factor

## Configuration Examples

### Ultra-Low Bandwidth Configuration

```python
ultra_low_config = {
    'resolution': '120x90',
    'fps': 1,
    'bitrate': '20k',
    'crf': 35
}

transcoder = MinicastTranscoder(ultra_low_config)
```

### High Quality Configuration

```python
high_quality_config = {
    'resolution': '320x240',
    'fps': 5,
    'bitrate': '100k',
    'crf': 23
}

transcoder = MinicastTranscoder(high_quality_config)
```

### Custom Server Configuration

```python
server_config = {
    'rtsp_port': 8554,
    'rtsp_path': '/my_stream',
    'max_clients': 50,
    'lag_threshold_ms': 100,
    'catch_up_scale': 1.5,
    'stats_interval': 2
}

server = MinicastServer(server_config)
```

## Error Handling

The library raises appropriate exceptions for common errors:

```python
try:
    transcoder = MinicastTranscoder()
    transcoder.transcode_gif("input.gif", "output.mp4")
except RuntimeError as e:
    print(f"FFmpeg not available: {e}")
except Exception as e:
    print(f"Transcoding failed: {e}")
```

## Best Practices

1. **Always validate input files** before transcoding
2. **Use appropriate configurations** for your target bandwidth
3. **Monitor client statistics** to optimize performance
4. **Handle exceptions gracefully** in production code
5. **Use stream-ready files** for optimal RTSP performance

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg and ensure it's in your PATH
2. **Port already in use**: Use a different RTSP port
3. **Permission denied**: Ensure write permissions for output directories
4. **Invalid input file**: Verify the input file is a valid GIF

### Debug Mode

Enable verbose logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
``` 