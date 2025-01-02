from celery import shared_task
import os
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@shared_task(bind=True)
def process_image(self, image_path):
    try:
        # Debugging: Print the image path
        print(f"Image path: {image_path}")

        # Check if the file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"The image file at {image_path} does not exist.")

        # Open the image file
        img = Image.open(image_path)
        raw_text = pytesseract.image_to_string(img)
        
        # Debugging: Print the raw OCR output
        print(f"Raw OCR output: {raw_text}")

        # Split the raw text into lines and number them
        items = raw_text.splitlines()
        numbered_result = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items) if item.strip()])
        
        # Debugging: Print the formatted OCR output
        print(f"Formatted OCR output: {numbered_result}")

        return numbered_result
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        raise e