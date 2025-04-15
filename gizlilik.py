import os
import sys
import json
import hashlib
import base64
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import subprocess
import threading
import webbrowser
import time
import io
from datetime import datetime
from PIL import Image, ImageTk
import tkinterweb  # pip install tkinterweb
import customtkinter as ctk  # pip install customtkinter
import mimetypes
import random
import string
import platform
from functools import partial

class ModernTheme:
    # Tema renkleri
    class Light:
        bg_primary = "#FFFFFF"
        bg_secondary = "#F5F5F5"
        accent = "#4A6FFF"
        accent_hover = "#3A5FEF"
        text_primary = "#333333"
        text_secondary = "#666666"
        border = "#E0E0E0"
        success = "#4CAF50"
        warning = "#FFC107"
        error = "#F44336"
        highlight = "#E3F2FD"
        
    class Dark:
        bg_primary = "#1E1E1E"
        bg_secondary = "#252526"
        accent = "#4A6FFF"
        accent_hover = "#3A5FEF"
        text_primary = "#F0F0F0"
        text_secondary = "#B0B0B0"
        border = "#444444"
        success = "#81C784"
        warning = "#FFD54F"
        error = "#E57373"
        highlight = "#2C3E50"
    
    class NeonDark:
        bg_primary = "#121212"
        bg_secondary = "#1a1a1a"
        accent = "#00E5FF"
        accent_hover = "#00B8D4"
        text_primary = "#FFFFFF"
        text_secondary = "#BBBBBB"
        border = "#333333"
        success = "#00E676"
        warning = "#FFEA00"
        error = "#FF1744"
        highlight = "#311B92"
    
    class Forest:
        bg_primary = "#FAFAFA"
        bg_secondary = "#F0F7EE"
        accent = "#2E7D32"
        accent_hover = "#1B5E20"
        text_primary = "#263238"
        text_secondary = "#546E7A"
        border = "#A5D6A7"
        success = "#4CAF50"
        warning = "#FFA000"
        error = "#D32F2F"
        highlight = "#C8E6C9"
    
    class Ocean:
        bg_primary = "#FFFFFF"
        bg_secondary = "#E3F2FD"
        accent = "#0277BD"
        accent_hover = "#01579B"
        text_primary = "#263238"
        text_secondary = "#455A64"
        border = "#BBDEFB"
        success = "#00BFA5"
        warning = "#FFB300"
        error = "#F44336"
        highlight = "#B3E5FC"

class ImageViewer(ctk.CTkToplevel):
    def __init__(self, master, image_path):
        super().__init__(master)
        self.title("Görüntü Görüntüleyici")
        self.geometry("800x600")
        self.minsize(400, 300)
        
        self.theme = master.theme
        self.configure(fg_color=self.theme.bg_primary)
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self, fg_color=self.theme.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst buton çubuğu
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Resmi döndürme butonları
        self.rotate_left_btn = ctk.CTkButton(
            button_frame, text="↺ Sola Döndür", command=self._rotate_left,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=120
        )
        self.rotate_left_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.rotate_right_btn = ctk.CTkButton(
            button_frame, text="↻ Sağa Döndür", command=self._rotate_right,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=120
        )
        self.rotate_right_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Zoom butonları
        self.zoom_in_btn = ctk.CTkButton(
            button_frame, text="🔍+", command=self._zoom_in,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=80
        )
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.zoom_out_btn = ctk.CTkButton(
            button_frame, text="🔍-", command=self._zoom_out,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=80
        )
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.fit_btn = ctk.CTkButton(
            button_frame, text="Ekrana Sığdır", command=self._fit_to_screen,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=120
        )
        self.fit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kapat butonu sağda
        self.close_btn = ctk.CTkButton(
            button_frame, text="✖ Kapat", command=self.destroy,
            fg_color=self.theme.error, hover_color="#D32F2F",
            text_color="#FFFFFF", width=100
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Resim gösterme alanı - ScrollableFrame içinde
        self.scroll_container = ctk.CTkScrollableFrame(main_frame, fg_color=self.theme.bg_secondary)
        self.scroll_container.pack(fill=tk.BOTH, expand=True)
        
        # Resim etiketi
        self.image_label = ctk.CTkLabel(self.scroll_container, text="")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Dosya bilgisi
        self.info_label = ctk.CTkLabel(
            main_frame, 
            text=f"Dosya: {os.path.basename(image_path)}", 
            text_color=self.theme.text_secondary
        )
        self.info_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Resmi yükle ve hazırla
        self.original_image = Image.open(image_path)
        self.current_image = self.original_image.copy()
        self.zoom_level = 1.0
        self.rotation_angle = 0
        self._fit_to_screen()  # Başlangıçta ekrana sığdır
        
        # Pencere boyutu değiştiğinde resmi yeniden ölçeklendir
        self.bind("<Configure>", lambda e: self._update_image() if e.widget == self else None)
    
    def _rotate_left(self):
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self._update_image()
    
    def _rotate_right(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self._update_image()
    
    def _zoom_in(self):
        self.zoom_level *= 1.2
        self._update_image()
    
    def _zoom_out(self):
        self.zoom_level /= 1.2
        self._update_image()
    
    def _fit_to_screen(self):
        self.zoom_level = 1.0
        self._update_image(fit=True)
    
    def _update_image(self, fit=False):
        # Rotasyon uygula
        rotated = self.original_image.rotate(self.rotation_angle, expand=True)
        
        # Pencere boyutunu al
        window_width = self.winfo_width() - 40  # Kenar boşluklarını hesaba kat
        window_height = self.winfo_height() - 100  # Butonlar ve kenar boşluklarını hesaba kat
        
        if window_width <= 1 or window_height <= 1:  # Pencere henüz hazır değil
            self.after(100, self._update_image)
            return
        
        # Otomatik boyutlandır veya zoom uygula
        if fit:
            # Orijinal boyutları al
            img_width, img_height = rotated.size
            
            # En-boy oranını koru
            width_ratio = window_width / img_width
            height_ratio = window_height / img_height
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            resized = rotated.resize((new_width, new_height), Image.LANCZOS)
        else:
            # Zoom seviyesini uygula
            new_width = int(rotated.width * self.zoom_level)
            new_height = int(rotated.height * self.zoom_level)
            resized = rotated.resize((new_width, new_height), Image.LANCZOS)
        
        # Tkinter PhotoImage'e dönüştür ve göster
        self.tk_image = ImageTk.PhotoImage(resized)
        self.image_label.configure(image=self.tk_image)
        
        # Görüntü boyutunu güncelle
        self.info_label.configure(
            text=f"Dosya: {os.path.basename(self.original_image.filename)} | "
                f"Boyut: {new_width}x{new_height} | Zoom: {self.zoom_level:.2f}x"
        )

class VideoPlayer(ctk.CTkToplevel):
    def __init__(self, master, video_file):
        super().__init__(master)
        self.title("Video Oynatıcı")
        self.geometry("800x600")
        self.minsize(640, 480)
        
        self.theme = master.theme
        self.configure(fg_color=self.theme.bg_primary)
        
        self.video_file = video_file
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self, fg_color=self.theme.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video oynatıcı alanı
        self.player_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        self.player_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bilgi etiketi
        self.info_label = ctk.CTkLabel(
            self.player_frame, 
            text="Video yükleniyor...",
            text_color=self.theme.text_primary
        )
        self.info_label.pack(pady=20)
        
        # Kontrol butonları çerçevesi
        control_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Kontrol butonları
        self.play_btn = ctk.CTkButton(
            control_frame, text="▶️ Oynat", command=self._play,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.play_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pause_btn = ctk.CTkButton(
            control_frame, text="⏸️ Duraklat", command=self._pause,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_btn = ctk.CTkButton(
            control_frame, text="⏹️ Durdur", command=self._stop,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kapat butonu sağda
        self.close_btn = ctk.CTkButton(
            control_frame, text="✖ Kapat", command=self._close,
            fg_color=self.theme.error, hover_color="#D32F2F",
            text_color="#FFFFFF", width=100
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Bilgilendirme etiketi
        self.file_info = ctk.CTkLabel(
            main_frame, 
            text=f"Dosya: {os.path.basename(video_file)}", 
            text_color=self.theme.text_secondary
        )
        self.file_info.pack(anchor=tk.W)
        
        # Kullanıcının sisteminde uygun video oynatıcıyı başlat
        self._launch_player()
    
    def _launch_player(self):
        try:
            # Sisteme göre uygun video oynatıcı seç
            system = platform.system()
            
            if system == "Windows":
                # Windows'ta varsayılan oynatıcı ile aç
                os.startfile(self.video_file)
                self.info_label.configure(text="Video sistem oynatıcısında açıldı.")
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", self.video_file])
                self.info_label.configure(text="Video sistem oynatıcısında açıldı.")
            else:  # Linux ve diğerleri
                subprocess.Popen(["xdg-open", self.video_file])
                self.info_label.configure(text="Video sistem oynatıcısında açıldı.")
            
        except Exception as e:
            self.info_label.configure(text=f"Video açılamadı: {str(e)}")
    
    def _play(self):
        messagebox.showinfo("Bilgi", "Video sistem oynatıcısında açıldı.")
    
    def _pause(self):
        messagebox.showinfo("Bilgi", "Bu özellik şu anda desteklenmiyor.\nLütfen sistem oynatıcısını kullanın.")
    
    def _stop(self):
        messagebox.showinfo("Bilgi", "Bu özellik şu anda desteklenmiyor.\nLütfen sistem oynatıcısını kullanın.")
    
    def _close(self):
        messagebox.showinfo("Bilgi", "Video oynatıcısı kapatılıyor.\nSistem oynatıcısını manuel olarak kapatmanız gerekebilir.")
        self.destroy()

class TextEditor(ctk.CTkToplevel):
    def __init__(self, master, file_path):
        super().__init__(master)
        self.title("Metin Düzenleyici")
        self.geometry("800x600")
        self.minsize(400, 300)
        
        self.theme = master.theme
        self.configure(fg_color=self.theme.bg_primary)
        
        self.file_path = file_path
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self, fg_color=self.theme.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst buton çubuğu
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Kaydet butonu
        self.save_btn = ctk.CTkButton(
            button_frame, text="💾 Kaydet", command=self._save_file,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kapat butonu sağda
        self.close_btn = ctk.CTkButton(
            button_frame, text="✖ Kapat", command=self._close,
            fg_color=self.theme.error, hover_color="#D32F2F",
            text_color="#FFFFFF", width=100
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Metin düzenleme alanı
        self.text_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget kullanarak metin düzenleme alanı oluştur
        text_color = self.theme.text_primary
        bg_color = self.theme.bg_secondary
        
        self.text_area = tk.Text(
            self.text_frame,
            bg=bg_color,
            fg=text_color,
            insertbackground=text_color,  # imleç rengi
            selectbackground=self.theme.accent,
            selectforeground="#FFFFFF",
            borderwidth=0,
            padx=10,
            pady=10,
            wrap="word",
            font=("Segoe UI" if platform.system() == "Windows" else "Helvetica", 11)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Kaydırma çubuğu
        self.scrollbar = ttk.Scrollbar(self.text_area, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        # Dosya bilgisi
        self.info_label = ctk.CTkLabel(
            main_frame, 
            text=f"Dosya: {os.path.basename(file_path)}", 
            text_color=self.theme.text_secondary
        )
        self.info_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Dosyayı yükle
        self._load_file()
    
    def _load_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı: {str(e)}")
    
    def _save_file(self):
        try:
            content = self.text_area.get('1.0', tk.END)
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            messagebox.showinfo("Bilgi", "Dosya başarıyla kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
    
    def _close(self):
        answer = messagebox.askyesnocancel(
            "Kaydet ve Çık", 
            "Değişiklikleri kaydetmek istiyor musunuz?"
        )
        
        if answer is None:  # İptal
            return
        elif answer:  # Evet
            self._save_file()
            self.destroy()
        else:  # Hayır
            self.destroy()

class FileExplorer(ctk.CTkToplevel):
    def __init__(self, master, folder_path, hidden_id=None):
        super().__init__(master)
        self.title("Gizli Klasör İçeriği")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        self.master_app = master
        self.theme = master.theme
        self.configure(fg_color=self.theme.bg_primary)
        
        self.folder_path = folder_path
        self.hidden_id = hidden_id
        self.current_path = folder_path
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self, fg_color=self.theme.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst buton çubuğu
        button_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Geri butonu
        self.back_btn = ctk.CTkButton(
            button_frame, text="⬅️ Geri", command=self._go_back,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=80
        )
        self.back_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Üst klasöre git butonu
        self.up_btn = ctk.CTkButton(
            button_frame, text="⬆️ Üst Klasör", command=self._go_up,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.up_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Yenile butonu
        self.refresh_btn = ctk.CTkButton(
            button_frame, text="🔄 Yenile", command=self._refresh,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=80
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kapat butonu sağda
        self.close_btn = ctk.CTkButton(
            button_frame, text="✖ Kapat", command=self.destroy,
            fg_color=self.theme.error, hover_color="#D32F2F",
            text_color="#FFFFFF", width=80
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Yeni klasör butonu
        self.new_folder_btn = ctk.CTkButton(
            button_frame, text="📁 Yeni Klasör", command=self._create_folder,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=100
        )
        self.new_folder_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Mevcut yol gösterimi
        path_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary, height=30)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_var = tk.StringVar()
        self.path_var.set(folder_path)
        
        self.path_label = ctk.CTkLabel(
            path_frame, 
            textvariable=self.path_var,
            text_color=self.theme.text_secondary
        )
        self.path_label.pack(padx=10, pady=5, anchor=tk.W)
        
        # Dosya listesi çerçevesi
        file_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dosya listesi - TreeView
        self.file_tree = ttk.Treeview(
            file_frame, 
            columns=("name", "size", "date", "type"),
            show="headings",
            selectmode="browse"
        )
        
        # Sütun başlıkları
        self.file_tree.heading("name", text="İsim")
        self.file_tree.heading("size", text="Boyut")
        self.file_tree.heading("date", text="Tarih")
        self.file_tree.heading("type", text="Tür")
        
        # Sütun genişlikleri
        self.file_tree.column("name", width=350, anchor="w")
        self.file_tree.column("size", width=100, anchor="e")
        self.file_tree.column("date", width=150, anchor="w")
        self.file_tree.column("type", width=100, anchor="w")
        
        # Kaydırma çubukları
        vsb = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_tree.yview)
        hsb = ttk.Scrollbar(file_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Yerleştirme
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # Açıklama etiketi
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="Hazır",
            text_color=self.theme.text_secondary
        )
        self.status_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Çift tıklama olayı
        self.file_tree.bind("<Double-1>", self._on_item_double_click)
        
        # Sağ tık menüsü
        self.file_tree.bind("<Button-3>", self._show_context_menu)
        
        # Dosya listesini doldur
        self._populate_files()
        
        # Stil uygulamaları
        self._apply_treeview_style()
    
    def _apply_treeview_style(self):
        # TreeView stillerini tema renklerine göre ayarla
        style = ttk.Style()
        
        # TreeView arka plan ve yazı renkleri
        style.configure(
            "Treeview", 
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            fieldbackground=self.theme.bg_secondary,
            borderwidth=0
        )
        
        # TreeView başlık stilleri
        style.configure(
            "Treeview.Heading",
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            borderwidth=1
        )
        
        # Seçili öğe stili
        style.map(
            "Treeview",
            background=[("selected", self.theme.accent)],
            foreground=[("selected", "#FFFFFF")]
        )
    
    def _populate_files(self):
        # Mevcut dosya listesini temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            # Klasörleri ve dosyaları listele
            folders = []
            files = []
            
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                
                # Dosya bilgilerini al
                stat_info = os.stat(item_path)
                size = stat_info.st_size
                mod_time = datetime.fromtimestamp(stat_info.st_mtime).strftime('%d.%m.%Y %H:%M')
                
                if os.path.isdir(item_path):
                    # Klasör
                    folders.append((item, "<Klasör>", mod_time, "Klasör"))
                else:
                    # Dosya
                    size_str = self._format_size(size)
                    file_type = self._get_file_type(item)
                    files.append((item, size_str, mod_time, file_type))
            
            # Önce klasörleri ekle
            for folder in sorted(folders):
                self.file_tree.insert("", tk.END, values=folder, tags=("folder",))
            
            # Sonra dosyaları ekle
            for file in sorted(files):
                self.file_tree.insert("", tk.END, values=file, tags=("file",))
            
            # Yol etiketini güncelle
            self.path_var.set(self.current_path)
            self.status_label.configure(text=f"{len(folders)} klasör, {len(files)} dosya")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör içeriği listelenemedi: {str(e)}")
    
    def _format_size(self, size_bytes):
        """Dosya boyutunu okunaklı formata dönüştürür"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    
    def _get_file_type(self, filename):
        """Dosya uzantısına göre türünü belirler"""
        _, ext = os.path.splitext(filename)
        
        if not ext:
            return "Dosya"
        
        ext = ext.lower()
        
        # Yaygın dosya türleri
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            return "Resim"
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']:
            return "Video"
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']:
            return "Ses"
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            return "Belge"
        elif ext in ['.txt', '.md', '.rtf', '.json', '.xml', '.html', '.css', '.js']:
            return "Metin"
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "Arşiv"
        elif ext in ['.exe', '.msi', '.bat', '.cmd']:
            return "Program"
        elif ext in ['.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs']:
            return "Kod"
        else:
            return ext
    
    def _on_item_double_click(self, event):
        """Öğeye çift tıklandığında açma işlemi"""
        item = self.file_tree.selection()[0]
        values = self.file_tree.item(item, "values")
        name = values[0]
        item_type = values[3]
        
        # Tam yolu oluştur
        item_path = os.path.join(self.current_path, name)
        
        if item_type == "Klasör":
            # Klasörü aç
            self.current_path = item_path
            self._populate_files()
        else:
            # Dosya türüne göre uygun görüntüleyici aç
            self._open_file(item_path)
    
    def _open_file(self, file_path):
        """Dosya türüne göre uygun görüntüleyici açar"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            # Resim dosyaları
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                ImageViewer(self, file_path)
            
            # Video dosyaları
            elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']:
                VideoPlayer(self, file_path)
            
            # Metin dosyaları
            elif ext in ['.txt', '.md', '.rtf', '.json', '.xml', '.html', '.css', '.js']:
                TextEditor(self, file_path)
            
            # Diğer dosyalar - sistem varsayılan uygulamasıyla aç
            else:
                # Windows
                if platform.system() == "Windows":
                    os.startfile(file_path)
                # macOS
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", file_path])
                # Linux
                else:
                    subprocess.Popen(["xdg-open", file_path])
        
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı: {str(e)}")
    
    def _go_back(self):
        """Geri düğmesi işlevi"""
        if self.current_path != self.folder_path:
            # Ana klasör sınırını aşmayacak şekilde üst klasöre git
            parent = os.path.dirname(self.current_path)
            if os.path.commonpath([parent, self.folder_path]) == self.folder_path:
                self.current_path = parent
                self._populate_files()
    
    def _go_up(self):
        """Üst klasöre git düğmesi işlevi"""
        # Ana klasör sınırını aşmayacak şekilde üst klasöre git
        parent = os.path.dirname(self.current_path)
        if os.path.commonpath([parent, self.folder_path]) == self.folder_path:
            self.current_path = parent
            self._populate_files()
    
    def _refresh(self):
        """Mevcut klasörü yenile"""
        self._populate_files()
    
    def _create_folder(self):
        """Yeni klasör oluştur"""
        folder_name = simpledialog_askstring("Yeni Klasör", "Klasör adı:")
        if folder_name:
            try:
                new_folder_path = os.path.join(self.current_path, folder_name)
                os.makedirs(new_folder_path)
                self._refresh()
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör oluşturulamadı: {str(e)}")
    
    def _show_context_menu(self, event):
        """Sağ tık menüsü göster"""
        # Tıklanan öğeyi seç
        item = self.file_tree.identify_row(event.y)
        if not item:
            return
        
        # Öğeyi seç
        self.file_tree.selection_set(item)
        values = self.file_tree.item(item, "values")
        name = values[0]
        item_type = values[3]
        item_path = os.path.join(self.current_path, name)
        
        # Bağlam menüsü oluştur
        context_menu = tk.Menu(self, tearoff=0)
        
        if item_type == "Klasör":
            context_menu.add_command(label="Aç", command=lambda: self._on_item_double_click(None))
            context_menu.add_command(label="Yeniden Adlandır", command=lambda: self._rename_item(item_path))
            context_menu.add_command(label="Sil", command=lambda: self._delete_item(item_path))
        else:
            context_menu.add_command(label="Aç", command=lambda: self._on_item_double_click(None))
            context_menu.add_command(label="Yeniden Adlandır", command=lambda: self._rename_item(item_path))
            context_menu.add_command(label="Sil", command=lambda: self._delete_item(item_path))
        
        # Menüyü göster
        context_menu.tk_popup(event.x_root, event.y_root)
    
    def _rename_item(self, item_path):
        """Dosya veya klasör yeniden adlandırma"""
        old_name = os.path.basename(item_path)
        new_name = simpledialog_askstring("Yeniden Adlandır", "Yeni ad:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                new_path = os.path.join(os.path.dirname(item_path), new_name)
                os.rename(item_path, new_path)
                self._refresh()
            except Exception as e:
                messagebox.showerror("Hata", f"Yeniden adlandırılamadı: {str(e)}")
    
    def _delete_item(self, item_path):
        """Dosya veya klasör silme"""
        name = os.path.basename(item_path)
        is_dir = os.path.isdir(item_path)
        
        msg = f"'{name}' {'klasörünü' if is_dir else 'dosyasını'} silmek istediğinizden emin misiniz?"
        if is_dir:
            msg += "\nKlasör içindeki tüm dosyalar silinecektir!"
        
        if messagebox.askyesno("Sil", msg):
            try:
                if is_dir:
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                self._refresh()
            except Exception as e:
                messagebox.showerror("Hata", f"Silinemedi: {str(e)}")

class PrivateBrowser(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gizli Tarayıcı")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        self.theme = master.theme
        self.configure(fg_color=self.theme.bg_primary)
        
        # Ana çerçeve
        main_frame = ctk.CTkFrame(self, fg_color=self.theme.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst tarafta bulunan kontroller
        control_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Geri butonu
        self.back_btn = ctk.CTkButton(
            control_frame, text="⬅️", command=self._go_back,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=40
        )
        self.back_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # İleri butonu
        self.forward_btn = ctk.CTkButton(
            control_frame, text="➡️", command=self._go_forward,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=40
        )
        self.forward_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Yenile butonu
        self.refresh_btn = ctk.CTkButton(
            control_frame, text="🔄", command=self._refresh,
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=40
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Ana sayfa butonu
        self.home_btn = ctk.CTkButton(
            control_frame, text="🏠", command=lambda: self._load_url("https://www.google.com"),
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=40
        )
        self.home_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # URL giriş alanı
        self.url_var = tk.StringVar()
        self.url_var.set("https://www.google.com")
        
        self.url_entry = ctk.CTkEntry(
            control_frame, 
            textvariable=self.url_var,
            width=400,
            height=32,
            border_width=1,
            corner_radius=8
        )
        self.url_entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", lambda event: self._load_url(self.url_var.get()))
        
        # Git butonu
        self.go_btn = ctk.CTkButton(
            control_frame, text="Git", command=lambda: self._load_url(self.url_var.get()),
            fg_color=self.theme.accent, hover_color=self.theme.accent_hover,
            text_color="#FFFFFF", width=60
        )
        self.go_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kapat butonu
        self.close_btn = ctk.CTkButton(
            control_frame, text="✖", command=self.destroy,
            fg_color=self.theme.error, hover_color="#D32F2F",
            text_color="#FFFFFF", width=40
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Web tarayıcı
        browser_frame = ctk.CTkFrame(main_frame, fg_color=self.theme.bg_secondary)
        browser_frame.pack(fill=tk.BOTH, expand=True)
        
        # TkinterWeb kullanarak web tarayıcı oluştur
        self.browser = tkinterweb.HtmlFrame(browser_frame, messages_enabled=False)
        self.browser.pack(fill=tk.BOTH, expand=True)
        
        # Durum çubuğu
        self.status_bar = ctk.CTkLabel(
            main_frame, 
            text="Gizli tarayıcı - bilgiler saklanmaz", 
            text_color=self.theme.text_secondary,
            anchor="w"
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Gizli mod uyarısı
        self.privacy_label = ctk.CTkLabel(
            main_frame,
            text="🔒 Gizli tarayıcı aktif - geçmiş ve çerezler saklanmaz",
            text_color=self.theme.success,
            anchor="e"
        )
        self.privacy_label.pack(fill=tk.X, pady=(0, 5))
        
        # Başlangıç sayfasını yükle
        self._load_url("https://www.google.com")
        
        # Tarayıcı olay işleyicileri
        self.browser.on_link_click(self._on_link_click)
        self.browser.on_done_loading(self._on_done_loading)
    
    def _load_url(self, url):
        """Belirtilen URL'yi yükle"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            self.browser.load_website(url)
            self.url_var.set(url)
            self.status_bar.configure(text=f"Yükleniyor: {url}")
        except Exception as e:
            self.status_bar.configure(text=f"Hata: {str(e)}")
    
    def _go_back(self):
        """Geri git"""
        try:
            self.browser.go_back()
        except:
            pass
    
    def _go_forward(self):
        """İleri git"""
        try:
            self.browser.go_forward()
        except:
            pass
    
    def _refresh(self):
        """Sayfayı yenile"""
        try:
            self.browser.reload()
        except:
            pass
    
    def _on_link_click(self, url):
        """Link tıklama olayı"""
        self.url_var.set(url)
        return True
    
    def _on_done_loading(self, success):
        """Sayfa yükleme tamamlandı olayı"""
        if success:
            self.status_bar.configure(text=f"Yüklendi: {self.url_var.get()}")
        else:
            self.status_bar.configure(text=f"Yükleme hatası: {self.url_var.get()}")

class FolderHiderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Klasör Gizleme Uygulaması")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Tema seçimi
        self.themes = {
            "Açık": ModernTheme.Light,
            "Koyu": ModernTheme.Dark,
            "Neon Koyu": ModernTheme.NeonDark,
            "Orman": ModernTheme.Forest,
            "Okyanus": ModernTheme.Ocean
        }
        
        # Varsayılan temayı ayarla
        self.current_theme = "Koyu"
        self.theme = self.themes[self.current_theme]
        
        # CustomTkinter ayarları
        ctk.set_appearance_mode("dark" if "Dark" in self.current_theme else "light")
        ctk.set_default_color_theme("blue")
        
        # Uygulama verilerinin saklanacağı dizin
        self.app_data_dir = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~/.config'), 'FolderHider')
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
            
        self.config_file = os.path.join(self.app_data_dir, "hidden_folders.dat")
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.hidden_dir = os.path.join(self.app_data_dir, "hidden")
        if not os.path.exists(self.hidden_dir):
            os.makedirs(self.hidden_dir)
            
        self.salt = b'klasorgizle_salt_456789'  # Daha güçlü salt değeri
        self.hidden_folders = {}
        self.current_password = None
        self.is_authenticated = False
        
        # Ayarları yükle
        self.settings = self._load_settings()
        
        # Tema ayarını uygula
        if "theme" in self.settings:
            self.current_theme = self.settings["theme"]
            self.theme = self.themes[self.current_theme]
        
        # UI kurulumu
        self.setup_ui()
        self.check_first_run()
        
    def _load_settings(self):
        """Kullanıcı ayarlarını yükle"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"theme": "Koyu"}
        return {"theme": "Koyu"}
    
    def _save_settings(self):
        """Kullanıcı ayarlarını kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Ayarlar kaydedilemedi: {str(e)}")
    
    def setup_ui(self):
        # Ana çerçeveler
        self.login_frame = ctk.CTkFrame(self.root)
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Login çerçevesi
        login_header = ctk.CTkLabel(
            self.login_frame, 
            text="Klasör Gizleme Uygulaması", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        login_header.pack(pady=(40, 20))
        
        # Logo veya ikon (burada bir metin olarak temsil edildi)
        logo_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        logo_frame.pack(pady=(0, 30))
        
        logo_text = ctk.CTkLabel(
            logo_frame, 
            text="🔒", 
            font=ctk.CTkFont(size=64)
        )
        logo_text.pack()
        
        # Şifre giriş alanı başlığı
        password_label = ctk.CTkLabel(
            self.login_frame, 
            text="Lütfen şifrenizi girin:",
            font=ctk.CTkFont(size=14)
        )
        password_label.pack(pady=(0, 10))
        
        # Şifre giriş alanı
        self.password_entry = ctk.CTkEntry(
            self.login_frame, 
            show="•", 
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            placeholder_text="Şifre"
        )
        self.password_entry.pack(pady=(0, 20))
        self.password_entry.bind("<Return>", lambda event: self.login())
        
        # Giriş butonu
        login_button = ctk.CTkButton(
            self.login_frame, 
            text="Giriş", 
            command=self.login,
            width=200,
            height=40,
            border_width=0,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_button.pack(pady=(0, 20))
        
        # Ana çerçeve tasarımı
        # Üst panel
        top_panel = ctk.CTkFrame(self.main_frame)
        top_panel.pack(fill=tk.X, padx=10, pady=10)
        
        # Başlık ve logo
        header_label = ctk.CTkLabel(
            top_panel, 
            text="Klasör Gizleme Yöneticisi", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(side=tk.LEFT, padx=10)
        
        # Tema seçici
        theme_label = ctk.CTkLabel(top_panel, text="Tema:")
        theme_label.pack(side=tk.RIGHT, padx=(10, 5))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_menu = ctk.CTkOptionMenu(
            top_panel,
            values=list(self.themes.keys()),
            variable=self.theme_var,
            command=self.change_theme,
            width=120
        )
        self.theme_menu.pack(side=tk.RIGHT)
        
        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Sol panel - klasör listesi
        left_panel = ctk.CTkFrame(content_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)  # Boyutu sabitle
        
        # Klasör listesi başlığı
        list_header = ctk.CTkLabel(
            left_panel, 
            text="Gizli Klasörler", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_header.pack(pady=(10, 5), anchor=tk.W, padx=10)
        
        # Klasör listesi
        self.folder_list_frame = ctk.CTkScrollableFrame(left_panel)
        self.folder_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sağ panel - ana içerik
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Butonlar çerçevesi
        button_panel = ctk.CTkFrame(right_panel)
        button_panel.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        # Butonlar
        self.hide_btn = ctk.CTkButton(
            button_panel, 
            text="🔒 Klasör Gizle", 
            command=self.hide_folder,
            width=150,
            height=35,
            border_width=0,
            corner_radius=8
        )
        self.hide_btn.pack(side=tk.LEFT, padx=5)
        
        self.unhide_btn = ctk.CTkButton(
            button_panel, 
            text="🔓 Seçili Klasörü Göster", 
            command=self.unhide_folder,
            width=200,
            height=35,
            border_width=0,
            corner_radius=8
        )
        self.unhide_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = ctk.CTkButton(
            button_panel, 
            text="📂 Seçili Klasörü Aç", 
            command=self.open_folder,
            width=200,
            height=35,
            border_width=0,
            corner_radius=8
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = ctk.CTkButton(
            button_panel, 
            text="🗑️ Seçili Klasörü Sil", 
            command=self.remove_folder,
            width=200,
            height=35,
            fg_color="#E57373",
            hover_color="#EF5350",
            border_width=0,
            corner_radius=8
        )
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Ayrıca çıkış ve tarayıcı butonları için yeni bir panel
        special_buttons_panel = ctk.CTkFrame(right_panel)
        special_buttons_panel.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Gizli tarayıcı butonu
        self.browser_btn = ctk.CTkButton(
            special_buttons_panel, 
            text="🌐 Gizli Tarayıcı", 
            command=self.open_browser,
            width=150,
            height=35,
            fg_color="#7986CB",
            hover_color="#5C6BC0",
            border_width=0,
            corner_radius=8
        )
        self.browser_btn.pack(side=tk.LEFT, padx=5)
        
        # Şifre değiştir butonu
        self.change_pw_btn = ctk.CTkButton(
            special_buttons_panel, 
            text="🔑 Şifre Değiştir", 
            command=self.change_password,
            width=150,
            height=35,
            fg_color="#4DB6AC",
            hover_color="#26A69A",
            border_width=0,
            corner_radius=8
        )
        self.change_pw_btn.pack(side=tk.LEFT, padx=5)
        
        # Çıkış butonu
        self.logout_btn = ctk.CTkButton(
            special_buttons_panel, 
            text="🚪 Çıkış", 
            command=self.logout,
            width=100,
            height=35,
            fg_color="#F44336",
            hover_color="#D32F2F",
            border_width=0,
            corner_radius=8
        )
        self.logout_btn.pack(side=tk.RIGHT, padx=5)
        
        # Seçili klasör bilgisi
        self.info_frame = ctk.CTkFrame(right_panel)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Seçili klasör bilgisi başlığı
        selected_header = ctk.CTkLabel(
            self.info_frame, 
            text="Seçili Klasör Bilgisi", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        selected_header.pack(pady=(10, 5), anchor=tk.W, padx=10)
        
        # İçerik tablosu
        info_inner_frame = ctk.CTkFrame(self.info_frame)
        info_inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Klasör bilgileri
        self.selected_name_var = tk.StringVar(value="")
        self.selected_path_var = tk.StringVar(value="")
        self.selected_date_var = tk.StringVar(value="")
        self.selected_size_var = tk.StringVar(value="")
        self.selected_status_var = tk.StringVar(value="")
        
        # Bilgi etiketleri
        info_grid = ctk.CTkFrame(info_inner_frame, fg_color="transparent")
        info_grid.pack(fill=tk.X, padx=10, pady=10, anchor=tk.N)
        
        ctk.CTkLabel(info_grid, text="Klasör Adı:", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_grid, textvariable=self.selected_name_var, anchor="w").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(info_grid, text="Orijinal Konum:", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_grid, textvariable=self.selected_path_var, anchor="w").grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(info_grid, text="Gizlenme Tarihi:", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_grid, textvariable=self.selected_date_var, anchor="w").grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(info_grid, text="Boyut:", anchor="w").grid(row=3, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_grid, textvariable=self.selected_size_var, anchor="w").grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(info_grid, text="Durum:", anchor="w").grid(row=4, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_grid, textvariable=self.selected_status_var, anchor="w").grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # Önizleme alanı
        preview_frame = ctk.CTkFrame(info_inner_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        preview_label = ctk.CTkLabel(
            preview_frame, 
            text="Önizleme", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_label.pack(pady=(10, 5), anchor=tk.W, padx=10)
        
        self.preview_content = ctk.CTkTextbox(preview_frame, wrap="word", height=200)
        self.preview_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Durum çubuğu
        status_bar = ctk.CTkFrame(self.main_frame, height=25)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_bar, 
            text="Hazır", 
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.version_label = ctk.CTkLabel(
            status_bar, 
            text="v1.0.0", 
            anchor="e"
        )
        self.version_label.pack(side=tk.RIGHT, padx=10)
        
        # Başlangıçta login ekranını göster
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Temayı uygula
        self.apply_theme()
    
    def check_first_run(self):
        """İlk çalıştırma kontrolü ve şifre oluşturma"""
        if not os.path.exists(self.config_file):
            self.login_frame.pack_forget()
            self.setup_password()
        
    def setup_password(self):
        """İlk çalıştırma için şifre oluşturma penceresi"""
        self.setup_frame = ctk.CTkFrame(self.root)
        self.setup_frame.pack(fill=tk.BOTH, expand=True)
        
        setup_header = ctk.CTkLabel(
            self.setup_frame, 
            text="Hoş Geldiniz!", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        setup_header.pack(pady=(40, 10))
        
        setup_info = ctk.CTkLabel(
            self.setup_frame,
            text="Klasör Gizleme Uygulamasını ilk kez kullanıyorsunuz.\nLütfen bir ana şifre belirleyin.",
            font=ctk.CTkFont(size=14)
        )
        setup_info.pack(pady=(0, 30))
        
        # Şifre giriş alanı
        password_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        password_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(password_frame, text="Şifre:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.new_password = ctk.CTkEntry(password_frame, show="•", width=250)
        self.new_password.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(password_frame, text="Şifre Tekrar:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.confirm_password = ctk.CTkEntry(password_frame, show="•", width=250)
        self.confirm_password.grid(row=1, column=1, padx=10, pady=10)
        
        # Şifre güvenlik ipuçları
        tips_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        tips_frame.pack(pady=(0, 20))
        
        tips_text = """Güvenli bir şifre için:
- En az 8 karakter kullanın
- Büyük ve küçük harfler ekleyin
- Sayılar ve özel karakterler kullanın
- Kolayca tahmin edilebilir bilgiler kullanmayın"""
        
        tips_label = ctk.CTkLabel(
            tips_frame,
            text=tips_text,
            justify=tk.LEFT,
            font=ctk.CTkFont(size=12)
        )
        tips_label.pack(padx=20)
        
        # Oluştur butonu
        create_button = ctk.CTkButton(
            self.setup_frame,
            text="Şifre Oluştur",
            command=self.create_password,
            width=200,
            height=40,
            corner_radius=8
        )
        create_button.pack(pady=(10, 20))
    
    def create_password(self):
        """Yeni şifre oluştur"""
        password = self.new_password.get()
        confirm = self.confirm_password.get()
        
        if not password:
            messagebox.showerror("Hata", "Lütfen bir şifre girin.")
            return
            
        if password != confirm:
            messagebox.showerror("Hata", "Şifreler eşleşmiyor.")
            return
            
        if len(password) < 6:
            messagebox.showerror("Hata", "Şifre en az 6 karakter olmalıdır.")
            return
        
        # Şifreyi kaydet
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Boş hidden_folders sözlüğünü şifrele ve kaydet
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(json.dumps({}).encode())
        
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Kurulum ekranını kapat, login ekranını göster
        self.setup_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        messagebox.showinfo("Başarılı", "Şifreniz başarıyla oluşturuldu.\nLütfen giriş yapın.")
    
    def login(self):
        """Kullanıcı girişi"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Hata", "Lütfen şifrenizi girin.")
            return
        
        try:
            # Şifreyi doğrula
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            cipher_suite = Fernet(key)
            decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
            self.hidden_folders = json.loads(decrypted_data)
            
            # Başarılı giriş
            self.current_password = password
            self.is_authenticated = True
            self.login_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Klasör listesini güncelle
            self.update_folder_list()
            
            # Durum çubuğunu güncelle
            self.status_label.configure(text="Giriş başarılı")
            
        except Exception as e:
            messagebox.showerror("Hata", "Yanlış şifre veya bozuk veri.")
            self.password_entry.delete(0, tk.END)
    
    def logout(self):
        """Oturumu kapat"""
        self.is_authenticated = False
        self.current_password = None
        self.hidden_folders = {}
        
        # UI sıfırla
        self.main_frame.pack_forget()
        self.password_entry.delete(0, tk.END)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
    
    def change_password(self):
        """Şifre değiştirme penceresi"""
        if not self.is_authenticated:
            return
            
        password_window = ctk.CTkToplevel(self.root)
        password_window.title("Şifre Değiştir")
        password_window.geometry("400x300")
        password_window.resizable(False, False)
        password_window.transient(self.root)
        password_window.grab_set()
        
        # Tema ayarı
        password_window.configure(fg_color=self.theme.bg_primary)
        
        # İçerik
        header = ctk.CTkLabel(
            password_window, 
            text="Şifre Değiştir", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=(20, 15))
        
        form_frame = ctk.CTkFrame(password_window, fg_color="transparent")
        form_frame.pack(pady=10)
        
        # Eski şifre
        ctk.CTkLabel(form_frame, text="Mevcut Şifre:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        old_password = ctk.CTkEntry(form_frame, show="•", width=200)
        old_password.grid(row=0, column=1, padx=10, pady=10)
        
        # Yeni şifre
        ctk.CTkLabel(form_frame, text="Yeni Şifre:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        new_password = ctk.CTkEntry(form_frame, show="•", width=200)
        new_password.grid(row=1, column=1, padx=10, pady=10)
        
        # Yeni şifre tekrar
        ctk.CTkLabel(form_frame, text="Yeni Şifre Tekrar:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        confirm_password = ctk.CTkEntry(form_frame, show="•", width=200)
        confirm_password.grid(row=2, column=1, padx=10, pady=10)
        
        # Butonlar
        button_frame = ctk.CTkFrame(password_window, fg_color="transparent")
        button_frame.pack(pady=15)
        
        def change():
            old_pw = old_password.get()
            new_pw = new_password.get()
            confirm_pw = confirm_password.get()
            
            # Kontroller
            if not old_pw or not new_pw or not confirm_pw:
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
                return
                
            if old_pw != self.current_password:
                messagebox.showerror("Hata", "Mevcut şifre yanlış.")
                return
                
            if new_pw != confirm_pw:
                messagebox.showerror("Hata", "Yeni şifreler eşleşmiyor.")
                return
                
            if len(new_pw) < 6:
                messagebox.showerror("Hata", "Şifre en az 6 karakter olmalıdır.")
                return
                
            # Şifre değiştirme
            try:
                # Yeni şifre ile veriyi şifrele
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=self.salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(new_pw.encode()))
                
                cipher_suite = Fernet(key)
                encrypted_data = cipher_suite.encrypt(json.dumps(self.hidden_folders).encode())
                
                with open(self.config_file, 'wb') as f:
                    f.write(encrypted_data)
                
                self.current_password = new_pw
                messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi.")
                password_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Şifre değiştirilemedi: {str(e)}")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Değiştir",
            command=change,
            width=100,
            height=35,
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_hover
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=password_window.destroy,
            width=100,
            height=35,
            fg_color=self.theme.error,
            hover_color="#D32F2F"
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def apply_theme(self):
        """Tema renklerini uygula"""
        self.theme = self.themes[self.current_theme]
        
        # CustomTkinter görünüm modu
        ctk.set_appearance_mode("dark" if "Dark" in self.current_theme or "Neon" in self.current_theme else "light")
        
        # Ana pencere arka planı
        self.root.configure(bg=self.theme.bg_primary)
        
        # Login frame
        self.login_frame.configure(fg_color=self.theme.bg_primary)
        
        # Main frame
        self.main_frame.configure(fg_color=self.theme.bg_primary)
        
        # Tema değişikliğini ayarlara kaydet
        self.settings["theme"] = self.current_theme
        self._save_settings()
        
        # Klasör listesini güncelle (tema değişikliğini yansıtmak için)
        if self.is_authenticated:
            self.update_folder_list()
    
    def change_theme(self, theme_name):
        """Temayı değiştir"""
        self.current_theme = theme_name
        self.apply_theme()
    
    def update_folder_list(self):
        """Gizli klasör listesini günceller"""
        # Önceki klasör butonlarını temizle
        for widget in self.folder_list_frame.winfo_children():
            widget.destroy()
        
        if not self.hidden_folders:
            no_folders_label = ctk.CTkLabel(
                self.folder_list_frame, 
                text="Henüz gizli klasör yok",
                text_color=self.theme.text_secondary
            )
            no_folders_label.pack(pady=50)
            return
        
        # Her gizli klasör için bir buton oluştur
        for folder_id, folder_info in self.hidden_folders.items():
            folder_name = folder_info.get("name", "Bilinmeyen Klasör")
            
            frame = ctk.CTkFrame(self.folder_list_frame, fg_color="transparent")
            frame.pack(fill=tk.X, pady=2)
            
            # Klasör butonu
            btn = ctk.CTkButton(
                frame,
                text=folder_name,
                command=lambda fid=folder_id: self.select_folder(fid),
                anchor="w",
                fg_color="transparent",
                text_color=self.theme.text_primary,
                hover_color=self.theme.highlight,
                height=30,
                border_spacing=5
            )
            btn.pack(fill=tk.X)
        
        # Seçili klasör bilgilerini güncelle
        self.clear_selection()
    
    def select_folder(self, folder_id):
        """Bir klasörü seç ve bilgilerini göster"""
        if folder_id in self.hidden_folders:
            folder_info = self.hidden_folders[folder_id]
            
            # Klasör bilgilerini göster
            self.selected_name_var.set(folder_info.get("name", ""))
            self.selected_path_var.set(folder_info.get("original_path", ""))
            
            hide_date = folder_info.get("hide_date", "")
            self.selected_date_var.set(hide_date)
            
            size = folder_info.get("size", 0)
            size_str = self.format_size(size)
            self.selected_size_var.set(size_str)
            
            self.selected_status_var.set("Gizli")
            
            # Önizleme içeriğini güncelle
            hidden_path = os.path.join(self.hidden_dir, folder_id)
            preview_text = self.get_folder_preview(hidden_path)
            self.preview_content.delete("1.0", tk.END)
            self.preview_content.insert("1.0", preview_text)
            
            # Buton durumlarını güncelle
            self.unhide_btn.configure(state="normal")
            self.open_btn.configure(state="normal")
            self.remove_btn.configure(state="normal")
            
            # Seçilen klasör ID'sini sakla
            self.selected_folder_id = folder_id
        
    def clear_selection(self):
        """Seçili klasör bilgilerini temizle"""
        self.selected_name_var.set("")
        self.selected_path_var.set("")
        self.selected_date_var.set("")
        self.selected_size_var.set("")
        self.selected_status_var.set("")
        
        self.preview_content.delete("1.0", tk.END)
        
        # Butonları devre dışı bırak
        self.unhide_btn.configure(state="disabled")
        self.open_btn.configure(state="disabled")
        self.remove_btn.configure(state="disabled")
        
        self.selected_folder_id = None
    
    def get_folder_preview(self, folder_path):
        """Klasör içeriğinin önizlemesini oluşturur"""
        preview_text = "Klasör İçeriği:\n\n"
        
        try:
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(folder_path):
                rel_path = os.path.relpath(root, folder_path)
                if rel_path != ".":
                    preview_text += f"📁 {rel_path}\n"
                    dir_count += 1
                
                for file in files:
                    if file_count < 20:  # Çok fazla dosya göstermeyelim
                        file_path = os.path.join(rel_path, file)
                        if rel_path == ".":
                            preview_text += f"📄 {file}\n"
                        else:
                            preview_text += f"  📄 {file_path}\n"
                    file_count += 1
            
            total_count = file_count + dir_count
            
            if file_count > 20:
                preview_text += f"\n... ve {file_count - 20} dosya daha\n"
            
            preview_text += f"\nToplam: {dir_count} klasör, {file_count} dosya"
            
        except Exception as e:
            preview_text = f"Önizleme yüklenemedi: {str(e)}"
        
        return preview_text
    
    def format_size(self, size_bytes):
        """Dosya boyutunu okunaklı formata dönüştürür"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    
    def get_folder_size(self, folder_path):
        """Klasör boyutunu hesaplar"""
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
        except:
            pass
            
        return total_size
    
    def hide_folder(self):
        """Yeni bir klasörü gizle"""
        if not self.is_authenticated:
            return
            
        # Klasör seçme diyaloğu
        folder_path = filedialog.askdirectory(title="Gizlemek İstediğiniz Klasörü Seçin")
        
        if not folder_path:
            return
            
        # Klasör adını al
        folder_name = os.path.basename(folder_path)
        
        # Klasör zaten gizli mi kontrol et
        for folder_id, info in self.hidden_folders.items():
            if info.get("original_path") == folder_path:
                messagebox.showerror("Hata", "Bu klasör zaten gizlenmiş.")
                return
        
        try:
            # Yeni benzersiz ID oluştur
            folder_id = self.generate_id()
            
            # Gizli klasör için hedef yol
            target_path = os.path.join(self.hidden_dir, folder_id)
            
            # Klasörü kopyala
            shutil.copytree(folder_path, target_path)
            
            # Klasör bilgilerini kaydet
            size = self.get_folder_size(folder_path)
            hide_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            
            self.hidden_folders[folder_id] = {
                "name": folder_name,
                "original_path": folder_path,
                "hide_date": hide_date,
                "size": size
            }
            
            # Orijinal klasörü sil
            shutil.rmtree(folder_path)
            
            # Değişiklikleri kaydet
            self.save_hidden_folders()
            
            # UI güncelle
            self.update_folder_list()
            self.status_label.configure(text=f"{folder_name} klasörü başarıyla gizlendi")
            messagebox.showinfo("Başarılı", f"{folder_name} klasörü başarıyla gizlendi.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör gizlenemedi: {str(e)}")
    
    def unhide_folder(self):
        """Seçili klasörü göster (orijinal konumuna geri yükle)"""
        if not self.is_authenticated or not self.selected_folder_id:
            return
            
        folder_id = self.selected_folder_id
        folder_info = self.hidden_folders[folder_id]
        
        folder_name = folder_info.get("name", "")
        original_path = folder_info.get("original_path", "")
        
        # Orijinal klasör yolu hala mevcut mu?
        if os.path.exists(original_path):
            answer = messagebox.askyesno(
                "Dikkat", 
                f"Orijinal konum '{original_path}' zaten mevcut.\nÜzerine yazmak istiyor musunuz?"
            )
            if not answer:
                return
        
        try:
            # Gizli klasör yolu
            hidden_path = os.path.join(self.hidden_dir, folder_id)
            
            # Klasörü orijinal konumuna kopyala
            shutil.copytree(hidden_path, original_path)
            
            # Gizli klasörü sil
            shutil.rmtree(hidden_path)
            
            # Bilgileri listeden kaldır
            del self.hidden_folders[folder_id]
            
            # Değişiklikleri kaydet
            self.save_hidden_folders()
            
            # UI güncelle
            self.update_folder_list()
            self.status_label.configure(text=f"{folder_name} klasörü orijinal konumuna geri yüklendi")
            messagebox.showinfo("Başarılı", f"{folder_name} klasörü orijinal konumuna geri yüklendi.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör gösterilemedi: {str(e)}")
    
    def open_folder(self):
        """Seçili gizli klasörü aç"""
        if not self.is_authenticated or not self.selected_folder_id:
            return
            
        folder_id = self.selected_folder_id
        hidden_path = os.path.join(self.hidden_dir, folder_id)
        
        if os.path.exists(hidden_path):
            # Klasör gezgini aç
            FileExplorer(self, hidden_path, folder_id)
        else:
            messagebox.showerror("Hata", "Klasör açılamadı.")
    
    def remove_folder(self):
        """Seçili gizli klasörü kalıcı olarak sil"""
        if not self.is_authenticated or not self.selected_folder_id:
            return
            
        folder_id = self.selected_folder_id
        folder_info = self.hidden_folders[folder_id]
        folder_name = folder_info.get("name", "")
        
        # Onay iste
        answer = messagebox.askyesno(
            "Dikkat", 
            f"'{folder_name}' klasörünü kalıcı olarak silmek istediğinizden emin misiniz?\n"
            "Bu işlem geri alınamaz!"
        )
        
        if not answer:
            return
            
        try:
            # Gizli klasör yolu
            hidden_path = os.path.join(self.hidden_dir, folder_id)
            
            # Klasörü sil
            if os.path.exists(hidden_path):
                shutil.rmtree(hidden_path)
            
            # Bilgileri listeden kaldır
            del self.hidden_folders[folder_id]
            
            # Değişiklikleri kaydet
            self.save_hidden_folders()
            
            # UI güncelle
            self.update_folder_list()
            self.status_label.configure(text=f"{folder_name} klasörü kalıcı olarak silindi")
            messagebox.showinfo("Başarılı", f"{folder_name} klasörü kalıcı olarak silindi.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör silinemedi: {str(e)}")
            
    def open_folder(self):
        """Seçili gizli klasörü aç"""
        if not self.is_authenticated or not self.selected_folder_id:
            return
        
        folder_id = self.selected_folder_id
        folder_path = os.path.join(self.hidden_dir, folder_id)
        
        # Dosya gezginini aç
        FileExplorer(self.root, folder_path, hidden_id=folder_id)

    def restore_folder(self):
        """Seçili gizli klasörü geri yükle"""

        if not self.is_authenticated or not self.selected_folder_id:
            return

        folder_id = self.selected_folder_id
        folder_info = self.hidden_folders[folder_id]
        folder_name = folder_info.get("name", "")
        original_path = folder_info.get("original_path", "")

        # Hedef yolun uygunluğunu kontrol et
        if not original_path or not os.path.exists(os.path.dirname(original_path)):
            messagebox.showerror("Hata", "Klasörün orijinal konumu bulunamadı veya geçersiz.")
            return

        # Onay iste
        answer = messagebox.askyesno(
            "Geri Yükle",
            f"'{folder_name}' klasörünü orijinal konumuna geri yüklemek istediğinizden emin misiniz?"
        )

        if not answer:
            return

        try:
            # Gizli klasör yolu
            hidden_path = os.path.join(self.hidden_dir, folder_id)

            # Orijinal yola taşı
            shutil.move(hidden_path, original_path)

            # Bilgileri listeden kaldır
            del self.hidden_folders[folder_id]

            # Değişiklikleri kaydet
            self.save_hidden_folders()

            # UI güncelle
            self.update_folder_list()
            self.status_label.configure(text=f"'{folder_name}' klasörü geri yüklendi.")
            messagebox.showinfo("Başarılı", f"'{folder_name}' klasörü başarıyla geri yüklendi.")

        except Exception as e:
            messagebox.showerror("Hata", f"Klasör geri yüklenemedi: {str(e)}")

    def change_password(self):
        """Şifre değiştirme"""

        new_password = simpledialog.askstring("Şifre Değiştir", "Yeni şifre:", show="•")
        if new_password:
            self.current_password = self.hash_password(new_password)
            self.save_password()
            messagebox.showinfo("Başarılı", "Şifre başarıyla değiştirildi.")

    def setup_main_ui(self):
        """Ana uygulama arayüzünü kur"""

        # Buton stilleri
        button_font = ctk.CTkFont(size=14, weight="bold")
        button_fg_color = self.theme.accent
        button_hover_color = self.theme.accent_hover
        button_text_color = "#FFFFFF"

        # Sol çerçeve (klasör listesi)
        left_frame = ctk.CTkFrame(self.main_frame, fg_color=self.theme.bg_secondary)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)

        # Sağ çerçeve (işlemler)
        right_frame = ctk.CTkFrame(self.main_frame, fg_color=self.theme.bg_secondary)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # Klasör Listesi
        folder_list_label = ctk.CTkLabel(left_frame, text="Gizli Klasörler", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.theme.text_primary)
        folder_list_label.pack(pady=(10, 0))

        self.folder_listbox = tk.Listbox(
            left_frame,
            bg=self.theme.bg_primary,
            fg=self.theme.text_primary,
            selectbackground=self.theme.accent,
            selectforeground="#FFFFFF",
            font=("Segoe UI" if platform.system() == "Windows" else "Helvetica", 12),
            borderwidth=0,
            highlightthickness=0
        )
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.folder_listbox.bind('<<ListboxSelect>>', self.on_folder_select)

        # İşlem Butonları
        button_frame = ctk.CTkFrame(right_frame, fg_color=self.theme.bg_secondary)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        self.add_folder_button = ctk.CTkButton(
            button_frame, text="Klasör Ekle", command=self.add_folder,
            font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
        )
        self.add_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.open_folder_button = ctk.CTkButton(
            button_frame, text="Klasörü Aç", command=self.open_folder,
            font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
        )
        self.open_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.restore_folder_button = ctk.CTkButton(
            button_frame, text="Klasörü Geri Yükle", command=self.restore_folder,
            font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
        )
        self.restore_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.remove_folder_button = ctk.CTkButton(
            button_frame, text="Klasörü Sil", command=self.remove_folder,
            font=button_font, fg_color=self.theme.error, hover_color="#D32F2F", text_color=button_text_color
        )
        self.remove_folder_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.change_password_button = ctk.CTkButton(
            button_frame, text="Şifreyi Değiştir", command=self.change_password,
            font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
        )
        self.change_password_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.browse_button = ctk.CTkButton(
            button_frame, text="Gizli Tarayıcı", command=self.open_private_browser,
            font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
        )
        self.browse_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Durum çubuğu
        self.status_label = ctk.CTkLabel(
            self.main_frame, text="Hazır",
            text_color=self.theme.text_secondary,
            anchor="w"
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        # Klasör listesini doldur
        self.update_folder_list()

    def on_folder_select(self, event):
        """Klasör seçildiğinde bilgileri göster"""
        try:
            selection = self.folder_listbox.curselection()
            if selection:
                index = selection[0]
                folder_id = list(self.hidden_folders.keys())[index]
                self.selected_folder_id = folder_id
                folder_name = self.hidden_folders[folder_id]["name"]
                self.status_label.configure(text=f"Seçili: {folder_name}")
            else:
                self.selected_folder_id = None
                self.status_label.configure(text="Hazır")
        except Exception as e:
            print(f"Klasör seçme hatası: {e}")

    def update_folder_list(self):
        """Klasör listesini güncelle"""

        self.folder_listbox.delete(0, tk.END)
        for folder_id, folder_info in self.hidden_folders.items():
            self.folder_listbox.insert(tk.END, folder_info["name"])

        if self.hidden_folders:
            self.status_label.configure(text=f"{len(self.hidden_folders)} klasör kayıtlı")
        else:
            self.status_label.configure(text="Hiç klasör kayıtlı değil")

    def open_private_browser(self):
        """Gizli tarayıcıyı aç"""
        PrivateBrowser(self.root)

    def check_first_run(self):
        """Uygulamanın ilk kez çalışıp çalışmadığını kontrol et"""

        if not os.path.exists(self.config_file):
            self.show_first_run_dialog()
        else:
            self.load_hidden_folders()
            self.show_login_screen()

    def show_first_run_dialog(self):
        """İlk çalıştırma ekranını göster"""

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Hoş Geldiniz")
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        frame = ctk.CTkFrame(dialog, fg_color=self.theme.bg_primary)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(
            frame,
            text="Bu uygulama ilk kez çalıştırılıyor.\nLütfen bir şifre belirleyin:",
            font=ctk.CTkFont(size=16),
            text_color=self.theme.text_primary
        )
        label.pack(pady=(20, 10))

        password_entry = ctk.CTkEntry(
            frame,
            show="•",
            width=200,
            font=ctk.CTkFont(size=14),
            fg_color=self.theme.bg_secondary,
            text_color=self.theme.text_primary
        )
        password_entry.pack(pady=10)

        confirm_button = ctk.CTkButton(
            frame,
            text="Onayla",
            command=lambda: self.on_first_run_confirm(dialog, password_entry.get()),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_hover,
            text_color="#FFFFFF"
        )
        confirm_button.pack(pady=20)

        dialog.wait_window()  # Diyalog penceresini bekle

    def on_first_run_confirm(self, dialog, password):
        """İlk çalıştırma şifre onaylama"""

        if password:
            self.current_password = self.hash_password(password)
            self.save_password()
            dialog.destroy()
            self.show_login_screen()
        else:
            messagebox.showerror("Hata", "Lütfen bir şifre girin.")

    def show_login_screen(self):
        """Giriş ekranını göster"""

        self.main_frame.pack_forget()  # Ana ekranı gizle
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        def on_login():
            password = self.password_entry.get()
            if self.verify_password(password):
                self.is_authenticated = True
                self.login_frame.pack_forget()
                self.setup_main_ui()
                self.main_frame.pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showerror("Hata", "Yanlış şifre.")

        # Mevcut giriş butonunu kaldır
        for widget in self.login_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Giriş":
                widget.destroy()
                break

        # Yeni giriş butonu oluştur ve yerleştir
        login_button = ctk.CTkButton(
            self.login_frame,
            text="Giriş",
            command=on_login,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.theme.accent,
            hover_color=self.theme.accent_hover,
            text_color="#FFFFFF"
        )
        login_button.pack(pady=(20, 40))

    def hash_password(self, password):
        """Şifreyi hash'le"""

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=100000,
            salt=self.salt,
            length=32
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()

    def verify_password(self, password):
        """Şifreyi doğrula"""

        hashed_password = self.hash_password(password)
        return hashed_password == self.current_password

    def save_password(self):
        """Şifreyi kaydet"""

        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(self.current_password)

    def load_password(self):
        """Şifreyi yükle"""

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.current_password = f.read().strip()
        except FileNotFoundError:
            self.current_password = None

    def load_hidden_folders(self):
        """Gizli klasör bilgilerini yükle"""

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.hidden_folders = json.load(f)
        except FileNotFoundError:
            self.hidden_folders = {}
        except json.JSONDecodeError:
            self.hidden_folders = {}  # Dosya boşsa veya bozuksa sıfırla

    def save_hidden_folders(self):
        """Gizli klasör bilgilerini kaydet"""

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.hidden_folders, f)

    def generate_unique_id(self, length=16):
        """Eşsiz bir klasör ID'si oluştur"""

        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

if __name__ == "__main__":
    root = ctk.CTk()
    app = FolderHiderApp(root)
    root.mainloop()