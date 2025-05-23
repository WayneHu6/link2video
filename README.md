# 🎬 视频链接智能下载工具

这是一个基于 `yt-dlp` 和 `Playwright` 的命令行工具，可自动识别并下载来自多个短视频平台（如 **抖音**、**哔哩哔哩**、**YouTube** 等）的原始无水印视频。

对于 **抖音**，采用专用解析逻辑，获取真实视频地址；其他平台统一使用 `yt-dlp` 实现高清音视频下载。

---

## ✨ 功能特点

- ✅ **自动识别平台类型**：输入分享链接即可判断平台类型（抖音、B站、YouTube 等）
- 📥 **快速下载音视频**：视频和音频分离下载，保证高质量
- 🧼 **抖音无水印解析**：专为抖音设计，获取真实地址，绕过水印限制
- 🖥️ **命令行操作简洁直观**：适合批处理和自动化脚本集成
- 🌐 **多平台支持扩展性强**：基于 yt-dlp，支持平台丰富

---

## 🧰 使用方法

### 1️⃣ 安装依赖

确保 Python 3.7 及以上版本已安装。

安装依赖：

```bash
pip install -r requirements.txt
```

安装 Playwright 浏览器驱动（仅首次）：

```bash
playwright install
```

---

### 2️⃣ 命令行使用

```bash
python main.py <视频分享链接>
```

示例：

```bash
python main.py https://v.douyin.com/xxxxx/
```

程序会自动识别平台，并下载对应视频及音频资源。

---

## 📂 下载路径说明

所有下载内容将保存在：

```
./downloads/<平台名>/<视频标题>.mp4
```

例如：

```
./downloads/douyin/小猫跳舞.mp4
./downloads/youtube/Funny_Video.mp4
```

---

## 📌 当前支持平台

| 平台名称 | 处理方式   | 支持下载 |
|----------|------------|----------|
| 抖音     | Playwright | ✅ 无水印 |
| 哔哩哔哩 | yt-dlp     | ✅        |
| YouTube  | yt-dlp     | ✅        |
| 其他平台 | yt-dlp     | ✅（支持 yt-dlp 的平台）|

> 🔗 可参考 [yt-dlp 支持平台列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 🛠️ 技术栈

- Python 3
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Playwright（用于抖音页面模拟解析）
- requests、re、os 等标准库

---

## 📁 项目结构（示意）

```
.
├── main.py            # 主程序入口
├── process/
│   └── douyin.py          # 抖音专用解析逻辑
├── downloads/             # 视频保存路径
├── requirements.txt       # 依赖文件
└── README.md              # 项目说明文档
```


## 🤝 贡献

欢迎提交 PR 或 Issue：

- 添加新平台支持（如快手、小红书）
- 优化解析流程与错误处理
- 改进用户体验与交互提示

---

## 📄 License

本项目采用 [MIT License](./LICENSE) 开源协议。


---

## ⚠️ 免责声明

本工具仅供学习与技术研究使用，请勿用于任何违反平台服务协议或侵犯他人权益的行为。

使用者需对自己的使用行为负责，因使用本工具下载、传播、修改他人内容所引发的一切法律纠纷及后果，均与作者无关。

如涉及版权问题，请联系原视频平台或相关内容创作者处理。

---