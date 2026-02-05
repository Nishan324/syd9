import cv2
import numpy as np


class imageprocessor:
   
    def to_grayscale(self, img_bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

   
    def gaussian_blur(self, img_bgr: np.ndarray, intensity: int) -> np.ndarray:
        if intensity <= 0:
            return img_bgr
        k = int(intensity)
        if k < 1:
            k = 1
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(img_bgr, (k, k), 0)

 
    def canny_edges(self, img_bgr: np.ndarray, t1: int = 100, t2: int = 200) -> np.ndarray:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, t1, t2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

   
    def adjust_brightness_contrast(self, img_bgr: np.ndarray, brightness: int, contrast: float) -> np.ndarray:
        alpha = float(contrast)   # contrast
        beta = int(brightness)    # brightness
        return cv2.convertScaleAbs(img_bgr, alpha=alpha, beta=beta)


    def rotate(self, img_bgr: np.ndarray, degrees: int) -> np.ndarray:
        if degrees == 90:
            return cv2.rotate(img_bgr, cv2.ROTATE_90_CLOCKWISE)
        if degrees == 180:
            return cv2.rotate(img_bgr, cv2.ROTATE_180)
        if degrees == 270:
            return cv2.rotate(img_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img_bgr

  
    def flip(self, img_bgr: np.ndarray, mode: str) -> np.ndarray:
        if mode == "horizontal":
            return cv2.flip(img_bgr, 1)
        if mode == "vertical":
            return cv2.flip(img_bgr, 0)
        return img_bgr

    
    def resize_scale(self, img_bgr: np.ndarray, scale: float) -> np.ndarray:
        if scale <= 0:
            return img_bgr
        h, w = img_bgr.shape[:2]
        new_w = max(1, int(w * float(scale)))
        new_h = max(1, int(h * float(scale)))
        return cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

   
    def blur(self, img_bgr: np.ndarray, intensity: int) -> np.ndarray:
        return self.gaussian_blur(img_bgr, intensity)

    def brightness_contrast(self, img_bgr: np.ndarray, brightness: int, contrast: float) -> np.ndarray:
        return self.adjust_brightness_contrast(img_bgr, brightness, contrast)

    def resize(self, img_bgr: np.ndarray, scale: float) -> np.ndarray:
        return self.resize_scale(img_bgr, scale)
