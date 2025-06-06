# Multiple Window Video Player

Two modes supported:

**(1)Single Video Mode**: A video file can be played in multiple windows at the same time.

**(2)Multi Video Mode**: Multiple video files can be played independently.

The player program is on the basis of **VLC**(https://www.videolan.org/vlc) and **PyQt5**, so make sure VLC and PyQt5 have been installed before running this program.

```
pip install PyQt5 vlc
```

And change the **vlc_path** value in **play.conf** if necessary.

```
vlc_path = C:\Program Files\VideoLAN\VLC
```

**Usage**:

```
python play.py
```


Single video mode screenshot:

![single video mode](/assets/single.png)

Multi video mode screenshot:

![multi video mode](/assets/multi.png)



**WARNING**: VLC is such tough a memory monster that an instance of VLC may occupy 150MB memory.So, if you watch 4 or more video files at the same time, the player may not work as expected. 

**Don't ask what the program does, it's just abstract nonsense**
