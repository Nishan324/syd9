import os
import cv2


class imagemodel:
    def __init__(self):
        
        self._image_bgr = None
        self._filepath = None

        self._undo_stack = []
        self._redo_stack = []

    @property
    def has_image(self) -> bool:
        return self._image_bgr is not None

    
    @property
    def image(self):
        return self._image_bgr

    def load(self, path: str):
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Could not read image. Make sure it is JPG/PNG/BMP and not corrupted.")
        self._image_bgr = img
        self._filepath = path
        self._undo_stack.clear()
        self._redo_stack.clear()

    def save(self, path: str):
        if not self.has_image:
            raise ValueError("No image loaded.")
        ok = cv2.imwrite(path, self._image_bgr)
        if not ok:
            raise ValueError("Failed to save image (check permissions/path).")
        self._filepath = path

    def push(self, new_img):
        """Push new image with undo support."""
        if new_img is None:
            raise ValueError("push received None")
        if self._image_bgr is not None:
            self._undo_stack.append(self._image_bgr.copy())
            self._redo_stack.clear()
        self._image_bgr = new_img

    def undo(self) -> bool:
        if not self._undo_stack or self._image_bgr is None:
            return False
        self._redo_stack.append(self._image_bgr.copy())
        self._image_bgr = self._undo_stack.pop()
        return True

    def redo(self) -> bool:
        if not self._redo_stack or self._image_bgr is None:
            return False
        self._undo_stack.append(self._image_bgr.copy())
        self._image_bgr = self._redo_stack.pop()
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def get_info(self) -> str:
        if not self.has_image:
            return "No image loaded"
        h, w = self._image_bgr.shape[:2]
        name = os.path.basename(self._filepath) if self._filepath else "(unsaved)"
        return f"{name}  |  {w} x {h}"
