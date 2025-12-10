import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocessing import ImagePreprocessing
from src.ocr import OCREngine
from src.text_cleaning import TextCleaner
from src.pii_detection import PIIDetector
from src.image_redaction import ImageRedactor


class OCRPIIPipeline:
    def __init__(self, ocr_method="tesseract", gemini_api_key=None):
        """
        Initialize the pipeline with configurable OCR method
        
        Args:
            ocr_method: "tesseract" or "gemini"
            gemini_api_key: Google Gemini API key (required if using gemini method)
        """
        self.preprocessor = ImagePreprocessing()
        self.ocr = OCREngine(ocr_method=ocr_method, gemini_api_key=gemini_api_key)
        self.cleaner = TextCleaner()
        self.pii_detector = PIIDetector()
        self.redactor = ImageRedactor()
        self.ocr_method = ocr_method
    
    def process(self, image_path, output_dir="output"):
        results = {}
        results['ocr_method'] = self.ocr_method
        try:
            ### preprocess image
            preprocessed = self.preprocessor.preprocess_image(image_path)
            results['preprocessed_image'] = preprocessed
            ### text extraction
            raw_text = self.ocr.extract_text(preprocessed)
            results['raw_text'] = raw_text
            ## text cleaning
            cleaned_text = self.cleaner.cleanText(raw_text)
            results['cleaned_text'] = cleaned_text
            ## PII detection
            pii_entities = self.pii_detector.extract_pii_entities(cleaned_text)
            results['pii_entities'] = pii_entities
            ## generate redacted text
            redacted_text = self.pii_detector.redact_text(cleaned_text)
            results['redacted_text'] = redacted_text
            
            # Redact image
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                redacted_image_path = os.path.join(output_dir, f"{base_name}_redacted.jpg")
                
                try:
                    redacted_img = self.redactor.redact_image(image_path, redacted_image_path)
                    results['redacted_image_path'] = redacted_image_path
                except Exception as e:
                    results['redaction_error'] = str(e)
            
        except Exception as e:
            results['processing_error'] = str(e)
            raise
        
        return results