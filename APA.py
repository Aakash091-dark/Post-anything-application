# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
from storage import StorageManager
from PIL import Image, ImageTk
import shutil

class CollegeConnectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Connect")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f2f5")
        
        self.storage = StorageManager()
        
        # Create and configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_posts()

    def setup_ui(self):
        # Top frame for input
        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="ew")
        
        # Style configuration
        style = ttk.Style()
        style.configure("Custom.TButton", 
                       padding=5, 
                       font=('Helvetica', 10))
        
        # Text input
        self.text_input = tk.Text(self.input_frame, 
                                 height=4, 
                                 width=50, 
                                 font=('Helvetica', 11),
                                 wrap=tk.WORD)
        self.text_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.input_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="e")
        
        # Upload button
        self.upload_btn = ttk.Button(self.buttons_frame, 
                                   text="Upload File", 
                                   command=self.upload_file,
                                   style="Custom.TButton")
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Post button
        self.post_btn = ttk.Button(self.buttons_frame, 
                                  text="Post", 
                                  command=self.create_post,
                                  style="Custom.TButton")
        self.post_btn.pack(side=tk.LEFT, padx=5)
        
        # Feed canvas with scrollbar
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, 
                                     orient="vertical", 
                                     command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), 
                                window=self.scrollable_frame, 
                                anchor="nw", 
                                width=self.canvas.winfo_reqwidth())
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure canvas scrolling
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_post(self):
        content = self.text_input.get("1.0", tk.END).strip()
        if content:
            self.storage.add_post(content)
            self.text_input.delete("1.0", tk.END)
            self.load_posts()
        else:
            messagebox.showwarning("Warning", "Please enter some text!")

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.storage.add_file(file_path)
            self.load_posts()

    def load_posts(self):
        # Clear existing posts
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        posts = self.storage.get_posts()
        
        for i, post in enumerate(posts):
            post_frame = ttk.Frame(self.scrollable_frame, 
                                 style="Card.TFrame")
            post_frame.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
            self.scrollable_frame.grid_columnconfigure(0, weight=1)
            
            if post['type'] == 'text':
                content_label = ttk.Label(
                    post_frame, 
                    text=post['content'],
                    wraplength=600,
                    style="Content.TLabel"
                )
                content_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")
            
            elif post['type'] == 'file':
                if post['file_type'] in ['.png', '.jpg', '.jpeg', '.gif']:
                    try:
                        img = Image.open(post['file_path'])
                        img.thumbnail((300, 300))
                        photo = ImageTk.PhotoImage(img)
                        img_label = tk.Label(post_frame, image=photo)
                        img_label.image = photo
                        img_label.grid(row=0, column=0, pady=5, padx=5)
                    except Exception as e:
                        ttk.Label(post_frame, 
                                text="Error loading image").grid(row=0, column=0)
                else:
                    file_name = os.path.basename(post['file_path'])
                    ttk.Label(post_frame, 
                            text=f"File: {file_name}").grid(row=0, column=0)
                    
                download_btn = ttk.Button(
                    post_frame,
                    text="Download",
                    command=lambda p=post: self.download_file(p['file_path']),
                    style="Custom.TButton"
                )
                download_btn.grid(row=1, column=0, pady=5)
            
            # Add timestamp
            timestamp = datetime.fromtimestamp(post['timestamp'])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(post_frame, 
                     text=time_str, 
                     style="Time.TLabel").grid(row=2, column=0, 
                                             pady=2, padx=5, sticky="e")

    def download_file(self, file_path):
        if os.path.exists(file_path):
            save_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(file_path)[1],
                initialfile=os.path.basename(file_path)
            )
            if save_path:
                shutil.copy2(file_path, save_path)
                messagebox.showinfo("Success", "File downloaded successfully!")
        else:
            messagebox.showerror("Error", "File not found!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeConnectApp(root)
    root.mainloop()