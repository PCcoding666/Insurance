from PIL import Image
import base64
import io
import cv2
import numpy as np

def image_enhancement(img):
    # Convert to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur for noise reduction
    denoised_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply adaptive thresholding
    thresh_image = cv2.adaptiveThreshold(denoised_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4)

    return thresh_image

def resize_image(image_bytes, max_size=(4096, 4096)):
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    enhanced_img = image_enhancement(img)

    # Convert to PIL image for further processing
    pil_img = Image.fromarray(enhanced_img)
    pil_img.thumbnail(max_size, Image.LANCZOS)
    
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    return buffered

def encode_image_to_base64(image_bytes):
    buffered = resize_image(image_bytes)
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return base64_image
