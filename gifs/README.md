# GIFs Directory

This directory is for storing GIF files that you want to transcode and stream with Minicast.

## Adding GIFs

1. **Download a GIF** from sources like:
   - [Giphy](https://giphy.com/)
   - [Tenor](https://tenor.com/)
   - [Imgur](https://imgur.com/)
   - Create your own using tools like [GIMP](https://www.gimp.org/) or [Photoshop](https://www.adobe.com/products/photoshop.html)

2. **Place the GIF** in this directory with a descriptive name, for example:
   ```
   gifs/
   ├── reaction_happy.gif
   ├── reaction_sad.gif
   ├── meme_dancing.gif
   └── example.gif
   ```

3. **Use the GIF** in your Minicast workflow:
   ```bash
   # Transcode the GIF
   python transcode.py gifs/reaction_happy.gif output.mp4 --stream-ready
   
   # Start streaming server
   python server.py --input streams/reaction_happy_stream.mp4 --port 554
   ```

## Recommended GIF Specifications

For optimal performance with Minicast, consider these specifications:

- **Duration**: 2-5 seconds (3 seconds is ideal)
- **Resolution**: 320x240 or smaller (will be scaled down anyway)
- **File size**: Under 5MB (smaller is better)
- **Format**: Standard GIF format
- **Content**: Simple animations work best (avoid complex scenes)

## Example Workflow

```bash
# 1. Add a GIF to this directory
cp ~/Downloads/my_reaction.gif gifs/

# 2. Transcode it for streaming
python transcode.py gifs/my_reaction.gif output.mp4 --stream-ready

# 3. Start the streaming server
python server.py --input streams/my_reaction_stream.mp4 --port 554

# 4. Connect with VLC
# Open VLC → Media → Open Network Stream → rtsp://localhost:554/minicast
```

## Tips

- **Test with small GIFs first** to verify your setup
- **Use descriptive filenames** to easily identify your content
- **Keep backups** of your original GIFs
- **Consider bandwidth** - smaller GIFs work better in low-bandwidth scenarios

## Sample GIFs

If you need sample GIFs for testing, you can download some from:
- [Giphy's trending page](https://giphy.com/trending-gifs)
- [Tenor's popular GIFs](https://tenor.com/trending)
- [Imgur's GIF section](https://imgur.com/gallery/gif)

Remember to respect copyright and only use GIFs you have permission to use or that are in the public domain. 