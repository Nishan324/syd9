import tkinter as tk
from tkinter import ttk
from image_editor_app import imageeditorappp


def main():
    root = tk.Tk()

    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    app = imageeditorappp(root)

    def on_resize(_event):
        app._render_image(update_status=False)

    app.canvas.bind("<Configure>", on_resize)

    root.mainloop()


if __name__ == "__main__":
    main()
