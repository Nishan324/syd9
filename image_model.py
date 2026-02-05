import os
import cv2
import numpy as np


class imagemodel:
    def __init__(self):
        self._image_bgr = None
        self._filename = None
        self._undo_stack = []
        self._redo_stack = []
        self._preview_base = None
        self._is_previewing = False

    @property
    def filename(self):
        return self._filename

    @property
    def has_image(self) -> bool:
        return self._image_bgr is not None

    def get_image(self) -> np.ndarray:
        return self._image_bgr

    def get_info(self) -> str:
        if self._image_bgr is None:
            return "No image loaded"
        h, w = self._image_bgr.shape[:2]
        name = os.path.basename(self._filename) if self._filename else "Untitled"
        return f"{name}  |  {w}x{h}px  |  BGR"

    def load(self, path: str):
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Could not read this file as an image.")
        self._image_bgr = img
        self._filename = path
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._stop_preview()

    def set_image(self, new_bgr: np.ndarray, push_undo: bool = True):
        if new_bgr is None:
            return
        if push_undo and self._image_bgr is not None:
            self._undo_stack.append(self._image_bgr.copy())
            self._redo_stack.clear()
        self._image_bgr = new_bgr
        self._stop_preview()

    def undo(self):
        if not self._undo_stack or self._image_bgr is None:
            return
        self._redo_stack.append(self._image_bgr.copy())
        self._image_bgr = self._undo_stack.pop()
        self._stop_preview()

    def redo(self):
        if not self._redo_stack or self._image_bgr is None:
            return
        self._undo_stack.append(self._image_bgr.copy())
        self._image_bgr = self._redo_stack.pop()
        self._stop_preview()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def start_preview(self):
        if self._image_bgr is None or self._is_previewing:
            return
        self._preview_base = self._image_bgr.copy()
        self._is_previewing = True

    def preview_image(self, preview_bgr: np.ndarray):
        if self._image_bgr is None:
            return
        self._image_bgr = preview_bgr

    def commit_preview(self):
        if not self._is_previewing or self._preview_base is None or self._image_bgr is None:
            return
        self._undo_stack.append(self._preview_base.copy())
        self._redo_stack.clear()
        self._stop_preview()

    def cancel_preview(self):
        if not self._is_previewing or self._preview_base is None:
            return
        self._image_bgr = self._preview_base.copy()
        self._stop_preview()

    def _stop_preview(self):
        self._preview_base = None
        self._is_previewing = False
