# 🎵 Media Playlist Downloader

A beautiful and intuitive desktop GUI app built with Python and Tkinter for downloading entire playlists from platforms like **YouTube**, **SoundCloud**, and more. Supports high-quality audio downloads, format selection, and cookie-based authenticated downloads.

---

## ✨ Features

* 🎧 **Download from Playlists** — Supports YouTube, SoundCloud, and other supported sources.
* 🔽 **Multiple Formats** — Download in `MP3`, `MP4`, or the original media format.
* 💾 **Custom Output Directory** — Choose where to save your downloaded files.
* 🍪 **Cookie File Support** — Use a `cookies.txt` file to access private/age-restricted content.
* 📊 **Progress Indicator** — Real-time status and loading bar.
* 🎛️ **Download Quality Control** — Choose from "Best Available", "Good", or "Normal" quality.
* 🆘 **Built-in Help** — Comprehensive instructions on how to get your cookies file.
* 💻 **User-Friendly GUI** — Clean, responsive, and easy to use.
* 💬 **Open Source** — Freely available on GitHub!

---

## 🚀 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Hussein119/media-playlist-downloader.git
   cd media-playlist-downloader
   ```

2. **Create Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   python media_downloader_gui.py
   ```

---

## 🧩 Dependencies

* [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) – For media downloading
* [`pydub`](https://github.com/jiaaro/pydub) – For MP3 conversion
* `tkinter` – Built-in with Python (for GUI)
* `ffmpeg` – Required by `pydub` for format conversion

> 💡 Make sure `ffmpeg` is installed and added to your system's PATH.

---

## 📁 How to Use

1. Enter a **playlist URL** (YouTube, SoundCloud, etc.)
2. Select an **output folder** for saving downloads
3. *(Optional)* Add a **cookies.txt** file to access private or age-restricted content
4. Choose your desired **format** and **quality**
5. Click **Start Download** 🚀

Need help with cookies? Click the ❓ **Help** button next to the cookies field.

---

## 🔐 Cookie File Guide

You can export a cookies file using browser extensions like:

* **Chrome**: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/)
* **Firefox**: [cookies.txt extension](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

More detailed steps are available inside the app by clicking ❓ **Help**.

---

## 📸 Screenshots

> Add screenshots of your GUI app here to show off the interface.

---

## 🛠️ Troubleshooting

* Ensure your URL is supported by `yt-dlp`.
* Check that `ffmpeg` is installed and available via terminal/command prompt.
* If using cookies, make sure the file is correctly exported and not expired.
* Try running the script with administrator privileges if you encounter permission issues.

---

## 🧑‍💻 Author

**Hussein AK**
📬 [GitHub Profile](https://github.com/Hussein119)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## ❤️ Contributions

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a pull request.
