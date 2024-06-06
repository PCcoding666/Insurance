# pdf_to_images.py
import os
import fitz  # PyMuPDF
import logging

def pdf_to_images(pdf_path, output_folder, dpi=300):
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
