#!/usr/bin/env python3
"""
Playlist2txt_gui.py
Playlist2txt の GUI 起動ランチャー。
URL 入力ポップアップを表示し、プレイリスト名.txt を生成する。

使い方:
    python Playlist2txt_gui.py
    （コマンドライン引数は不要）
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Playlist2txt.py と同じディレクトリを検索パスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Playlist2txt import (
        extract_playlist_id,
        get_spotify_client,
        fetch_all_tracks,
        format_compact,
        format_verbose,
    )
except ImportError as e:
    print(f"Error: Failed to import Playlist2txt.py: {e}")
    sys.exit(1)

import re


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Playlist2txt")
        self.resizable(False, False)
        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_ui(self):
        pad = {"padx": 12, "pady": 5}

        # --- URL 入力 ---
        tk.Label(self, text="Spotify プレイリスト URL:", anchor="w").grid(
            row=0, column=0, columnspan=3, sticky="w", **pad
        )
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(self, textvariable=self.url_var, width=65)
        url_entry.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 6), sticky="ew")
        url_entry.bind("<Return>", lambda e: self.run())

        # --- 出力フォルダ ---
        tk.Label(self, text="出力フォルダ:", anchor="w").grid(
            row=2, column=0, columnspan=3, sticky="w", **pad
        )
        self.outdir_var = tk.StringVar(value=os.path.dirname(os.path.abspath(__file__)))
        tk.Entry(self, textvariable=self.outdir_var, width=65).grid(
            row=3, column=0, columnspan=3, padx=12, pady=(0, 6), sticky="ew"
        )

        # --- 出力形式 ---
        self.format_var = tk.StringVar(value="compact")
        fmt_frame = tk.Frame(self)
        fmt_frame.grid(row=4, column=0, columnspan=3, padx=12, pady=(0, 6), sticky="w")
        tk.Label(fmt_frame, text="出力形式:").pack(side="left")
        tk.Radiobutton(
            fmt_frame, text="コンパクト（番号. タイトル (アーティスト)）",
            variable=self.format_var, value="compact"
        ).pack(side="left", padx=(8, 0))
        tk.Radiobutton(
            fmt_frame, text="詳細（タイトル・アーティスト・アルバム）",
            variable=self.format_var, value="verbose"
        ).pack(side="left", padx=(16, 0))

        # --- 実行ボタン ---
        self.run_btn = tk.Button(
            self, text="生成", width=12, command=self.run,
            bg="#1DB954", fg="white", font=("", 10, "bold"),
            relief="flat", cursor="hand2"
        )
        self.run_btn.grid(row=5, column=0, padx=12, pady=8, sticky="w")

        self.status_var = tk.StringVar(value="URL を入力して「生成」を押してください。")
        tk.Label(self, textvariable=self.status_var, fg="gray", anchor="w").grid(
            row=5, column=1, columnspan=2, padx=4, pady=8, sticky="w"
        )

        # --- ログ / 出力プレビュー ---
        tk.Label(self, text="ログ / 出力プレビュー:", anchor="w").grid(
            row=6, column=0, columnspan=3, sticky="w", padx=12
        )
        self.log = scrolledtext.ScrolledText(
            self, width=72, height=20, state="disabled",
            font=("Courier", 9), bg="#1a1a1a", fg="#d0d0d0",
            insertbackground="white"
        )
        self.log.grid(row=7, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="nsew")

    # ── ログ出力 ──────────────────────────────────────────────

    def log_write(self, msg: str):
        def _write():
            self.log.config(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.config(state="disabled")
        self.after(0, _write)

    # ── 実行 ─────────────────────────────────────────────────

    def run(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "URL を入力してください。")
            return

        outdir = self.outdir_var.get().strip()
        if outdir and not os.path.isdir(outdir):
            messagebox.showerror("Error", f"出力フォルダが存在しません:\n{outdir}")
            return

        self.run_btn.config(state="disabled", text="処理中…")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self.status_var.set("処理中…")

        verbose = (self.format_var.get() == "verbose")
        thread = threading.Thread(
            target=self._worker, args=(url, outdir, verbose), daemon=True
        )
        thread.start()

    def _worker(self, url: str, outdir: str, verbose: bool):
        try:
            self._generate(url, outdir, verbose)
        except Exception as e:
            self.log_write(f"\n[ERROR] {e}")
            self.after(0, lambda: messagebox.showerror("エラー", str(e)))
            self.after(0, lambda: self.status_var.set("エラーが発生しました。"))
        finally:
            self.after(0, lambda: self.run_btn.config(state="normal", text="生成"))

    def _generate(self, url: str, outdir: str, verbose: bool):
        self.log_write(f"URL: {url}")

        try:
            playlist_id = extract_playlist_id(url)
        except ValueError as e:
            raise ValueError(f"有効な Spotify プレイリスト URL ではありません:\n{url}") from e

        self.log_write(f"Playlist ID: {playlist_id}")
        self.log_write("Connecting to Spotify API...")

        sp = get_spotify_client()

        playlist_info = sp.playlist(playlist_id, fields="name")
        playlist_name = playlist_info.get("name", playlist_id)
        self.log_write(f"Playlist: {playlist_name}")
        self.log_write("Fetching tracks...")

        tracks = fetch_all_tracks(sp, playlist_id)
        self.log_write(f"{len(tracks)} tracks found.")

        # テキスト生成
        if verbose:
            output_text = format_verbose(playlist_name, tracks)
        else:
            output_text = format_compact(playlist_name, tracks, url)

        # 保存
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", playlist_name)
        filename = f"{safe_name}.txt"
        out_path = os.path.join(outdir, filename) if outdir else filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_text)

        self.log_write(f"\nSaved: {out_path}")
        self.log_write("-" * 60)
        self.log_write(output_text)

        self.after(0, lambda: self.status_var.set(f"完了: {filename}"))
        self.after(0, lambda: messagebox.showinfo(
            "完了",
            f"保存しました:\n\n{out_path}"
        ))


def main():
    if not os.environ.get("SPOTIFY_CLIENT_ID") or not os.environ.get("SPOTIFY_CLIENT_SECRET"):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Environment variables not set",
            "Please set the following environment variables before running:\n\n"
            "  SPOTIFY_CLIENT_ID\n"
            "  SPOTIFY_CLIENT_SECRET\n\n"
            "Windows (Command Prompt):\n"
            "  set SPOTIFY_CLIENT_ID=your_client_id\n"
            "  set SPOTIFY_CLIENT_SECRET=your_client_secret"
        )
        root.destroy()
        sys.exit(1)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
