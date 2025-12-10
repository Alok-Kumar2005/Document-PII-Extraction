import pytesseract
from PIL import Image
import cv2
import numpy as np
import base64
from io import BytesIO
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class OCREngine:
    def __init__(self, tesseract_cmd=None, ocr_method="tesseract", gemini_api_key=None):
        self.ocr_method = ocr_method
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        if ocr_method == "gemini":
            if not gemini_api_key:
                gemini_api_key = os.getenv("GOOGLE_API_KEY")
            if not gemini_api_key:
                raise ValueError("Gemini API key is required for LLM-based OCR")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=gemini_api_key,
                temperature=0
            )
    
    def _image_to_base64(self, image):
        """Convert image to base64 string"""
        if isinstance(image, str):
            pil_image = Image.open(image)
        elif isinstance(image, np.ndarray):
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
        else:
            pil_image = image
        
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def extract_text_with_gemini(self, image):
        """Extract text using Gemini Vision API via LangChain"""
        try:
            ### iamage to base64
            img_base64 = self._image_to_base64(image)
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": """Extract all text from this image accurately. 
                        Pay special attention to:
                        - Handwritten text
                        - Names, dates, phone numbers, email addresses
                        - Medical information
                        - Any personal identifiable information (PII)
                        
                        Return ONLY the extracted text, preserving the original formatting and layout as much as possible.
                        Do not add any explanations or comments."""
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{img_base64}"
                    }
                ]
            )
            response = self.llm.invoke([message])
            return response.content
            
        except Exception as e:
            print(f"Error in Gemini OCR: {str(e)}")
            raise
    
    def extract_text_with_tesseract(self, image):
        """Extract text using Tesseract OCR"""
        if isinstance(image, str):
            pil_image = Image.open(image)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
        
        config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_image, config=config)
        return text
    
    def extract_text(self, image):
        if self.ocr_method == "gemini":
            return self.extract_text_with_gemini(image)
        else:
            return self.extract_text_with_tesseract(image)
    
    def extract_with_boxes(self, image):
        if self.ocr_method != "tesseract":
            raise NotImplementedError("Bounding box extraction is only available with Tesseract OCR")
        
        if isinstance(image, str):
            pil_image = Image.open(image)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
        
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
        return data


if __name__ == "__main__":
    print("Testing Tesseract OCR...")
    ocr_tesseract = OCREngine(ocr_method="tesseract")
    sample_image_path = "images/preprocessed_14.jpg"
    text_tesseract = ocr_tesseract.extract_text(sample_image_path)
    print("Tesseract Extracted Text:")
    print(text_tesseract)
    print("=" * 100)
    
    try:
        print("\nTesting Gemini OCR...")
        ocr_gemini = OCREngine(ocr_method="gemini", gemini_api_key="YOUR_API_KEY")
        text_gemini = ocr_gemini.extract_text(sample_image_path)
        print("Gemini Extracted Text:")
        print(text_gemini)
    except Exception as e:
        print(f"Gemini OCR not available: {str(e)}")