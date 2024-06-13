# utils.py

import base64
import io
import re
import os
import json
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
import logging

def encode_image_to_base64(image_bytes):
    """
    Encode image bytes to a base64 string.
    
    :param image_bytes: The image file bytes.
    :return: Base64 encoded string of the image.
    """
    buffered = resize_image(image_bytes)
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return base64_image

def resize_image(image_bytes, max_size=(4096, 4096)):
    """
    Resize the image to the specified maximum size.

    :param image_bytes: The image file bytes.
    :param max_size: The maximum dimensions for resizing.
    :return: Resized image in bytes.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    enhanced_img = image_enhancement(img)

    pil_img = Image.fromarray(enhanced_img)
    pil_img.thumbnail(max_size, Image.LANCZOS)

    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    return buffered

def image_enhancement(img):
    """
    Enhance the image using grayscale conversion, Gaussian blur, and adaptive thresholding.

    :param img: The input image.
    :return: Enhanced image.
    """
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    thresh_image = cv2.adaptiveThreshold(denoised_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4)
    return thresh_image

def pdf_to_images(pdf_path, output_folder, dpi=300):
    """
    Convert each page of a PDF to an image.

    :param pdf_path: Path to the PDF file.
    :param output_folder: Folder to save the output images.
    :param dpi: Dots per inch for image resolution.
    :return: List of paths to the saved images.
    """
    pdf_document = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
        logging.info(f'Saved {image_path}')
    pdf_document.close()
    return image_paths

def clean_response(response):
    """
    Clean the response by extracting JSON content within curly braces.

    :param response: The raw response string.
    :return: Extracted and cleaned JSON content.
    """
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        extracted_content = match.group(0)
        cleaned_content = extracted_content.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            return cleaned_content
    else:
        return response

