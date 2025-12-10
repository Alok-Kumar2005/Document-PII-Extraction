import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import re
import spacy
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from src.ocr import OCREngine

class PIIDetector:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_lg"])
            self.nlp = spacy.load("en_core_web_lg")
        
        self.analyzer = AnalyzerEngine()
        self._add_custom_recognizers()
    
    def _add_custom_recognizers(self):
        phone_pattern = Pattern(
            name="indian_phone",
            regex=r"\b[6-9]\d{9}\b",
            score=0.85
        )
        
        phone_recognizer = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[phone_pattern]
        )
        
        self.analyzer.registry.add_recognizer(phone_recognizer)
    
    def detect(self, text):
        results = self.analyzer.analyze(
            text=text,
            language='en',
            entities=[
                "PERSON",
                "EMAIL_ADDRESS", 
                "PHONE_NUMBER",
                "MEDICAL_LICENSE",
                "DATE_TIME",
                "LOCATION",
                "IBAN_CODE",
                "CREDIT_CARD",
                "US_SSN",
                "US_PASSPORT"
            ]
        )
        
        return results
    
    def extract_pii_entities(self, text):
        results = self.detect(text)
        
        entities = []
        for result in results:
            entity = {
                'type': result.entity_type,
                'text': text[result.start:result.end],
                'start': result.start,
                'end': result.end,
                'score': result.score
            }
            entities.append(entity)
        
        return entities
    
    def redact_text(self, text):
        """Redact PII from text"""
        results = self.detect(text)
        results = sorted(results, key=lambda x: x.start, reverse=True)
        
        redacted_text = text
        for result in results:
            redacted_text = (
                redacted_text[:result.start] + 
                f"[{result.entity_type}]" + 
                redacted_text[result.end:]
            )
        
        return redacted_text
    

if __name__ == "__main__":
    ocr = OCREngine()
    sample_image_path = "images/preprocessed_14.jpg"
    extracted_text = ocr.extract_text(sample_image_path)
    print("Extracted Text:")
    print(extracted_text)
    print("=" * 100)
    
    pii_detector = PIIDetector()
    entities = pii_detector.extract_pii_entities(extracted_text)
    print("Detected PII Entities:")
    for entity in entities:
        print(entity)
    
    redacted_text = pii_detector.redact_text(extracted_text)
    print("\nRedacted Text:")
    print(redacted_text)