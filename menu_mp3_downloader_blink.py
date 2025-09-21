#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Menu MP3 Downloader with COLORED + BLINK ASCII 'J Music' banner
Platforms: YouTube, TikTok, Facebook, X (Twitter), Threads, Instagram
Uses: yt-dlp + ffmpeg
Note: BLINK effect (\033[5m) may not be supported by some terminals (e.g., legacy Windows CMD).
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

# Optional: enable ANSI on Windows if colorama is available (no hard dependency)
def _enable_windows_ansi():
    try:
        import colorama  # type: ignore
        colorama.just_fix_windows_console()
    except Exception:
        # Best-effort; Windows 10+ Terminal usually supports ANSI already
        pass

_enable_windows_ansi()

# ANSI styles
RESET = "\033[0m"
BOLD = "\033[1m"
BLINK = "\033[5m"

FG = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:
    print("ไม่พบไลบรารี yt-dlp\nติดตั้งด้วย: pip install yt-dlp")
    sys.exit(1)

PLATFORMS = {
    "1": "YouTube",
    "2": "TikTok",
    "3": "Facebook",
    "4": "X (Twitter)",
    "5": "Threads",
    "6": "Instagram",
}

def print_banner():
    # Colorful ASCII banner + blinking 'J MUSIC'
    top = FG["magenta"] + "############################################################" + RESET
    mid1 = FG["blue"] + "#                                                          #" + RESET
    line1 = (
        "#   "
        + FG["cyan"] + "JJJJJ " + RESET
        + FG["blue"] + "       MMM   MMM " + RESET
        + FG["green"] + "  U   U " + RESET
        + FG["yellow"] + "  SSSSS " + RESET
        + FG["red"] + "  IIIII " + RESET
        + FG["magenta"] + "  CCCC  " + RESET
        + "#"
    )
    line2 = (
        "#     "
        + FG["cyan"] + "J     " + RESET
        + FG["blue"] + "       M M M M M " + RESET
        + FG["green"] + "  U   U " + RESET
        + FG["yellow"] + "  S     " + RESET
        + FG["red"] + "    I   " + RESET
        + FG["magenta"] + "  C     " + RESET
        + "#"
    )
    line3 = (
        "#     "
        + FG["cyan"] + "J     " + RESET
        + FG["blue"] + "       M  M M  M " + RESET
        + FG["green"] + "  U   U " + RESET
        + FG["yellow"] + "   SSS  " + RESET
        + FG["red"] + "    I   " + RESET
        + FG["magenta"] + "  C     " + RESET
        + "#"
    )
    line4 = (
        "#   "
        + FG["cyan"] + "J J   " + RESET
        + FG["blue"] + "       M   M   M " + RESET
        + FG["green"] + "  U   U " + RESET
        + FG["yellow"] + "      S " + RESET
        + FG["red"] + "    I   " + RESET
        + FG["magenta"] + "  C     " + RESET
        + "#"
    )
    line5 = (
        "#    "
        + FG["cyan"] + "JJJ   " + RESET
        + FG["blue"] + "       M       M " + RESET
        + FG["green"] + "   UUU  " + RESET
        + FG["yellow"] + " SSSSS " + RESET
        + FG["red"] + "  IIIII " + RESET
        + FG["magenta"] + "  CCCC  " + RESET
        + "#"
    )
    brand_text = (
        BOLD
        + FG["white"] + "J" + RESET + " "
        + BOLD + FG["cyan"] + "M" + RESET + " "
        + BOLD + FG["green"] + "U" + RESET + " "
        + BOLD + FG["yellow"] + "S" + RESET + " "
        + BOLD + FG["red"] + "I" + RESET + " "
        + BOLD + FG["magenta"] + "C" + RESET
    )
    brand_line = "#                  " + BLINK + brand_text + RESET + "                      #"

    print()
    print(top)
    print(mid1)
    print(line1)
    print(line2)
    print(line3)
    print(line4)
    print(line5)
    print(mid1)
    print(brand_line)
    print(top)
    print()

def check_ffmpeg() -> bool:
    """ตรวจสอบว่ามี ffmpeg ใน PATH หรือไม่"""
    return shutil.which("ffmpeg") is not None or shutil.which("ffmpeg.exe") is not None

def ask_output_dir() -> Path:
    """ถามโฟลเดอร์ปลายทาง (กด Enter เพื่อใช้โฟลเดอร์ 'downloads')"""
    default_dir = Path.cwd() / "downloads"
    try:
        user_in = input(f"บันทึกไฟล์ลงโฟลเดอร์ไหน? (เว้นว่างใช้ค่าเริ่มต้น: {default_dir}): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nยกเลิก")
        sys.exit(0)
    out_dir = Path(user_in) if user_in else default_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def sanitize_filename(name: str) -> str:
    # เอาอักขระที่อาจมีปัญหาออกแบบง่าย ๆ
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()

def progress_hook(d):
    if d.get('status') == 'downloading':
        # แสดงความคืบหน้าอย่างย่อ
        p = d.get('_percent_str') or ''
        s = d.get('_speed_str') or ''
        eta = d.get('_eta_str') or ''
        sys.stdout.write(f"\rกำลังดาวน์โหลด... {p}  ความเร็ว {s}  เหลือเวลา {eta}   ")
        sys.stdout.flush()
    elif d.get('status') == 'finished':
        print("\nดาวน์โหลดเสร็จ กำลังแปลงเป็น MP3 ...")

def build_ydl_opts(output_dir: Path) -> dict:
    # ตั้งค่าให้เลือกเสียงที่ดีสุด แล้ว extract เป็น mp3 192kbps
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outtmpl = str(output_dir / f"%(title)s_{timestamp}.%(ext)s")
    return {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noprogress": True,           # เราใช้ progress_hook เอง
        "progress_hooks": [progress_hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        # "cookiefile": "cookies.txt",  # ถ้าต้องใช้คุกกี้ให้ยกเลิกคอมเมนต์
        "quiet": True,                # ลด log
        "no_warnings": True,
        "trim_file_name": 200,
    }

def download_mp3(url: str, output_dir: Path) -> Optional[Path]:
    ydl_opts = build_ydl_opts(output_dir)
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # หลัง post-process จะกลายเป็น .mp3
            title = info.get("title") or "audio"
            title = sanitize_filename(title)
            # หาไฟล์ mp3 ที่พึ่งสร้าง (ใช้ไทม์สแตมป์ช่วยลดการชนกันของชื่อ)
            possible = list(output_dir.glob(f"{title}_*.mp3"))
            if not possible:
                # fallback: หาทุก .mp3 ที่อัปเดตล่าสุดในโฟลเดอร์
                possible = sorted(output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
            return possible[0] if possible else None
    except DownloadError as e:
        print(f"\nเกิดข้อผิดพลาดระหว่างดาวน์โหลด: {e}")
    except Exception as e:
        print(f"\nเกิดข้อผิดพลาดไม่คาดคิด: {e}")
    return None

def page_download(platform_key: str):
    print_banner()
    platform_name = PLATFORMS.get(platform_key, "Unknown")
    print(f"=== {platform_name} → โหลด MP3 ===")
    print("[วางลิงก์วิดีโอที่ต้องการ หรือพิมพ์ b เพื่อกลับหน้าแรก]")
    try:
        url = input("> URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nกลับหน้าแรก\n")
        return
    if not url or url.lower() == "b":
        print("กลับหน้าแรก\n")
        return

    # โฟลเดอร์ปลายทาง
    out_dir = ask_output_dir()

    if not check_ffmpeg():
        print("\n⚠️ ยังไม่พบ ffmpeg ในเครื่อง จึงแปลง MP3 ไม่ได้")
        print("โปรดติดตั้ง ffmpeg ให้เรียบร้อยก่อน แล้วลองใหม่อีกครั้ง\n")
        print("กด Enter เพื่อกลับหน้าแรก...", end="")
        try:
            input()
        except Exception:
            pass
        return

    print("\nเริ่มดาวน์โหลดและแปลงเป็น MP3 ...")
    mp3_path = download_mp3(url, out_dir)
    if mp3_path and mp3_path.exists():
        print(f"\n✅ สำเร็จ! ไฟล์ถูกบันทึกที่:\n{mp3_path}\n")
    else:
        print("\n❌ ไม่สามารถดาวน์โหลด/แปลงไฟล์ได้ ลองลิงก์อื่นหรือเช็คสิทธิ์การเข้าถึง (ลิงก์ส่วนตัว/จำกัดอายุ/ต้องล็อกอิน) แล้วลองใหม่อีกครั้ง\n")

    print("กด Enter เพื่อกลับหน้าแรก...", end="")
    try:
        input()
    except Exception:
        pass

def main_menu():
    while True:
        print_banner()
        print("==============================")
        print("  ตัวเลือกโหลดเสียงเป็น MP3  ")
        print("==============================")
        for k, v in PLATFORMS.items():
            print(f"{k}. {v}")
        print("0. ออกจากโปรแกรม")
        print("------------------------------")

        try:
            choice = input("พิมพ์หมายเลขที่ต้องการ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nออกจากโปรแกรม")
            break

        if choice == "0":
            print("ลาก่อนครับ")
            break
        elif choice in PLATFORMS:
            page_download(choice)
        else:
            print("กรุณาเลือกหมายเลขให้ถูกต้อง (0-6)")

if __name__ == "__main__":
    main_menu()
