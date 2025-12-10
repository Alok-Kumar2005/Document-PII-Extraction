import cv2
import numpy as np
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image

class ImageRedactor:
    def __init__(self):
        self.engine = ImageRedactorEngine()
    
    def redact_image(self, image_path, output_path=None):
        img = Image.open(image_path)
        redacted_img = self.engine.redact(img, fill="black")
        
        if output_path:
            redacted_img.save(output_path)
        
        return redacted_img
    
    def redact_with_boxes(self, image_path, pii_entities, output_path=None):
        img = cv2.imread(image_path)
        for entity in pii_entities:
            pass
        
        if output_path:
            cv2.imwrite(output_path, img)
        
        return img