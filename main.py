import sys
import os
import yt_dlp
from process.douyin import handle_aweme_download


def get_site(url: str):
    """根据链接判断所属平台"""
    if "douyin.com" in url:
        return "douyin"
    if "bilibili.com" in url:
        return "bilibili"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "generic"


def handle_platform_download(url: str, site: str):
    """下载分发逻辑"""
    if site == "douyin":
        print(">>> 检测到抖音链接，使用专用解析器下载")
        handle_aweme_download(url)
        return

    # 其余平台用 yt-dlp 处理
    base_dir = os.path.join("downloads", site)
    os.makedirs(base_dir, exist_ok=True)

    common_opts = {
        'quiet': False,
        'outtmpl': os.path.join(base_dir, '%(title)s.%(ext)s'),
    }

    # 下载视频
    print(f">>> 从 [{site}] 下载视频…")
    with yt_dlp.YoutubeDL({**common_opts, 'format': 'bv*'}) as ydl:
        ydl.download([url])

    # 下载音频
    print(f">>> 从 [{site}] 下载音频…")
    with yt_dlp.YoutubeDL({**common_opts, 'format': 'ba'}) as ydl:
        ydl.download([url])


def main():
    if len(sys.argv) != 2:
        print("用法: python download.py <视频链接>")
        sys.exit(1)

    url = sys.argv[1]
    site = get_site(url)
    print(f">>> 识别平台: {site}")
    handle_platform_download(url, site)


if __name__ == "__main__":
    main()
