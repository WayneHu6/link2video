# 🎬 Smart Video Link Downloader

A command-line tool based on `yt-dlp` and `Playwright` for automatically identifying and downloading original, watermark-free videos from various short video platforms (such as **Douyin**, **Bilibili**, **YouTube**, etc.).

This tool uses a custom parsing logic for **Douyin** to retrieve the real video address, while other platforms rely on `yt-dlp` to provide high-quality audio and video downloads.

---

## ✨ Features

- ✅ **Automatic platform detection**: Recognizes platform type from shared video links (Douyin, Bilibili, YouTube, etc.)
- 📥 **Fast audio/video download**: Separates audio and video for higher quality
- 🧼 **Douyin watermark-free**: Specialized logic to extract the real video URL without watermark
- 🖥️ **Simple CLI operation**: Suitable for batch processing and scripting integration
- 🌐 **Multi-platform support**: Built on `yt-dlp`, supporting a wide range of platforms

---

## 🧰 Usage

### 1️⃣ Install dependencies

Ensure Python 3.7 or later is installed.

Install required dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browser drivers (only needed once):

```bash
playwright install
```

---

### 2️⃣ Command-line usage

```bash
python main.py <video_share_url>
```

Example:

```bash
python main.py https://v.douyin.com/xxxxx/
```

The tool will automatically detect the platform and download the corresponding video and audio.

---

## 📂 Download Path

All downloads will be saved to:

```
./downloads/<platform>/<video_title>.mp4
```

Examples:

```
./downloads/douyin/Cat_Dance.mp4
./downloads/youtube/Funny_Video.mp4
```

---

## 📌 Supported Platforms

| Platform   | Method       | Download Support       |
|------------|--------------|------------------------|
| Douyin     | Playwright   | ✅ Watermark-Free       |
| Bilibili   | yt-dlp       | ✅                      |
| YouTube    | yt-dlp       | ✅                      |
| Others     | yt-dlp       | ✅ (Any yt-dlp-supported platform) |

> 🔗 See full [yt-dlp supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 🛠️ Tech Stack

- Python 3
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Playwright (for Douyin dynamic content parsing)
- Standard libraries: `requests`, `re`, `os`, etc.

---

## 📁 Project Structure

```
.
├── main.py              # Entry point
├── process/
│   └── douyin.py        # Douyin-specific parser
├── downloads/           # Downloaded media files
├── requirements.txt     # Dependency list
└── README.md            # Project documentation
```


## 🤝 Contribution

Contributions are welcome via PR or Issue:

- Add support for more platforms (e.g., Kuaishou, Xiaohongshu)
- Improve parsing logic and error handling
- Enhance user experience and CLI feedback

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## ⚠️ Disclaimer

This tool is intended for **educational and research purposes only**. Do not use it to violate platform terms of service or infringe on the rights of others.

You are solely responsible for how you use this tool. The author is **not liable** for any legal issues or consequences resulting from downloading, distributing, or modifying content from third-party platforms.

If you encounter copyright-related issues, please contact the original platform or content creators.

---
