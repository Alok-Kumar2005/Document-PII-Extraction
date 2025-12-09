import pytesseract
from PIL import Image
import cv2
import numpy as np


class OCREngine:
    def __init__(self, tesseract_cmd=None):
        """
        Initialize the OCR engine with optional Tesseract command path.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    def extract_text(self, image):
        if isinstance(image, str):
            pil_image = Image.open(image)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
        config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_image, config = config)
        return text
    
    def extract_with_boxes(self, image):
        if isinstance(image, str):
            pil_image = Image.open(image)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
        
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
        return data
    

if __name__ == "__main__":
    ocr_engine = OCREngine()
    sample_image_path = "images/preprocessed_14.jpg"
    text = ocr_engine.extract_text(sample_image_path)
    print("Extracted Text:")
    print(text)
    print("=" * 100)
    data = ocr_engine.extract_with_boxes(sample_image_path)
    print("OCR Data with Bounding Boxes:")
    print(data)