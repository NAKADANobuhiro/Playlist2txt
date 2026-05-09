# Playlist2txt

Spotify のプレイリスト URL から、トラック情報（タイトル・アーティスト・アルバム）を
テキストファイルに出力する Python スクリプトです。

## 出力形式

### コンパクト形式（デフォルト）

```
RHYMESTER宇多丸の 今月の聴く『マブ論』！！ 2026年6月号  アトロク2
 1.GOODBYE (lyrical school)
 2.SOUL LOVER (feat. 山添みなみ)(FAREWELL, MY L.u.v, 山添みなみ)
 3.Bias Wrecker (feat. 山添みなみ)(FAREWELL, MY L.u.v, 山添みなみ)
...
https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx
```

### 詳細形式（`--text`）

```
プレイリスト: RHYMESTER宇多丸の 今月の聴く『マブ論』！！ 2026年6月号  アトロク2
トラック数: 16
============================================================

[  1] GOODBYE
       アーティスト : lyrical school
       アルバム     : GOODBYE
...
```

## セットアップ

### 1. ライブラリのインストール

```
pip install spotipy
```

### 2. Spotify API アプリの作成

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) にアクセス
2. 「Create app」でアプリを新規作成
3. 「Redirect URIs」に以下を入力して保存:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` は登録できないため、必ず `127.0.0.1` を使うこと
4. 「Settings」画面で **Client ID** と **Client Secret** を確認

### 3. 環境変数の設定

**Windows（コマンドプロンプト）:**
```
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Windows（PowerShell）:**
```
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
```

**Mac / Linux:**
```
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

## 使い方

```
python Playlist2txt.py <playlist_url> [output_file] [--text]
```

| 引数 | 説明 |
|------|------|
| `playlist_url` | Spotify プレイリストの URL（必須） |
| `output_file` | 出力ファイル名（省略時はプレイリスト名.txt を自動生成） |
| `--text` | 詳細形式で出力（省略時はコンパクト形式） |

### 実行例

```
# コンパクト形式、ファイル名自動
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx

# コンパクト形式、ファイル名指定
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx output.txt

# 詳細形式
python Playlist2txt.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx output.txt --text
```

### 初回実行時

ブラウザが自動で開き、Spotify へのログインと権限承認が求められます。
承認後はトークンが `.cache` ファイルに保存され、2 回目以降はブラウザ認証不要です。

## 動作環境

- Python 3.10 以上
- spotipy 2.x
