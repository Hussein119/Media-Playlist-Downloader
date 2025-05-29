import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import font
import threading
import yt_dlp as youtube_dl
from pydub import AudioSegment
import webbrowser
import subprocess
import signal

class MediaDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
        self.is_downloading = False
        self.download_thread = None  # Track the download thread
        self.processes = []  # Track subprocesses (if any)
        
        # Bind the close event to cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        # Configure main window
        self.root.title("Media Playlist Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Colors and styling
        bg_color = "#f8f9fa"
        primary_color = "#2c3e50"
        secondary_color = "#3498db"
        accent_color = "#27ae60"
        warning_color = "#e74c3c"
        info_color = "#17a2b8"
        
        self.root.configure(bg=bg_color)
        
        # Fonts
        title_font = font.Font(family="Arial", size=18, weight="bold")
        label_font = font.Font(family="Arial", size=11)
        
        # Configure grid weights for main window
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main canvas and scrollbar for scrolling
        main_canvas = tk.Canvas(self.root, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=bg_color)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid the canvas and scrollbar
        main_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")
        
        main_canvas.bind('<Enter>', _bind_to_mousewheel)
        main_canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Main container (now inside scrollable frame)
        main_frame = tk.Frame(scrollable_frame, bg=bg_color, padx=25, pady=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, text="🎵 Media Playlist Downloader", 
                              font=title_font, bg=bg_color, fg=primary_color)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # URL Section
        url_frame = tk.LabelFrame(main_frame, text="📡 Playlist URL", 
                                 font=label_font, bg=bg_color, fg=primary_color, padx=15, pady=15)
        url_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=label_font, 
                            width=70, relief="solid", bd=1)
        url_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Add placeholder text functionality
        url_entry.insert(0, "Enter playlist URL (SoundCloud, YouTube, etc.)")
        url_entry.config(fg='gray')
        
        def on_url_focus_in(event):
            if url_entry.get() == "Enter playlist URL (SoundCloud, YouTube, etc.)":
                url_entry.delete(0, tk.END)
                url_entry.config(fg='black')
                
        def on_url_focus_out(event):
            if url_entry.get() == "":
                url_entry.insert(0, "Enter playlist URL (SoundCloud, YouTube, etc.)")
                url_entry.config(fg='gray')
            self.update_format_options()
                
        def on_url_change(*args):
            self.update_format_options()
                
        url_entry.bind('<FocusIn>', on_url_focus_in)
        url_entry.bind('<FocusOut>', on_url_focus_out)
        url_entry.bind('<KeyRelease>', lambda e: self.update_format_options())
        
        # Directory Section
        dir_frame = tk.LabelFrame(main_frame, text="📁 Output Directory", 
                                 font=label_font, bg=bg_color, fg=primary_color, padx=15, pady=15)
        dir_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        dir_frame.grid_columnconfigure(0, weight=1)
        
        self.directory_var = tk.StringVar()
        directory_entry = tk.Entry(dir_frame, textvariable=self.directory_var, font=label_font, 
                                  width=50, relief="solid", bd=1)
        directory_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        browse_btn = tk.Button(dir_frame, text="📂 Browse", command=self.select_directory, 
                              bg=secondary_color, fg="white", font=label_font, width=12,
                              cursor="hand2", relief="flat")
        browse_btn.grid(row=0, column=1, padx=(10, 5), pady=5)
        
        # Cookies Section with Help Button
        cookies_frame = tk.LabelFrame(main_frame, text="🍪 Cookies File (Optional)", 
                                     font=label_font, bg=bg_color, fg=primary_color, padx=15, pady=15)
        cookies_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        cookies_frame.grid_columnconfigure(0, weight=1)
        
        self.cookies_var = tk.StringVar()
        cookies_entry = tk.Entry(cookies_frame, textvariable=self.cookies_var, font=label_font, 
                                width=50, relief="solid", bd=1)
        cookies_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        cookies_btn = tk.Button(cookies_frame, text="📄 Browse", command=self.select_cookies_file, 
                               bg=secondary_color, fg="white", font=label_font, width=12,
                               cursor="hand2", relief="flat")
        cookies_btn.grid(row=0, column=1, padx=(10, 5), pady=5)
        
        cookies_clear_btn = tk.Button(cookies_frame, text="❌ Clear", command=self.clear_cookies, 
                                     bg=warning_color, fg="white", font=label_font, width=8,
                                     cursor="hand2", relief="flat")
        cookies_clear_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Help button for cookies
        cookies_help_btn = tk.Button(cookies_frame, text="❓ Help", command=self.show_cookies_help, 
                                    bg=info_color, fg="white", font=label_font, width=8,
                                    cursor="hand2", relief="flat")
        cookies_help_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Options Section
        options_frame = tk.LabelFrame(main_frame, text="⚙️ Download Options", 
                                     font=label_font, bg=bg_color, fg=primary_color, padx=15, pady=15)
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        # Format selection
        tk.Label(options_frame, text="Output Format:", font=label_font, bg=bg_color, fg=primary_color).grid(
            row=0, column=0, padx=5, pady=8, sticky="w")
        
        self.format_var = tk.StringVar(value="MP3")
        self.format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, 
                                   values=["MP3", "Original Format"], state="readonly", font=label_font)
        self.format_combo.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        # Quality selection
        tk.Label(options_frame, text="Audio Quality:", font=label_font, bg=bg_color, fg=primary_color).grid(
            row=0, column=2, padx=(20, 5), pady=8, sticky="w")
        
        self.quality_var = tk.StringVar(value="Best Available")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, 
                                    values=["Best Available", "Good", "Normal"], state="readonly", font=label_font)
        quality_combo.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        
        # Progress Section
        progress_frame = tk.Frame(main_frame, bg=bg_color)
        progress_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to download...")
        progress_label = tk.Label(progress_frame, textvariable=self.progress_var, 
                                 font=label_font, bg=bg_color, fg=primary_color)
        progress_label.grid(row=0, column=0, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Action Buttons
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.download_btn = tk.Button(button_frame, text="🚀 Start Download", command=self.start_download, 
                                     bg=accent_color, fg="white", font=("Arial", 12, "bold"), 
                                     width=18, height=2, cursor="hand2", relief="flat")
        self.download_btn.grid(row=0, column=0, padx=10)
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear All", command=self.clear_all, 
                             bg=warning_color, fg="white", font=label_font, 
                             width=15, cursor="hand2", relief="flat")
        clear_btn.grid(row=0, column=1, padx=10)
        
        # Footer with credits (now inside scrollable area)
        footer_frame = tk.Frame(main_frame, bg=primary_color, height=60)
        footer_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        footer_frame.grid_propagate(False)
        footer_frame.grid_columnconfigure(0, weight=1)
        
        # Footer label with clickable GitHub link
        def open_github(event):
            webbrowser.open_new("https://github.com/Hussein119")

        footer_label = tk.Label(
            footer_frame,
            text="Powered by Hussein AK \nContact: github.com/Hussein119",
            font=("Arial", 11, "italic"),
            bg=primary_color,
            fg="white",
            cursor="hand2",
            justify="center"
        )
        footer_label.grid(row=0, column=0, pady=12)
        footer_label.bind("<Button-1>", open_github)
        
        # Add hover effects
        self.add_hover_effects([browse_btn, cookies_btn, cookies_clear_btn, cookies_help_btn, self.download_btn, clear_btn])
        
        # Initialize format options
        self.update_format_options()

    def show_cookies_help(self):
        """Show detailed instructions on how to get cookies file"""
        help_window = tk.Toplevel(self.root)
        help_window.title("🍪 How to Get Cookies File")
        help_window.geometry("700x600")
        help_window.resizable(True, True)
        help_window.configure(bg="#f8f9fa")
        
        # Make window modal
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Create main frame
        main_frame = tk.Frame(help_window, bg="#f8f9fa", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🍪 How to Get Cookies File", 
                              font=("Arial", 16, "bold"), bg="#f8f9fa", fg="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Create scrollable text area
        text_frame = tk.Frame(main_frame, bg="#f8f9fa")
        text_frame.pack(fill="both", expand=True)
        
        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Arial", 11),
                                            bg="white", fg="#2c3e50", relief="solid", bd=1)
        text_area.pack(fill="both", expand=True)
        
        # Help content
        help_content = """📝 Why do you need cookies?

Cookies help bypass rate limits and access private/age-restricted content on some platforms. They're optional but can improve download success rates.

🌐 Method 1: Browser Extension (Recommended)

For Chrome/Edge:
1. Install "Get cookies.txt LOCALLY" extension from Chrome Web Store
2. Go to the website you want to download from (YouTube, SoundCloud, etc.)
3. Log in to your account if needed
4. Click the extension icon
5. Click "Export" to download cookies.txt file

For Firefox:
1. Install "cookies.txt" extension
2. Visit the target website and log in
3. Click the extension icon
4. Choose "Current Site" and export

🔧 Method 2: Browser Developer Tools

For any browser:
1. Open the website and log in
2. Press F12 to open Developer Tools
3. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
4. Click "Cookies" in the left sidebar
5. Select the website domain
6. Right-click and "Copy all as Netscape format"
7. Paste into a text file and save as cookies.txt

📱 Method 3: Mobile (Android)

Using Kiwi Browser:
1. Install Kiwi Browser (supports Chrome extensions)
2. Add "Get cookies.txt LOCALLY" extension
3. Visit the website and log in
4. Export cookies using the extension

⚠️ Important Notes:

• Never share your cookies file - it contains login information
• Cookies expire after some time (usually days/weeks)
• Only use cookies from sites you trust
• Some sites may detect and block cookie usage

🔒 Privacy & Security:

• Cookies contain sensitive session data
• Keep cookies files secure and delete when not needed
• Only use with reputable downloaders
• Log out and clear cookies if you suspect compromise

🎯 Platform-Specific Tips:

YouTube:
- Helps with age-restricted content
- May bypass some regional restrictions
- Useful for private playlists you have access to

SoundCloud:
- Access private tracks you're authorized to hear
- Bypass some rate limits
- Better success with large playlists

Instagram/TikTok:
- Required for private accounts
- Helps with stories and highlights
- Reduces rate limiting

💡 Troubleshooting:

If downloads fail even with cookies:
1. Try refreshing cookies (re-export from browser)
2. Make sure you're logged in when exporting
3. Check if the content is actually accessible in your browser
4. Some content may still be protected despite cookies

Remember: Respect content creators' rights and platform terms of service!"""
        
        text_area.insert(tk.END, help_content)
        text_area.config(state="disabled")  # Make read-only
        
        # Close button
        close_btn = tk.Button(main_frame, text="✅ Got it!", command=help_window.destroy,
                             bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                             width=15, cursor="hand2", relief="flat")
        close_btn.pack(pady=(20, 0))
        
        # Center the help window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
    def add_hover_effects(self, buttons):
        def on_enter(e):
            e.widget.config(relief="raised")
            
        def on_leave(e):
            e.widget.config(relief="flat")
            
        for btn in buttons:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
    def select_directory(self):
        directory = filedialog.askdirectory(title="Select Download Directory")
        if directory:
            self.directory_var.set(directory)
            
    def select_cookies_file(self):
        cookies_file = filedialog.askopenfilename(
            title="Select Cookies File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if cookies_file:
            self.cookies_var.set(cookies_file)
            
    def clear_cookies(self):
        self.cookies_var.set("")
        
    def clear_all(self):
        self.url_var.set("")
        self.directory_var.set("")
        self.cookies_var.set("")
        self.progress_var.set("Ready to download...")
        self.progress_bar.stop()
        self.update_format_options()
        
    def is_youtube_url(self, url):
        """Check if the URL is from YouTube"""
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
        return any(domain in url.lower() for domain in youtube_domains)
        
    def update_format_options(self):
        """Update format options based on URL"""
        url = self.url_var.get().strip()
        
        if url and url != "Enter playlist URL (SoundCloud, YouTube, etc.)" and self.is_youtube_url(url):
            # YouTube URL - show MP3, MP4, and Original Format options
            self.format_combo['values'] = ["MP3", "MP4", "Original Format"]
        else:
            # Non-YouTube URL - show MP3 and Original Format only
            self.format_combo['values'] = ["MP3", "Original Format"]
            
        # Reset to MP3 if current selection is not available
        current_format = self.format_var.get()
        if current_format not in self.format_combo['values']:
            self.format_var.set("MP3")
        
    def validate_inputs(self):
        url = self.url_var.get().strip()
        directory = self.directory_var.get().strip()
        
        if not url or url == "Enter playlist URL (SoundCloud, YouTube, etc.)":
            messagebox.showerror("Error", "Please provide a valid playlist URL.")
            return False
            
        if not directory:
            messagebox.showerror("Error", "Please select a download directory.")
            return False
            
        return True
     
    def start_download(self):
        if not self.validate_inputs():
            return
            
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download is already in progress!")
            return
            
        # Start download in separate thread
        self.download_thread = threading.Thread(target=self.download_playlist)
        self.download_thread.daemon = True
        self.download_thread.start()

    def download_playlist(self):
        self.is_downloading = True
        self.download_btn.config(state="disabled", text="⏳ Downloading...")
        self.progress_bar.start()
        self.progress_var.set("Preparing download...")
        
        try:
            playlist_url = self.url_var.get().strip()
            save_directory = self.directory_var.get().strip()
            cookies_file = self.cookies_var.get().strip()
            
            # Create directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
                
            # Configure yt-dlp options
            selected_format = self.format_var.get()
            
            if selected_format == "MP4" and self.is_youtube_url(playlist_url):
                cmd = [
                    "python", "-m", "yt_dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "--merge-output-format", "mp4",
                    "--output", os.path.join(save_directory, "%(playlist_index)s - %(title)s.%(ext)s")
                ]
                cmd.append(playlist_url)
                process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                self.processes.append(process)  # Track the subprocess
                process.wait()  # Wait for completion
                self.progress_var.set("MP4 files downloaded successfully!")
                messagebox.showinfo("Success", 
                                  f"Playlist downloaded successfully!\n"
                                  f"Format: {selected_format}\n"
                                  f"Location: {save_directory}")
            else:
                # For SoundCloud and other platforms, or MP3 format
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(save_directory, '%(playlist_index)s - %(title)s.%(ext)s'),
                    'noplaylist': False,
                    'postprocessors': [],
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                }
            
                # Add cookies file if provided
                if cookies_file and os.path.exists(cookies_file):
                    ydl_opts['cookiefile'] = cookies_file
                
                # Add additional options for better compatibility
                ydl_opts.update({
                    'ignoreerrors': True,  # Continue on download errors
                    'no_warnings': False,
                    'extractaudio': False,
                    'embed_subs': False,
                    'writeautomaticsub': False,
                })
                
                self.progress_var.set("Extracting playlist information...")
                
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(playlist_url, download=True)
                    playlist_title = info_dict.get('title', 'playlist')
                    entries = info_dict.get('entries', [])
                    
                    # Handle format conversion for MP3
                    if selected_format == "MP3":
                        self.progress_var.set("Converting to MP3...")
                        total_files = len(entries)
                        
                        for i, entry in enumerate(entries):
                            try:
                                if entry is None:  # Skip failed entries
                                    continue
                                    
                                file_path = ydl.prepare_filename(entry)
                                if file_path and os.path.exists(file_path) and not file_path.endswith('.mp3'):
                                    self.progress_var.set(f"Converting to MP3... ({i+1}/{total_files})")
                                    audio = AudioSegment.from_file(file_path)
                                    mp3_path = os.path.splitext(file_path)[0] + '.mp3'
                                    audio.export(mp3_path, format='mp3')
                                    os.remove(file_path)
                            except Exception as e:
                                print(f"Error converting file {i+1}: {e}")
                                continue
                        
                        self.progress_var.set("Download and conversion completed successfully!")
                    else:
                        self.progress_var.set("Files downloaded in original format!")
                    
                    successful_downloads = len([e for e in entries if e is not None])
                    messagebox.showinfo("Success", 
                                      f"Playlist '{playlist_title}' downloaded successfully!\n"
                                      f"Format: {selected_format}\n"
                                      f"Location: {save_directory}\n"
                                      f"Files downloaded: {successful_downloads}")
                              
        except Exception as e:
            self.progress_var.set("Download failed!")
            error_msg = str(e)
            
            if "Requested format is not available" in error_msg:
                error_msg += "\n\nTip: Try selecting 'Original Format' instead of MP4, or check if the videos support the requested quality."
            elif "Private video" in error_msg:
                error_msg += "\n\nTip: Some videos in the playlist might be private. Try using a cookies file if you have access."
            elif "Video unavailable" in error_msg:
                error_msg += "\n\nTip: Some videos might be region-locked or removed. The downloader will skip these."
                
            messagebox.showerror("Error", f"Download failed:\n{error_msg}")
            
        finally:
            self.is_downloading = False
            self.download_btn.config(state="normal", text="🚀 Start Download")
            self.progress_bar.stop()
            self.processes = []  # Clear tracked processes

    def on_closing(self):
        if self.is_downloading:
            if messagebox.askokcancel("Quit", "Download is in progress. Are you sure you want to quit?"):
                self.progress_bar.stop()
                
                for process in self.processes:
                    try:
                        if process.poll() is None:  # Still running
                            if os.name == 'nt':
                                process.send_signal(signal.CTRL_BREAK_EVENT)
                            else:
                                process.terminate()
                            process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    except Exception as e:
                        print(f"Error terminating process: {e}")

                self.processes = []
                self.is_downloading = False
                self.download_btn.config(state="normal", text="🚀 Start Download")
                self.progress_var.set("Download cancelled.")
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = MediaDownloaderGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()