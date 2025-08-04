# Minicast 🎞️📡  
Ultra-Low-Bandwidth Reaction GIF Channel  

Minicast is a lightweight RTSP-compatible streaming service optimized for broadcasting short, looping reaction GIFs with minimal data usage. Designed for situations where bandwidth is scarce, Minicast cleverly adapts video delivery using advanced transcoding, low-res H.264, and real-time client catch-up mechanics.

## 🚀 Features

- 🔁 Transcodes 3-second GIFs to 160×120 @ 2fps H.264 (baseline profile)
- 🎥 Sends only P-frames after initial I-frame to save bandwidth
- ⏩ Clients falling >200ms behind are automatically sped up (`scale=2.0`) until they catch up
- 📈 Per-client byte tracking for adaptive streaming
- 🔌 RTSP-compatible output, easily viewable in VLC

## 📦 How It Works

1. **GIF Ingestion:** Upload or reference a 3-second reaction GIF.
2. **Transcoding:** GIF is converted to H.264 @ 160x120, 2fps, baseline profile.
3. **Smart Frame Control:** After 1 second, only P-frames are transmitted.
4. **Client Monitoring:** Backend monitors RTSP clients. If any fall behind by >200ms...
5. **Catch-up Mode:** RTSP `PLAY` command issued with `scale=2.0` so clients catch up in real time — no buffering.

## 🛠️ Requirements

- Python 3.9+
- `ffmpeg`
- `OpenRTSP` or `live555` libs
- VLC (for client testing)
- Optional: Docker for isolated deployment

## 🧪 Example Usage

```bash
# Transcode GIF to streaming-ready H.264
python transcode.py input.gif output.mp4

# Start Minicast RTSP server
python server.py --input output.mp4 --port 554

# In VLC
vlc rtsp://localhost:554/minicast
````

## 📡 Architecture

```text
GIF ──▶ Transcoder ──▶ RTSP Server ──▶ Clients
                            ▲
                     Byte Tracking
                            │
                     Catch-up Trigger
```

## 🧠 Use Cases

* Remote meme delivery in low-bandwidth regions
* Twitch/Discord reaction mirrors
* Embedded systems needing efficient video signaling
* Hacky lo-fi "TV" broadcasting

## 🧊 TODO

* [ ] Web UI for uploading & previewing GIFs
* [ ] Client stats dashboard
* [ ] Adaptive bitrate streaming
* [ ] Docker container

## 📄 License

MIT License

---

Crafted with love for the bandwidth-challenged 💾
