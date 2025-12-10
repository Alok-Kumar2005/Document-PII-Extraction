import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocessing import ImagePreprocessing
from src.ocr import OCREngine
from src.text_cleaning import TextCleaner
from src.pii_detection import PIIDetector
from src.image_redaction import ImageRedactor


class OCRPIIPipeline:
    def __init__(self):
        self.preprocessor = ImagePreprocessing()
        self.ocr = OCREngine()
        self.cleaner = TextCleaner()
        self.pii_detector = PIIDetector()
        self.redactor = ImageRedactor()
    
    def process(self, image_path, output_dir="output"):
        results = {}
        ### preprocesss images
        preprocessed = self.preprocessor.preprocess_image(image_path)
        results['preprocessed_image'] = preprocessed
        ### extract text
        raw_text = self.ocr.extract_text(preprocessed)
        results['raw_text'] = raw_text
        ### clean text
        cleaned_text = self.cleaner.cleanText(raw_text)
        results['cleaned_text'] = cleaned_text
        ### detect PII
        pii_entities = self.pii_detector.extract_pii_entities(cleaned_text)
        results['pii_entities'] = pii_entities
        ## generated reducted text
        redacted_text = self.pii_detector.redact_text(cleaned_text)
        results['redacted_text'] = redacted_text
        ## redact image
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            redacted_image_path = os.path.join(output_dir, f"{base_name}_redacted.jpg")
            
            try:
                redacted_img = self.redactor.redact_image(image_path, redacted_image_path)
                results['redacted_image_path'] = redacted_image_path
            except Exception as e:
                results['redaction_error'] = str(e)
        
        return results