# batch_processing.py
import os
import logging
from api_calls import get_structured_data_from_image
from data_cleaning import clean_response

def process_images_and_merge(image_paths, prompt):
    all_results = {}
    total_duration = 0
    total_input_tokens = 0
    total_output_tokens = 0
    for image_path in image_paths:
        logging.info(f"Processing {image_path}...")
        structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(image_path, prompt)
        if structured_data:
            cleaned_data = clean_response(structured_data)
            all_results[os.path.basename(image_path)] = cleaned_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
    return all_results, total_duration, total_input_tokens, total_output_tokens
