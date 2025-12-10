import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import numpy as np
import pytesseract
from PIL import Image


class ImagePreprocessing:
    """
    To handle image preprocessing
    """
    @staticmethod
    def deskew(image):
        """Deskew tilted images using opencv"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        crdnts = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(crdnts)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    @staticmethod
    def contrast_enhancement(image):
        """Enhance image contrast using histogram equalization"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def REmove_noise(image):
        """Remove noise from image using Gaussian blur"""
        return cv2.GaussianBlur(image, (5, 5), 0)
    
    @staticmethod
    def binarization(image):
        """Convert image to binary using Otsu's thresholding"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def preprocess_image(image_path):
        """Apply all preprocessing steps to the image"""
        image = cv2.imread(image_path)
        image = ImagePreprocessing.deskew(image)
        image = ImagePreprocessing.contrast_enhancement(image)
        image = ImagePreprocessing.REmove_noise(image)
        image = ImagePreprocessing.binarization(image)
        return image
    


if __name__ == "__main__":
    input_image_path = "images/page_30.jpg"
    output_image_path = "images/preprocessed_30.jpg"
    preprocessed_image = ImagePreprocessing.preprocess_image(input_image_path)
    cv2.imwrite(output_image_path, preprocessed_image)
    print(f"Preprocessed image saved to {output_image_path}")