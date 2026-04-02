# ClapControl 👏

**Hands-free Spotify controller using double claps**

Clap twice quickly → Spotify opens and plays your chosen song or playlist.  
No voice commands. No phone. Just pure claps.

![ClapControl Interface](https://via.placeholder.com/900x500/0F172A/3B82F6?text=ClapControl+Main+Interface)

---

## ✨ Features

- Double clap detection to trigger Spotify playback
- Support for **single tracks** and **full playlists**
- Smart logic: Ignores further claps until you close Spotify
- Modern, clean GUI with blue + red professional theme
- Extremely lightweight (~low RAM usage)
- Runs silently in the background
- 100% local & offline (after setup)

---

## 📸 Screenshots

### Main Application Window
![Main UI](https://via.placeholder.com/800x480/1E2937/60A5FA?text=ClapControl+UI)

*(Replace these placeholder images with actual screenshots of your app after uploading them to your repository)*

---

## 🚀 Quick Installation & Setup

### Step 1: Install Required Packages

Open **Command Prompt** and run:

```bash
  pip install customtkinter pyaudio numpy psutil
```
Windows users: If pyaudio installation fails, run these commands:Bashpip install pipwin
pipwin install pyaudio
Step 2: Download the Script
Download the file clapcontrol.py from this repository.
Step 3: Run the Application
Bashpython clapcontrol.py

How to Use

Launch clapcontrol.py
Choose your mode:
Single Song
Full Playlist

Paste any Spotify link in the input box and click Set & Save
Track example: https://open.spotify.com/track/63lREHNcVGyCVVydtLBk8n
Playlist example: https://open.spotify.com/playlist/YOUR_PLAYLIST_ID_HERE

Toggle Start Listening to ON
Clap twice quickly (within 0.8 seconds)

Spotify should open and start playing your selection.
Note for Playlists on Windows:
Sometimes Spotify opens the playlist but doesn't auto-play. In that case, simply click the big Play button inside Spotify.

Configuration Tips

Claps not detected? → Decrease THRESHOLD value in the code (try 0.20)
False triggers? → Increase THRESHOLD (try 0.30)
You can easily customize colors, window size, or add new features since it's built with CustomTkinter.


Requirements

Python 3.8 or higher
Spotify Desktop App installed
Working microphone
Windows (fully tested), macOS & Linux (basic support)


Made by
Akshat Johri
GitHub: https://github.com/AkshatJohri242009

License
This project is licensed under the MIT License — feel free to use, modify, and distribute.

⭐ If you like this project, please give it a star!

Made with ❤️ using Python & CustomTkinter
text

---

### How to upload:

1. Copy all the text above.
2. Create a new file named **`README.md`** in your project folder.
3. Paste the content and save it.
4. Commit and push to GitHub.

**Tip**: After uploading the file, take 2–3 screenshots of the running app and add them to your repo (in a folder called `screenshots`). Then replace the placeholder image links with the actual GitHub raw URLs.

Would you like me to also create a separate `clapcontrol.py` file with the latest version (blue + red theme + top credit) so you can upload both together? Just say **"yes"** and I'll give you the final code file.
