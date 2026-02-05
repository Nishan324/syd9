import cv2
import numpy as np


class imageprocessor:

    @staticmethod
    def to_grayscale(bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def gaussian_blur(bgr: np.ndarray, intensity: int) -> np.ndarray:
        if intensity <= 0:
            return bgr
        k = max(1, int(intensity))
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(bgr, (k, k), 0)

    @staticmethod
    def canny_edges(bgr: np.ndarray, t1: int = 100, t2: int = 200) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, t1, t2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def adjust_brightness_contrast(bgr: np.ndarray, brightness: int, contrast: float) -> np.ndarray:
        alpha = float(contrast)
        beta = int(brightness)
        return cv2.convertScaleAbs(bgr, alpha=alpha, beta=beta)

    @staticmethod
    def rotate(bgr: np.ndarray, degrees: int) -> np.ndarray:
        if degrees == 90:
            return cv2.rotate(bgr, cv2.ROTATE_90_CLOCKWISE)
        if degrees == 180:
            return cv2.rotate(bgr, cv2.ROTATE_180)
        if degrees == 270:
            return cv2.rotate(bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return bgr

    @staticmethod
    def flip(bgr: np.ndarray, mode: str) -> np.ndarray:
        if mode == "horizontal":
            return cv2.flip(bgr, 1)
        if mode == "vertical":
            return cv2.flip(bgr, 0)
        return bgr

    @staticmethod
    def resize_scale(bgr: np.ndarray, scale: float) -> np.ndarray:
        if scale <= 0:
            return bgr
        h, w = bgr.shape[:2]
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
