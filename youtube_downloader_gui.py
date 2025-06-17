import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os
import yt_dlp
import sys
import traceback
import sv_ttk  # Modern tema için


# --- Gerekli Araclari Kontrol Et ---
def get_resource_path(relative_path):
    """ Hem script modunda hem de PyInstaller ile paketlenmis halde dosya yolunu bulur. """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller gecici bir klasor olusturur ve yolu _MEIPASS icinde saklar.
        base_path = sys._MEIPASS
    else:
        # Normal script modunda
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


FFMPEG_PATH = get_resource_path("ffmpeg.exe")
ICON_PATH = get_resource_path("icon.ico")


# --- Ana Uygulama Sınıfı ---
class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("600x680")  # Pencereyi biraz büyüttük
        self.root.resizable(False, False)

        # Pencere ikonu (eger icon.ico varsa)
        if os.path.exists(ICON_PATH):
            self.root.iconbitmap(ICON_PATH)

        # Modern tema ayarları
        sv_ttk.set_theme("dark")  # "light" veya "dark" olarak degistirebilirsiniz

        self.video_info = None
        self.available_formats = []
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # --- URL Giriş Alanı ---
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(url_frame, text="YouTube Linki:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, width=50, font=("Segoe UI", 11))
        self.url_entry.pack(side="left", expand=True, fill="x")
        self.fetch_button = ttk.Button(url_frame, text="Bilgi Getir", command=self.start_fetch_thread,
                                       style="Accent.TButton")
        self.fetch_button.pack(side="left", padx=(10, 0))

        # --- Video Detayları Alanı ---
        self.thumbnail_label = ttk.Label(main_frame, background="#333333")
        self.thumbnail_label.pack(pady=10, fill="x")
        placeholder_img = Image.new('RGB', (560, 315), color='#333333')
        self.tk_placeholder_img = ImageTk.PhotoImage(placeholder_img)
        self.thumbnail_label.config(image=self.tk_placeholder_img)

        self.title_label = ttk.Label(main_frame, text="Video Başlığı Burada Görünecek", wraplength=550,
                                     justify="center", font=("Segoe UI Semibold", 13))
        self.title_label.pack(pady=(10, 20))

        # --- İndirme Seçenekleri ---
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill="x", pady=10)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)

        ttk.Label(options_frame, text="Format:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5,
                                                                             sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.format_menu = ttk.Combobox(options_frame, textvariable=self.format_var, values=["MP4", "MP3"],
                                        state="disabled", width=10)
        self.format_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.format_menu.bind("<<ComboboxSelected>>", self.update_quality_options)

        ttk.Label(options_frame, text="Kalite:", font=("Segoe UI", 10)).grid(row=0, column=2, padx=(20, 5), pady=5,
                                                                             sticky="w")
        self.quality_var = tk.StringVar()
        self.quality_menu = ttk.Combobox(options_frame, textvariable=self.quality_var, state="disabled", width=25)
        self.quality_menu.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # --- İndirme Butonu ve Durum Alanı ---
        self.download_button = ttk.Button(main_frame, text="İndir", state="disabled",
                                          command=self.start_download_thread, style="Accent.TButton")
        self.download_button.pack(pady=20, ipady=5, fill="x")

        self.status_label = ttk.Label(main_frame, text="Lütfen bir YouTube linki yapıştırın.", justify="center",
                                      font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 5))

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5, fill="x")

    # ----- Arka Plan Fonksiyonları (Bu kısımda değişiklik yok, sadece kopyalayın) -----

    def start_fetch_thread(self):
        thread = threading.Thread(target=self.fetch_video_info)
        thread.daemon = True
        thread.start()

    def fetch_video_info(self):
        url = self.url_entry.get()
        if not url: return
        self.set_ui_state("disabled", "Video formatları getiriliyor...")
        try:
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
            self.available_formats = self.video_info.get('formats', [])
            thumbnail_url = self.video_info.get('thumbnail')
            response = requests.get(thumbnail_url)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((560, 315))
            self.tk_thumbnail = ImageTk.PhotoImage(img)
            self.thumbnail_label.config(image=self.tk_thumbnail)
            self.title_label.config(text=self.video_info.get('title', 'Başlık bulunamadı'))
            self.format_menu.config(state="readonly")
            self.update_quality_options()
            self.set_ui_state("normal", "İndirmeye hazır. Format ve kalite seçin.")
        except Exception as e:
            messagebox.showerror("Hata", f"Video bilgileri alınamadı:\n{e}")
            self.set_ui_state("normal", "Hata oluştu. Lütfen tekrar deneyin.")

    def update_quality_options(self, event=None):
        self.quality_menu.set('')
        selected_type = self.format_var.get()

        if selected_type == "MP4":
            qualities = []
            video_formats = [f for f in self.available_formats if f.get('vcodec') != 'none' and f.get('ext') == 'mp4']
            for f in sorted(video_formats, key=lambda x: x.get('height', 0), reverse=True):
                fps = f.get('fps')
                fps_text = f"({fps}fps)" if fps else ""
                filesize = f.get('filesize') or f.get('filesize_approx')
                size_mb = f"{filesize / 1024 / 1024:.2f} MB" if filesize else "Bilinmiyor"
                label = f"{f.get('height')}p {fps_text} - {size_mb}"
                qualities.append((label, f['format_id']))
            self.quality_map = {label: format_id for label, format_id in qualities}
            self.quality_menu['values'] = [label for label, format_id in qualities]
            self.quality_menu.config(state="readonly")
            if self.quality_menu['values']:
                self.quality_var.set(self.quality_menu['values'][0])
        else:  # MP3
            self.quality_menu['values'] = []
            self.quality_var.set("En İyi Ses Kalitesi (Otomatik)")
            self.quality_menu.config(state="disabled")

    def start_download_thread(self):
        thread = threading.Thread(target=self.download)
        thread.daemon = True
        thread.start()

    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'fraction' in d and d['fraction'] is not None:
                self.progress_bar['value'] = d['fraction'] * 100
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                self.status_label.config(
                    text=f"İndiriliyor: {downloaded / 1024 / 1024:.2f}MB / {total / 1024 / 1024:.2f}MB")
            self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.status_label.config(text="İndirme tamamlandı, dönüştürülüyor...")

    def download(self):
        save_path = filedialog.askdirectory()
        if not save_path: return
        self.set_ui_state("disabled", "İndirme başlıyor...")

        try:
            if self.format_var.get() == "MP4":
                selected_label = self.quality_var.get()
                format_id = self.quality_map[selected_label]
                format_selector = f"{format_id}+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
                ydl_opts = {'format': format_selector,
                            'outtmpl': os.path.join(save_path, '%(title)s [%(height)sp].%(ext)s'),
                            'progress_hooks': [self.download_progress_hook], 'ffmpeg_location': FFMPEG_PATH,
                            'merge_output_format': 'mp4'}
            else:  # MP3
                ydl_opts = {'format': 'bestaudio/best', 'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                            'progress_hooks': [self.download_progress_hook], 'ffmpeg_location': FFMPEG_PATH,
                            'postprocessors': [
                                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_info['webpage_url']])

            self.status_label.config(text="Dosya başarıyla kaydedildi!")
            messagebox.showinfo("Başarılı", "İndirme tamamlandı.")

        except Exception as e:
            error_details = traceback.format_exc()
            error_message = f"Beklenmedik bir hata oluştu:\n\n{str(e)}\n\nDetaylar:\n{error_details}"
            messagebox.showerror("İndirme Hatası", error_message)
        finally:
            self.set_ui_state("normal", "Yeni indirme için hazır.")
            self.progress_bar['value'] = 0

    def set_ui_state(self, state, status_text=""):
        self.fetch_button.config(state=state)
        self.download_button.config(state=state if self.video_info else "disabled")
        self.format_menu.config(state=state if self.video_info else "disabled")
        if self.format_var.get() == "MP4":
            self.quality_menu.config(state=state if self.video_info else "disabled")
        else:
            self.quality_menu.config(state="disabled")
        if status_text:
            self.status_label.config(text=status_text)


if __name__ == "__main__":
    if not all(os.path.exists(get_resource_path(f)) for f in ["ffmpeg.exe", "ffprobe.exe"]):
        messagebox.showwarning("Eksik Dosya",
                               "FFmpeg/ffprobe.exe bulunamadı.\nLütfen kurulumu 'build.bat' ile tekrar yapın.")
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

