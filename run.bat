@echo off
:: Auto-setup and run menu_mp3_downloader_blink.py on Windows

cd /d %~dp0

echo [1/5] Checking if venv exists...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo [2/5] Activating venv...
call venv\Scripts\activate

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo [5/5] Running program...
python menu_mp3_downloader_blink.py

pause
