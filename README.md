# blindtest-builder

## Description

This script allows you to create blindtests from csv files.

The csv file must be formatted the following way:
```
Playlist,TrackNumber,TrackTitle,Artist,YoutubeLink
```

The script is meant to be launched the following way:
```
./blindtest-builder.py file.csv
```

It will download the audio from youtube videos and organize the songs in playlists. To do so, it uses youtube-dl.

Example:
```
SoftPlaylist,1,BeautifulSong,Artist1,https://www.youtube.com/...
JazzPlaylist,1,AmazingSong,Artist1,https://www.youtube.com/...
JazzPlaylist,2,AstonishingSong,Artist2,https://www.youtube.com/...
RockPlaylist,1,RockSong,Artist1,https://www.youtube.com/...
```

The script will create the following files in the current directory:
```
SoftPlaylist.m3u
SoftPlaylist
-- 1.Artist1_-_BeautifulSong.format
JazzPlaylist.m3u
JazzPlaylist
-- 1.Artist1_-_AmazingSong.format
-- 2.Artist2_-_AstonishingSong.format
RockPlaylist.m3u
RockPlaylist
-- 1.Artist1_-_RockSong.format
```

## Requirements

The only requirements are python, eye-d3.

### Mac OS X installation

First install homebrew (see [http://brew.sh/](http://brew.sh/)

```
brew install ffmpeg youtube-dl
```
