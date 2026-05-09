#!/usr/bin/env python3
"""
Playlist2txt.py
Spotify プレイリストのリンクから、トラック情報（タイトル・アーティスト・アルバム）を
テキストファイルに出力するスクリプト。

使い方:
    python Playlist2txt.py <playlist_url> [output_file] [--text]

オプション:
    --text   詳細形式（タイトル・アーティスト・アルバムを個別行）で出力する。
             省略時はコンパクト形式（番号. タイトル (アーティスト)）で出力。

例:
    # コンパクト形式（デフォルト）
    python Playlist2txt.py https://open.spotify.com/playlist/xxxxx
    python Playlist2txt.py https://open.spotify.com/playlist/xxxxx output.txt

    # 詳細形式
    python Playlist2txt.py https://open.spotify.com/playlist/xxxxx --text
    python Playlist2txt.py https://open.spotify.com/playlist/xxxxx output.txt --text

事前準備:
    1. https://developer.spotify.com/dashboard でアプリを作成し、
       Client ID と Client Secret を取得してください。
       ※ Redirect URI には http://127.0.0.1:8888/callback を入力してください。
         （http://localhost:8888/callback は登録できないため NG）
    2. 環境変数に設定:
         Windows:
           set SPOTIFY_CLIENT_ID=your_client_id
           set SPOTIFY_CLIENT_SECRET=your_client_secret
         Mac/Linux:
           export SPOTIFY_CLIENT_ID=your_client_id
           export SPOTIFY_CLIENT_SECRET=your_client_secret
    3. 必要ライブラリのインストール:
         pip install spotipy

    ※ 初回実行時にブラウザが開き、Spotify へのログインと権限承認が求められます。
       承認後はトークンがキャッシュ（.cache ファイル）に保存されるため、
       2回目以降はブラウザ認証は不要です。
"""

import sys
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 必要なスコープ（公開・非公開プレイリストの読み取り）
SCOPES = "playlist-read-private playlist-read-collaborative"
REDIRECT_URI = "http://127.0.0.1:8888/callback"


def extract_playlist_id(url: str) -> str:
    """Spotify プレイリスト URL からプレイリスト ID を抽出する。"""
    match = re.search(r"playlist/([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"有効な Spotify プレイリスト URL ではありません: {url}")
    return match.group(1)


def get_spotify_client() -> spotipy.Spotify:
    """環境変数から認証情報を読み取り Spotify クライアントを返す。"""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("エラー: 環境変数 SPOTIFY_CLIENT_ID と SPOTIFY_CLIENT_SECRET を設定してください。")
        print()
        print("  Spotify Developer Dashboard でアプリを作成し、認証情報を取得:")
        print("  https://developer.spotify.com/dashboard")
        print()
        print("  Windows の場合:")
        print("    set SPOTIFY_CLIENT_ID=your_client_id")
        print("    set SPOTIFY_CLIENT_SECRET=your_client_secret")
        sys.exit(1)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def fetch_all_tracks(sp: spotipy.Spotify, playlist_id: str) -> list[dict]:
    """プレイリスト内の全トラックを取得する（ページネーション対応）。"""
    tracks = []
    results = sp.playlist_items(playlist_id)

    while results:
        for item in results.get("items", []):
            # 新しい API レスポンス形式: "item" キーにトラック情報が入っている
            # 古い形式の "track" キーにも対応（フォールバック）
            track = item.get("item") or item.get("track")
            if not track or track.get("type") != "track":
                continue  # エピソード（Podcast）や削除済みをスキップ

            title = track.get("name", "不明")
            artists = ", ".join(a["name"] for a in track.get("artists", []))
            album = track.get("album", {}).get("name", "不明")

            tracks.append({
                "title": title,
                "artist": artists,
                "album": album,
            })

        results = sp.next(results) if results.get("next") else None

    return tracks


def format_compact(playlist_name: str, tracks: list[dict], playlist_url: str) -> str:
    """コンパクト形式: プレイリスト名、番号付きトラック一覧、URL。"""
    width = len(str(len(tracks)))  # 曲数に応じてナンバリング幅を揃える
    lines = [playlist_name]
    lines.append(playlist_url)
    for i, t in enumerate(tracks, start=1):
        lines.append(f"{i:>{width}}.{t['title']} ({t['artist']})")
    return "\n".join(lines)


def format_verbose(playlist_name: str, tracks: list[dict]) -> str:
    """詳細形式: タイトル・アーティスト・アルバムを個別行で表示。"""
    lines = []
    lines.append(f"プレイリスト: {playlist_name}")
    lines.append(f"トラック数: {len(tracks)}")
    lines.append("=" * 60)
    lines.append("")
    for i, t in enumerate(tracks, start=1):
        lines.append(f"[{i:>3}] {t['title']}")
        lines.append(f"       アーティスト : {t['artist']}")
        lines.append(f"       アルバム     : {t['album']}")
        lines.append("")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("使い方: python Playlist2txt.py <playlist_url> [output_file] [--text]")
        print()
        print("  --text   詳細形式（タイトル・アーティスト・アルバム）で出力")
        print("           省略時はコンパクト形式で出力")
        print()
        print("例:")
        print("  python Playlist2txt.py https://open.spotify.com/playlist/xxxxx")
        print("  python Playlist2txt.py https://open.spotify.com/playlist/xxxxx output.txt")
        print("  python Playlist2txt.py https://open.spotify.com/playlist/xxxxx --text")
        print("  python Playlist2txt.py https://open.spotify.com/playlist/xxxxx output.txt --text")
        sys.exit(0)

    # --text フラグを取り出す
    verbose = "--text" in args
    args = [a for a in args if a != "--text"]

    playlist_url = args[0]
    output_file = args[1] if len(args) >= 2 else None

    # プレイリスト ID を取得
    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    print(f"プレイリスト ID: {playlist_id}")
    print("Spotify API に接続中...")
    print("※ 初回はブラウザが開きます。Spotify にログインして承認してください。")

    sp = get_spotify_client()

    playlist_info = sp.playlist(playlist_id, fields="name")
    playlist_name = playlist_info.get("name", playlist_id)

    print(f"プレイリスト名: {playlist_name}")
    print("トラック情報を取得中...")

    tracks = fetch_all_tracks(sp, playlist_id)
    print(f"{len(tracks)} 件のトラックを取得しました。")

    # 出力テキストを生成
    if verbose:
        output_text = format_verbose(playlist_name, tracks)
    else:
        output_text = format_compact(playlist_name, tracks, playlist_url)

    # 出力先を決定
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"\n結果を保存しました: {output_file}")
    else:
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", playlist_name)
        auto_file = f"{safe_name}.txt"
        with open(auto_file, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"\n結果を保存しました: {auto_file}")

    # コンソールにも出力
    print()
    print(output_text)


if __name__ == "__main__":
    main()
