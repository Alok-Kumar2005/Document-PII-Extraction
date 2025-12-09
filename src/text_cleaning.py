import re
from ocr import OCREngine

class TextCleaner:
    @staticmethod
    def removeWhitespaces(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def removeSpecialCharacters(text: str) -> str:
        return re.sub(r'[^A-Za-z0-9\s]', '', text)
    
    @staticmethod
    def toLowerCase(text: str) -> str:
        return text.lower()
    
    @staticmethod
    def cleanText(text: str) -> str:
        text = TextCleaner.removeWhitespaces(text)
        text = TextCleaner.removeSpecialCharacters(text)
        text = TextCleaner.toLowerCase(text)
        return text
    

if __name__ == "__main__":
    ocr = OCREngine()
    sample_image_path = "images/preprocessed_14.jpg"
    extracted_text = ocr.extract_text(sample_image_path)
    print("Original Extracted Text:")
    print(extracted_text)
    cleaned_text = TextCleaner.cleanText(extracted_text)
    print("\nCleaned Text:")
    print(cleaned_text)
    print("=" * 100)
    data = ocr.extract_with_boxes(sample_image_path)
    print("OCR Data with Bounding Boxes:")
    print(data)
    print("=" * 100)

