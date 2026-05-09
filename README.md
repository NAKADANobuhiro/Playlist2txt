# Playlist2txt

A Python script that exports track information (title, artist, album) from a Spotify playlist URL to a text file.

[日本語版 README はこちら](README.ja.md)

## Output Formats

### Compact format (default)

```
RHYMESTER Udamaru's "Maburon" Listening Picks!! June 2026 — Atrok2
 1.GOODBYE (lyrical school)
 2.SOUL LOVER (feat. Minami Yamazoe)(FAREWELL, MY L.u.v, Minami Yamazoe)
 3.Bias Wrecker (feat. Minami Yamazoe)(FAREWELL, MY L.u.v, Minami Yamazoe)
...
https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx
```

### Verbose format (`--text`)

```
Playlist: RHYMESTER Udamaru's "Maburon" Listening Picks!! June 2026 — Atrok2
Tracks: 16
============================================================

[  1] GOODBYE
       Artist : lyrical school
       Album  : GOODBYE
...
```

## Setup

### 1. Install dependencies

```
pip install spotipy
```

### 2. Create a Spotify API app

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app
2. Under **Redirect URIs**, add the following and save:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` does NOT work — always use `127.0.0.1`
3. Note your **Client ID** and **Client Secret** from the Settings page

### 3. Set environment variables

**Windows (Command Prompt):**
```
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Windows (PowerShell):**
```
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
```

**Mac / Linux:**
```
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Usage

```
python Playlist2txt.py <playlist_url> [output_file] [--text]
```

| Argument | Description |
|----------|-------------|
| `playlist_url` | Spotify playlist URL (required) |
| `output_file` | Output filename (defaults to playlist name + `.txt`) |
| `--text` | Use verbose format (defaults to compact format) |

### Examples

```
# Compact format, auto filename
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx

# Compact format, custom filename
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx output.txt

# Verbose format
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx output.txt --text
```

### First run

A browser window will open for Spotify login and permission approval.
After authorization, the token is cached in `.cache` — subsequent runs will not require browser sign-in.

## Requirements

- Python 3.10+
- spotipy 2.x
