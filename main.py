import tkinter as tk
from tkinter import ttk

from image_editor_app import imageeditorappp


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass

    app = imageeditorappp(root)

    
    def on_resize(event):
        if hasattr(app, "_render_image"):
            app._render_image(update_status=False)
        else:
            app._render(update_status=False)

    root.bind("<Configure>", on_resize)
    root.mainloop()


if __name__ == "__main__":
    main()
