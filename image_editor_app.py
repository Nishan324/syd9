import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

from image_processor import imageprocessor

from image_model import imagemodel


SUPPORTED_FORMATS = [("Image Files", "*.jpg *.jpeg *.png *.bmp"),
                     ("JPEG", "*.jpg *.jpeg"),
                     ("PNG", "*.png"),
                     ("BMP", "*.bmp")]


class imageeditorappp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo editor")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.model = imagemodel()
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

        self.controls = ttk.Frame(self.main, padding=10)
        self.controls.pack(side=tk.LEFT, fill=tk.Y)

        self.display_frame = ttk.Frame(self.main, padding=10)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.display_frame, bg="#797979", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="No image loaded")
        self.status = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=6)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Label(self.controls, text="Effects / Tools", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

        btn_frame1 = ttk.Frame(self.controls)
        btn_frame1.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame1, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame1, text="Edge Detect (Canny)", command=self.apply_edges).pack(fill=tk.X, pady=2)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=10)

        ttk.Label(self.controls, text="Blur", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.blur_slider = ttk.Scale(self.controls, from_=0, to=30, orient=tk.HORIZONTAL, command=self._on_blur_change)
        self.blur_slider.pack(fill=tk.X, pady=(4, 2))
        self.blur_value_label = ttk.Label(self.controls, text="0")
        self.blur_value_label.pack(anchor="e")

        ttk.Label(self.controls, text="Brightness", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 0))
        self.bright_slider = ttk.Scale(self.controls, from_=-100, to=100, orient=tk.HORIZONTAL, command=self._on_bc_change)
        self.bright_slider.pack(fill=tk.X, pady=(4, 2))
        self.bright_value_label = ttk.Label(self.controls, text="0")
        self.bright_value_label.pack(anchor="e")

        ttk.Label(self.controls, text="Contrast", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 0))
        self.contrast_slider = ttk.Scale(self.controls, from_=0.5, to=2.0, orient=tk.HORIZONTAL, command=self._on_bc_change)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X, pady=(4, 2))
        self.contrast_value_label = ttk.Label(self.controls, text="1.00")
        self.contrast_value_label.pack(anchor="e")

        bc_btns = ttk.Frame(self.controls)
        bc_btns.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(bc_btns, text="Apply Sliders", command=self.commit_sliders).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        ttk.Button(bc_btns, text="Cancel Sliders", command=self.cancel_sliders).pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=10)

        ttk.Label(self.controls, text="Rotate", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        rot = ttk.Frame(self.controls)
        rot.pack(fill=tk.X, pady=5)
        ttk.Button(rot, text="90°", command=lambda: self.apply_rotate(90)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(rot, text="180°", command=lambda: self.apply_rotate(180)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(rot, text="270°", command=lambda: self.apply_rotate(270)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Label(self.controls, text="Flip", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 0))
        flip = ttk.Frame(self.controls)
        flip.pack(fill=tk.X, pady=5)
        ttk.Button(flip, text="Horizontal", command=lambda: self.apply_flip("horizontal")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(flip, text="Vertical", command=lambda: self.apply_flip("vertical")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Separator(self.controls).pack(fill=tk.X, pady=10)

        ttk.Label(self.controls, text="Resize", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.scale_slider = ttk.Scale(self.controls, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=self._on_scale_label)
        self.scale_slider.set(1.0)
        self.scale_slider.pack(fill=tk.X, pady=(4, 2))
        self.scale_value_label = ttk.Label(self.controls, text="1.00")
        self.scale_value_label.pack(anchor="e")

        ttk.Button(self.controls, text="Apply Resize", command=self.apply_resize).pack(fill=tk.X, pady=(6, 0))

        self.controls.bind_all("<ButtonRelease-1>", self._maybe_commit_preview)

    # ---------- File ----------
    def open_image(self):
        path = filedialog.askopenfilename(title="Open Image", filetypes=SUPPORTED_FORMATS)
        if not path:
            return
        try:
            self.model.load(path)
            self._current_save_path = path
            self._reset_sliders()
            self._render_image()
            self._update_ui_state()
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def save_image(self):
        if not self.model.has_image:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        if self._current_save_path:
            self._save_to_path(self._current_save_path)
        else:
            self.save_image_as()

    def save_image_as(self):
        if not self.model.has_image:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        path = filedialog.asksaveasfilename(title="Save Image As", defaultextension=".png", filetypes=SUPPORTED_FORMATS)
        if not path:
            return
        self._save_to_path(path)
        self._current_save_path = path
        self._update_ui_state()

    def _save_to_path(self, path: str):
        try:
            bgr = self.model.get_image()
            ok = cv2.imwrite(path, bgr)
            if not ok:
                raise ValueError("OpenCV failed to write the file.")
            messagebox.showinfo("Saved", f"Image saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    # ---------- Edit ----------
    def undo(self):
        if not self.model.has_image:
            return
        self.model.undo()
        self._render_image()
        self._update_ui_state()

    def redo(self):
        if not self.model.has_image:
            return
        self.model.redo()
        self._render_image()
        self._update_ui_state()

    # ---------- Operations ----------
    def apply_grayscale(self):
        if not self._ensure_image():
            return
        out = imageprocessor.to_grayscale(self.model.get_image())
        self.model.set_image(out, push_undo=True)
        self._render_image()
        self._update_ui_state()

    def apply_edges(self):
        if not self._ensure_image():
            return
        out = imageprocessor.canny_edges(self.model.get_image(), 100, 200)
        self.model.set_image(out, push_undo=True)
        self._render_image()
        self._update_ui_state()

    def apply_rotate(self, deg: int):
        if not self._ensure_image():
            return
        out = imageprocessor.rotate(self.model.get_image(), deg)
        self.model.set_image(out, push_undo=True)
        self._render_image()
        self._update_ui_state()

    def apply_flip(self, mode: str):
        if not self._ensure_image():
            return
        out = imageprocessor.flip(self.model.get_image(), mode)
        self.model.set_image(out, push_undo=True)
        self._render_image()
        self._update_ui_state()

    def apply_resize(self):
        if not self._ensure_image():
            return
        scale = float(self.scale_slider.get())
        if scale <= 0:
            messagebox.showerror("Error", "Invalid Scale")
            return
        out = imageprocessor.resize_scale(self.model.get_image(), scale)
        self.model.set_image(out, push_undo=True)
        self._render_image()
        self._update_ui_state()

    # ---------- Slider Preview ----------
    def _on_blur_change(self, _value):
        if not self._ensure_image(silent=True):
            self.blur_value_label.config(text="0")
            return
        intensity = int(float(self.blur_slider.get()))
        self.blur_value_label.config(text=str(intensity))

        self.model.start_preview()
        base = self.model._preview_base if self.model._preview_base is not None else self.model.get_image()
        out = imageprocessor.gaussian_blur(base, intensity)
        self.model.preview_image(out)
        self._render_image(update_status=False)

    def _on_bc_change(self, _value):
        if not self._ensure_image(silent=True):
            self.bright_value_label.config(text="0")
            self.contrast_value_label.config(text="1.00")
            return

        b = int(float(self.bright_slider.get()))
        c = float(self.contrast_slider.get())
        self.bright_value_label.config(text=str(b))
        self.contrast_value_label.config(text=f"{c:.2f}")

        self.model.start_preview()
        base = self.model._preview_base if self.model._preview_base is not None else self.model.get_image()
        out = imageprocessor.adjust_brightness_contrast(base, brightness=b, contrast=c)
        self.model.preview_image(out)
        self._render_image(update_status=False)

    def commit_sliders(self):
        if not self._ensure_image(silent=True):
            return
        self.model.commit_preview()
        self._render_image()
        self._update_ui_state()

    def cancel_sliders(self):
        if not self._ensure_image(silent=True):
            return
        self.model.cancel_preview()
        self._reset_sliders()
        self._render_image()
        self._update_ui_state()

    def _maybe_commit_preview(self, event):
        if not self.model.has_image:
            return
        if self.model._is_previewing:
            self.model.commit_preview()
            self._render_image()
            self._update_ui_state()

    def _on_scale_label(self, _value):
        self.scale_value_label.config(text=f"{float(self.scale_slider.get()):.2f}")

    # ---------- Render ----------
    def _render_image(self, update_status=True):
        self.canvas.delete("all")
        if not self.model.has_image:
            self.canvas.create_text(10, 10, anchor="nw", fill="white", text="Open an image (File → Open)...")
            if update_status:
                self.status_var.set("No image loaded")
            return

        bgr = self.model.get_image()
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())
        img_w, img_h = pil_img.size

        scale = min(canvas_w / img_w, canvas_h / img_h)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(pil_img)
        x = (canvas_w - new_w) // 2
        y = (canvas_h - new_h) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self._photo)

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
                messagebox.showwarning("No Image", "Please open an image first (File → Open).")
            return False
        return True

    def _reset_sliders(self):
        self.blur_slider.set(0)
        self.bright_slider.set(0)
        self.contrast_slider.set(1.0)
        self.scale_slider.set(1.0)
        self.blur_value_label.config(text="0")
        self.bright_value_label.config(text="0")
        self.contrast_value_label.config(text="1.00")
        self.scale_value_label.config(text="1.00")
