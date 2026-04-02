import customtkinter as ctk
import pyaudio
import numpy as np
import time
import subprocess
import platform
import sys
import psutil
import webbrowser
from threading import Thread

# ========================= CONFIG =========================
RATE = 44100
CHUNK = 1024
THRESHOLD = 0.25          # Clap sensitivity - adjust if claps are missed (try 0.20)
CLAP_WINDOW = 0.8
COOLDOWN = 3.0

DEFAULT_URI = "spotify:track:63lREHNcVGyCVVydtLBk8n"
# =========================================================

class ClapControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClapControl • Hands-Free Spotify")
        self.geometry("1040x720")
        self.minsize(980, 680)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_uri = DEFAULT_URI
        self.is_playlist = False
        self.is_listening = False
        self.spotify_was_opened = False
        self.running = True

        self.p = None
        self.stream = None
        self.clap_thread = None

        self.create_ui()
        self.init_audio()
        self.start_clap_thread()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def parse_spotify_link(self, link):
        link = link.strip()
        if "open.spotify.com/track/" in link:
            try:
                track_id = link.split("open.spotify.com/track/")[1].split("?")[0].split("/")[0]
                self.is_playlist = False
                return f"spotify:track:{track_id}"
            except:
                return None
        elif "open.spotify.com/playlist/" in link:
            try:
                playlist_id = link.split("open.spotify.com/playlist/")[1].split("?")[0].split("/")[0]
                self.is_playlist = True
                return f"spotify:playlist:{playlist_id}"
            except:
                return None
        elif link.startswith("spotify:track:"):
            self.is_playlist = False
            return link
        elif link.startswith("spotify:playlist:"):
            self.is_playlist = True
            return link
        return None

    def create_ui(self):
        # ==================== NAV BAR (Blue + Red) ====================
        nav_frame = ctk.CTkFrame(self, height=78, fg_color="#0F172A", corner_radius=0)
        nav_frame.pack(fill="x", padx=0, pady=0)
        nav_frame.pack_propagate(False)

        title_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=40)

        title = ctk.CTkLabel(title_frame, text="ClapControl", 
                             font=ctk.CTkFont(size=32, weight="bold"), text_color="#3B82F6")
        title.pack(side="left")

        # Your GitHub Credit - right next to the app name
        credit = ctk.CTkLabel(title_frame, text="   •   Made by Akshat Johri", 
                              font=ctk.CTkFont(size=15), text_color="#EF4444", cursor="hand2")
        credit.pack(side="left", padx=(10, 0))
        credit.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/AkshatJohri242009"))

        # Status
        self.status_dot = ctk.CTkLabel(nav_frame, text="●", text_color="#22C55E", 
                                       font=ctk.CTkFont(size=24))
        self.status_dot.pack(side="left", padx=(30, 6))
        self.status_label = ctk.CTkLabel(nav_frame, text="Ready • Listening OFF", 
                                         font=ctk.CTkFont(size=15), text_color="#94A3B8")
        self.status_label.pack(side="left")

        # Toggle
        self.toggle_switch = ctk.CTkSwitch(nav_frame, text="Start Listening", 
                                           command=self.toggle_listening,
                                           font=ctk.CTkFont(size=16, weight="normal"),
                                           width=170, height=36)
        self.toggle_switch.pack(side="right", padx=40)

        # HERO
        hero = ctk.CTkFrame(self, fg_color="#1E2937", corner_radius=28)
        hero.pack(fill="both", expand=True, padx=36, pady=(28, 18))

        hero_label = ctk.CTkLabel(hero, text="👏 Double Clap to Play", 
                                  font=ctk.CTkFont(size=48, weight="bold"), text_color="#3B82F6")
        hero_label.pack(pady=(52, 12))

        self.current_song_label = ctk.CTkLabel(
            hero,
            text="Current: Baconator - RJ Pasin\n(Single Track)",
            font=ctk.CTkFont(size=20),
            text_color="#CBD5E1",
            justify="center"
        )
        self.current_song_label.pack(pady=(0, 36))

        ctk.CTkLabel(hero, text="Clap twice quickly • Spotify will open and attempt to play",
                     font=ctk.CTkFont(size=17), text_color="#64748B").pack()

        # CONFIG
        config_frame = ctk.CTkFrame(self, fg_color="#1E2937", corner_radius=28)
        config_frame.pack(fill="x", padx=36, pady=18)

        ctk.CTkLabel(config_frame, text="Choose Playback Mode", 
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B82F6").pack(anchor="w", padx=32, pady=(26, 12))

        mode_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=32, pady=(0, 20))

        self.mode_var = ctk.StringVar(value="Single Song")

        ctk.CTkRadioButton(mode_frame, text="Single Song", variable=self.mode_var, 
                           value="Single Song", font=ctk.CTkFont(size=15)).pack(side="left", padx=(0, 40))

        ctk.CTkRadioButton(mode_frame, text="Full Playlist", variable=self.mode_var, 
                           value="Playlist", font=ctk.CTkFont(size=15)).pack(side="left")

        input_row = ctk.CTkFrame(config_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=32, pady=(10, 28))

        self.link_entry = ctk.CTkEntry(input_row, 
            placeholder_text="Paste Spotify link here (track or playlist)...",
            height=54, font=ctk.CTkFont(size=15))
        self.link_entry.pack(side="left", fill="x", expand=True, padx=(0, 18))

        set_btn = ctk.CTkButton(input_row, text="Set & Save", width=160, height=54,
                                font=ctk.CTkFont(size=16, weight="bold"),
                                fg_color="#EF4444", text_color="white",
                                hover_color="#DC2626", command=self.set_new_song)
        set_btn.pack(side="right")

        # FEATURES
        ctk.CTkLabel(self, text="Key Features", 
                     font=ctk.CTkFont(size=21, weight="bold")).pack(anchor="w", padx=44, pady=(8, 10))

        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="x", padx=36, pady=(0, 30))

        features = [
            ("Ultra Low Resource", "Runs quietly in background"),
            ("Smart Behavior", "Ignores claps until Spotify is closed"),
            ("Flexible Playback", "Song or full playlist supported"),
            ("Clean & Private", "100% local operation")
        ]

        for i, (title, desc) in enumerate(features):
            card = ctk.CTkFrame(grid_frame, fg_color="#1F2937", corner_radius=20)
            card.grid(row=0, column=i, padx=12, pady=12, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="#60A5FA").pack(pady=(20, 6))
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=13), text_color="#94A3B8", wraplength=200).pack(pady=(0, 20))

        for col in range(4):
            grid_frame.grid_columnconfigure(col, weight=1)

    def update_mode(self):
        pass

    # ====================== CORE FUNCTIONS ======================
    def init_audio(self):
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=RATE,
                                      input=True, frames_per_buffer=CHUNK)
        except Exception as e:
            print(f"Microphone error: {e}")

    def start_clap_thread(self):
        self.clap_thread = Thread(target=self.clap_listener_loop, daemon=True)
        self.clap_thread.start()

    def clap_listener_loop(self):
        first_clap_time = None
        last_trigger_time = 0

        while self.running:
            if not self.is_listening or not self.stream:
                time.sleep(0.1)
                continue

            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                volume = np.max(np.abs(audio_chunk))

                if volume > THRESHOLD:
                    current_time = time.time()

                    if first_clap_time is None:
                        first_clap_time = current_time
                    elif current_time - first_clap_time <= CLAP_WINDOW:
                        if current_time - last_trigger_time > COOLDOWN:
                            self.handle_double_clap()
                            last_trigger_time = current_time
                        first_clap_time = None
                    else:
                        first_clap_time = current_time

                    time.sleep(0.15)
                else:
                    time.sleep(0.01)
            except:
                time.sleep(0.05)

    def handle_double_clap(self):
        if not self.spotify_was_opened:
            self.open_spotify_and_play()
        else:
            if not self.is_spotify_running():
                self.spotify_was_opened = False
                self.open_spotify_and_play()

    def is_spotify_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'spotify' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def open_spotify_and_play(self):
        try:
            uri_to_open = self.current_uri
            if not uri_to_open.endswith(":play"):
                uri_to_open += ":play"

            print(f"🎵 Opening → {uri_to_open} ({'Playlist' if self.is_playlist else 'Track'})")

            # Windows command for best compatibility
            subprocess.Popen(f'start "" "{uri_to_open}"', shell=True)

            self.spotify_was_opened = True
            self.after(0, lambda: self.update_status("Spotify opened • If playlist doesn't auto-play, click Play button"))
        except Exception as e:
            print(f"Error: {e}")

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.toggle_switch.configure(text="Listening • Stop")
            self.status_dot.configure(text_color="#EF4444")
            self.status_label.configure(text="Listening • Double clap active", text_color="#EF4444")
        else:
            self.toggle_switch.configure(text="Start Listening")
            self.status_dot.configure(text_color="#3B82F6")
            self.status_label.configure(text="Paused", text_color="#94A3B8")

    def set_new_song(self):
        link = self.link_entry.get()
        uri = self.parse_spotify_link(link)

        if uri:
            self.current_uri = uri
            mode_text = "Playlist" if self.is_playlist else "Single Track"
            short_id = uri.split(":")[-1][:12] + "..." if len(uri) > 25 else uri
            self.current_song_label.configure(
                text=f"Current: {short_id}\n({mode_text})"
            )
            self.link_entry.delete(0, "end")
            self.after(0, lambda: self.update_status("Updated successfully ✅"))
        else:
            self.after(0, lambda: self.update_status("❌ Invalid Spotify link", error=True))

    def update_status(self, text, error=False):
        color = "#EF4444" if error else "#22C55E"
        self.status_label.configure(text=text, text_color=color)

    def on_close(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.p:
            try:
                self.p.terminate()
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    # pip install customtkinter pyaudio numpy psutil
    app = ClapControlApp()
    app.mainloop()