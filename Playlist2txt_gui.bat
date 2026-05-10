@echo off
cd /d "%~dp0"

REM ============================================================
REM  Playlist2txt_gui.bat
REM  Double-click to launch the Playlist2txt GUI.
REM ============================================================

REM --- Load credentials ---
if not exist "spotify_credentials.bat" (
    echo [ERROR] spotify_credentials.bat not found.
    echo         Please create it in the same folder.
    pause
    exit /b 1
)
call spotify_credentials.bat

REM --- Check if credentials are still placeholder values ---
if "%SPOTIFY_CLIENT_ID%"=="your_client_id_here" (
    echo [ERROR] SPOTIFY_CLIENT_ID is not set in spotify_credentials.bat.
    echo         Opening spotify_credentials.bat in Notepad...
    start notepad spotify_credentials.bat
    pause
    exit /b 1
)
if "%SPOTIFY_CLIENT_SECRET%"=="your_client_secret_here" (
    echo [ERROR] SPOTIFY_CLIENT_SECRET is not set in spotify_credentials.bat.
    echo         Opening spotify_credentials.bat in Notepad...
    start notepad spotify_credentials.bat
    pause
    exit /b 1
)

REM --- Check Python is available ---
where python > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python.
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Install dependencies if missing ---
python -c "import spotipy" > nul 2>&1
if errorlevel 1 (
    echo Installing required libraries...
    pip install spotipy
    if errorlevel 1 (
        echo [ERROR] Failed to install libraries.
        pause
        exit /b 1
    )
    echo Done.
)

REM --- Launch GUI ---
python Playlist2txt_gui.py

REM --- Pause only on error ---
if errorlevel 1 (
    echo.
    echo [ERROR] Script exited with an error.
    pause
)
