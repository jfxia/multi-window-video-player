# Multiple Window Video Player

Two modes supported:

**(1)Single Video Mode**: A video file can be played in multiple windows at the same time.

**(2)Multi Video Mode**: Multiple video files can be played independently.

The player program is on the basis of **VLC**(https://www.videolan.org/vlc) and PyQt5, so make sure VLC and PyQt5 have been installed before running this program.

```
pip install PyQt5 vlc
```

And change the VLC path value in the script to your own installation path if necessary.

```
vlc_path = r'C:\Program Files\VideoLAN\VLC'
```

**Usage**:

```
python play.py
```


Single video mode screenshot:

![single video mode](/assets/single.png)

Multi video mode screenshot:

![multi video mode](/assets/multi.png)
