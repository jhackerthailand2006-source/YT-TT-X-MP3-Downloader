#!/bin/bash
# Auto-setup and run menu_mp3_downloader_blink.py

set -e

WORKDIR="$(dirname "$0")"
cd "$WORKDIR"

echo ">>> [1/6] สร้าง virtual environment (venv) ถ้ายังไม่มี..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo ">>> [2/6] เปิดใช้งาน venv..."
source venv/bin/activate

echo ">>> [3/6] อัปเดต pip..."
python -m pip install --upgrade pip

echo ">>> [4/6] ติดตั้ง dependencies จาก requirements.txt..."
pip install -r requirements.txt

echo ">>> [5/6] ตรวจสอบ ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ยังไม่พบ ffmpeg ติดตั้งผ่าน apt ..."
    sudo apt update
    sudo apt install -y ffmpeg
else
    echo "พบ ffmpeg แล้ว ✅"
fi

echo ">>> [6/6] รันโปรแกรม..."
python menu_mp3_downloader_blink.py
