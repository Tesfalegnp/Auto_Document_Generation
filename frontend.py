import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import webbrowser
from pathlib import Path
import sys
import threading
import random
from shutil import which

PROJECT_ROOT = Path(__file__).parent.resolve()
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

AST_JSON = DOCS_DIR / "ast_summary.json"
README_MD = PROJECT_ROOT / "README_docs.md"
INDEX_HTML = DOCS_DIR / "index.html"


class AnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=50, bg_color="#161b22", fg_color="#58a6ff", hover_color="#238636"):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg="#0d1117")
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.text = text
        self.rect = self.create_rectangle(2, 2, width-2, height-2, fill=bg_color, outline=fg_color, width=2)
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg_color, font=("Segoe UI", 12, "bold"))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.animation_running = False
        self.pulse_radius = 0
        self.pulse_id = None
        
    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.start_pulse_animation()
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)
        self.stop_pulse_animation()
        
    def on_click(self, event):
        self.flash_animation()
        self.command()
        
    def start_pulse_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.animate_pulse()
            
    def stop_pulse_animation(self):
        self.animation_running = False
        if self.pulse_id:
            self.delete(self.pulse_id)
            self.pulse_id = None
            
    def animate_pulse(self):
        if not self.animation_running:
            return
        if self.pulse_id:
            self.delete(self.pulse_id)
        self.pulse_radius = (self.pulse_radius + 2) % 20
        w, h = self.winfo_width(), self.winfo_height()
        self.pulse_id = self.create_oval(w//2 - self.pulse_radius, h//2 - self.pulse_radius,
                                         w//2 + self.pulse_radius, h//2 + self.pulse_radius,
                                         outline=self.fg_color, width=1)
        self.after(50, self.animate_pulse)
        
    def flash_animation(self):
        original_color = self.hover_color
        for i in range(3):
            self.after(i * 100, lambda: self.itemconfig(self.rect, fill="#58a6ff"))
            self.after(i * 100 + 50, lambda: self.itemconfig(self.rect, fill=original_color))


class DocsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 AI POWERED AUTO DOCUMENT CREATOR")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        # Background canvas
        self.bg_canvas = tk.Canvas(self.root, bg="#0d1117", highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        
        self.bg_circles = []
        self.setup_background_animation()

        # Main frame (on top of background)
        self.main_frame = tk.Frame(self.bg_canvas, bg="#0d1117")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.title_label = tk.Label(self.main_frame, text="AI POWERED AUTO DOCUMENT CREATOR",
                                    font=("Segoe UI", 32, "bold"), fg="white", bg="#0d1117")
        self.title_label.pack(pady=(0, 20))
        
        subtitle = tk.Label(self.main_frame, text="Transform Your Code into Professional Documentation",
                            font=("Segoe UI", 14), fg="#8b949e", bg="#0d1117")
        subtitle.pack(pady=(0, 20))
        
        self.folder_path = tk.StringVar()
        self.label = tk.Label(self.main_frame, text="📁 Selected Folder: None", font=("Segoe UI", 12),
                              fg="#c9d1d9", bg="#0d1117")
        self.label.pack(pady=10)
        
        btn_frame = tk.Frame(self.main_frame, bg="#0d1117")
        btn_frame.pack(pady=20)
        
        self.btn_select = AnimatedButton(btn_frame, "📂 SELECT FOLDER", self.select_folder, width=200, height=50)
        self.btn_select.pack(side=tk.LEFT, padx=10)
        self.btn_run = AnimatedButton(btn_frame, "🚀 START PARSING", self.run_pipeline_thread, width=200, height=50)
        self.btn_run.pack(side=tk.LEFT, padx=10)
        
        self.console = scrolledtext.ScrolledText(self.main_frame, width=100, height=20, bg="#0d1117", fg="#58a6ff",
                                                 font=("Consolas", 10), state=tk.DISABLED)
        self.console.pack(pady=20)

    def select_folder(self):
        folder = filedialog.askdirectory()  # fully flexible explorer
        if folder:
            self.folder_path.set(folder)
            self.label.config(text=f"📁 Selected Folder: {folder}", fg="#58a6ff")
            self.root.after(1000, lambda: self.label.config(fg="#c9d1d9"))
    
    def print_console(self, message, color="#58a6ff"):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n")
        self.console.tag_add(color, f"end-{len(message)+1}c", "end")
        self.console.tag_config(color, foreground=color)
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)
        
    def run_pipeline_thread(self):
        threading.Thread(target=self.run_pipeline, daemon=True).start()
    
    def run_pipeline(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        target_root = Path(folder).resolve()
        
        def run_cmd(cmd, desc=""):
            self.print_console(f"🔄 {desc}", "#f0c674")
            self.print_console(f"$ {' '.join(map(str, cmd))}", "#8abeb7")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                self.print_console(result.stdout.strip())
            if result.stderr:
                self.print_console(result.stderr.strip(), "#ff6c6b")
            if result.returncode != 0:
                self.print_console(f"❌ Error: Command failed with code {result.returncode}", "#ff6c6b")
                raise subprocess.CalledProcessError(result.returncode, cmd)
        
        try:
            # Step 1
            run_cmd([sys.executable, "-m", "galaxy_ast_docs.build_parsers"], "1. Building language parsers...")
            # Step 2
            run_cmd([sys.executable, "-m", "galaxy_ast_docs.generate_ast_docs",
                     "--root", str(target_root), "--output", str(AST_JSON)], "2. Parsing code into AST...")
            # Step 3
            run_cmd([sys.executable, "-m", "llm.generate_readme",
                     "--json", str(AST_JSON), "--out", str(README_MD)], "3. Generating README with LLM...")
            # Step 4
            md_to_html_path = PROJECT_ROOT / "tools" / "md_to_html.py"
            if md_to_html_path.exists():
                run_cmd([sys.executable, "-m", "tools.md_to_html",
                         "--md", str(README_MD), "--out", str(INDEX_HTML)], "4. Converting README to HTML...")
                webbrowser.open(f"file://{INDEX_HTML}")
            self.print_console("✅ Documentation completed successfully!", "#50fa7b")
        except subprocess.CalledProcessError:
            self.print_console("❌ Pipeline failed. See above logs.", "#ff6c6b")
    
    def setup_background_animation(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        for _ in range(8):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            radius = random.randint(30, 100)
            speed_x = random.uniform(0.5, 2)
            speed_y = random.uniform(0.5, 2)
            color = random.choice(["#58a6ff", "#1f6feb", "#388bfd", "#79c0ff"])
            circle = {'x': x, 'y': y, 'radius': radius, 'speed_x': speed_x, 'speed_y': speed_y,
                      'id': self.bg_canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")}
            self.bg_circles.append(circle)
        self.animate_background()
    
    def animate_background(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        for circle in self.bg_circles:
            self.bg_canvas.move(circle['id'], circle['speed_x'], circle['speed_y'])
            x1, y1, x2, y2 = self.bg_canvas.coords(circle['id'])
            if x1 <= 0 or x2 >= width:
                circle['speed_x'] = -circle['speed_x']
            if y1 <= 0 or y2 >= height:
                circle['speed_y'] = -circle['speed_y']
        self.root.after(50, self.animate_background)


if __name__ == "__main__":
    root = tk.Tk()
    app = DocsApp(root)
    root.mainloop()
