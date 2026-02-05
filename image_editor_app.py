import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk

from image_processor import imageprocessor
from image_model import imagemodel


SUPPORTED_FORMATS = [
    ("Image Files", "*.jpg *.jpeg *.png *.bmp"),
    ("JPEG", "*.jpg *.jpeg"),
    ("PNG", "*.png"),
    ("BMP", "*.bmp"),
]


class imageeditorappp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Editor")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.model = imagemodel()
        self.proc = imageprocessor()

        self._photo = None
        self._current_save_path = None

        self._build_menu()
        self._build_layout()
        self._update_ui_state()

   
    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)
        self._file_menu = file_menu
        self._edit_menu = edit_menu

    
    def _build_layout(self):
        self.main = ttk.Frame(self.root)
        self.main.pack(fill=tk.BOTH, expand=True)

        # Left controls
        self.controls = ttk.Frame(self.main, padding=10)
        self.controls.pack(side=tk.LEFT, fill=tk.Y)

        # Right display
        self.display_frame = ttk.Frame(self.main, padding=10)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.display_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

       
        self.status_var = tk.StringVar(value="No image loaded")
        self.status = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Label(self.controls, text="Controls", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        
        ttk.Button(self.controls, text="Open Image", command=self.open_image).pack(fill=tk.X, pady=2)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=8)

        
        ttk.Button(self.controls, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=2)
        ttk.Button(self.controls, text="Edge Detect (Canny)", command=self.apply_edges).pack(fill=tk.X, pady=2)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=8)

       
        self._add_slider("Blur", 0, 25, 0, "blur", is_int=True)
        self._add_slider("Brightness", -100, 100, 0, "bright", is_int=True)
        self._add_slider("Contrast", 0.5, 2.0, 1.0, "contrast", is_int=False)
        self._add_slider("Resize", 0.2, 2.0, 1.0, "scale", is_int=False)

        ttk.Button(self.controls, text="Apply Sliders", command=self.commit_sliders).pack(fill=tk.X, pady=(8, 2))
        ttk.Button(self.controls, text="Reset Sliders", command=self._reset_sliders).pack(fill=tk.X, pady=2)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=8)

       
        ttk.Label(self.controls, text="Rotate", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        rot = ttk.Frame(self.controls)
        rot.pack(fill=tk.X, pady=4)
        ttk.Button(rot, text="90°", command=lambda: self.apply_rotate(90)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(rot, text="180°", command=lambda: self.apply_rotate(180)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(rot, text="270°", command=lambda: self.apply_rotate(270)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Label(self.controls, text="Flip", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        flip = ttk.Frame(self.controls)
        flip.pack(fill=tk.X, pady=4)
        ttk.Button(flip, text="Horizontal", command=lambda: self.apply_flip("horizontal")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(flip, text="Vertical", command=lambda: self.apply_flip("vertical")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.root.bind("<Configure>", lambda e: self._render(update_status=False))

    def _add_slider(self, title, f, t, default, key, is_int: bool):
        ttk.Label(self.controls, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))
        s = ttk.Scale(self.controls, from_=f, to=t, orient=tk.HORIZONTAL,
                      command=lambda v, k=key, ii=is_int: self._on_slider(k, v, ii))
        s.pack(fill=tk.X, pady=(2, 0))
        lbl = ttk.Label(self.controls, text=str(default))
        lbl.pack(anchor="e")

        setattr(self, f"{key}_slider", s)
        setattr(self, f"{key}_label", lbl)

        s.set(default)
        self._on_slider(key, default, is_int)

    def _on_slider(self, key, value, is_int):
        lbl = getattr(self, f"{key}_label", None)
        if lbl is None:
            return
        if is_int:
            lbl.config(text=str(int(float(value))))
        else:
            lbl.config(text=f"{float(value):.2f}")

   
    def open_image(self):
        path = filedialog.askopenfilename(title="Open Image", filetypes=SUPPORTED_FORMATS)
        if not path:
            return
        try:
            self.model.load(path)
            self._current_save_path = None
            self._reset_sliders()
            self._render()
            self._update_ui_state()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def save_image(self):
        if not self._ensure_image():
            return
        if self._current_save_path:
            try:
                self.model.save(self._current_save_path)
                self.status_var.set(f"Saved: {self._current_save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{e}")
        else:
            self.save_image_as()

    def save_image_as(self):
        if not self._ensure_image():
            return
        path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp")]
        )
        if not path:
            return
        try:
            self.model.save(path)
            self._current_save_path = path
            self.status_var.set(f"Saved: {path}")
            self._update_ui_state()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{e}")

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the Photo Editor?"):
            self.root.destroy()

 
    def undo(self):
        if self.model.undo():
            self._render()
        self._update_ui_state()

    def redo(self):
        if self.model.redo():
            self._render()
        self._update_ui_state()

   
    def apply_grayscale(self):
        if not self._ensure_image():
            return
        out = self.proc.to_grayscale(self.model.image)
        self.model.push(out)
        self._render()
        self._update_ui_state()

    def apply_edges(self):
        if not self._ensure_image():
            return
        out = self.proc.canny_edges(self.model.image)
        self.model.push(out)
        self._render()
        self._update_ui_state()

    def apply_rotate(self, degrees: int):
        if not self._ensure_image():
            return
        out = self.proc.rotate(self.model.image, degrees)
        self.model.push(out)
        self._render()
        self._update_ui_state()

    def apply_flip(self, mode: str):
        if not self._ensure_image():
            return
        out = self.proc.flip(self.model.image, mode)
        self.model.push(out)
        self._render()
        self._update_ui_state()

    def commit_sliders(self):
        if not self._ensure_image():
            return

        img = self.model.image.copy()

        blur = int(float(self.blur_slider.get()))
        bright = int(float(self.bright_slider.get()))
        contrast = float(self.contrast_slider.get())
        scale = float(self.scale_slider.get())

        
        img = self.proc.blur(img, blur)

        
        img = self.proc.brightness_contrast(img, bright, contrast)

       
        img = self.proc.resize(img, scale)

        self.model.push(img)
        self._render()
        self._update_ui_state()

    def _reset_sliders(self):
        self.blur_slider.set(0)
        self.bright_slider.set(0)
        self.contrast_slider.set(1.0)
        self.scale_slider.set(1.0)
        self._on_slider("blur", 0, True)
        self._on_slider("bright", 0, True)
        self._on_slider("contrast", 1.0, False)
        self._on_slider("scale", 1.0, False)

    
    def _render_image(self, update_status=True):
      
        self._render(update_status=update_status)

    def _render(self, update_status=True):
        if not self.model.has_image:
            self.canvas.delete("all")
            if update_status:
                self.status_var.set("No image loaded")
            return

        img = self.model.image

        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        canvas_w = max(self.canvas.winfo_width(), 1)
        canvas_h = max(self.canvas.winfo_height(), 1)

        iw, ih = pil_img.size
        scale = min(canvas_w / iw, canvas_h / ih)
        new_w = max(int(iw * scale), 1)
        new_h = max(int(ih * scale), 1)

        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w // 2, canvas_h // 2, anchor="center", image=self._photo)

        if update_status:
            self.status_var.set(self.model.get_info())

  
    def _update_ui_state(self):
        has = self.model.has_image
        self._file_menu.entryconfig("Save", state=("normal" if has else "disabled"))
        self._file_menu.entryconfig("Save As...", state=("normal" if has else "disabled"))
        self._edit_menu.entryconfig("Undo", state=("normal" if self.model.can_undo() else "disabled"))
        self._edit_menu.entryconfig("Redo", state=("normal" if self.model.can_redo() else "disabled"))
        self.status_var.set(self.model.get_info() if has else "No image loaded")

    def _ensure_image(self, silent=False) -> bool:
        if not self.model.has_image:
            if not silent:
                messagebox.showwarning("No Image", "Please open an image first (File → Open or Open Image button).")
            return False
        return True
