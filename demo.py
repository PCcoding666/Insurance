import openai
import requests
import base64
import json
from PIL import Image 
import os
import logging
from datetime import datetime
import gradio as gr
import fitz  # PyMuPDF

# Set up logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Your OpenAI API key
api_key = 'sk-proj-5c5PuieVb45JrUQN3FVhT3BlbkFJJJFnKGadNLdWO75xhusD'
openai.api_key = api_key

# Function to resize the image
def resize_image(image_path, max_size=(1024, 1024)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.LANCZOS)
        resized_image_path = os.path.join('resized', os.path.basename(image_path))
        os.makedirs(os.path.dirname(resized_image_path), exist_ok=True)
        img.save(resized_image_path)
    return resized_image_path

# Function to encode the image to base64
def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_image

# Function to call the GPT-4 Vision API and get structured data from the image
def get_structured_data_from_image(image_path, prompt):
    # Resize the image to reduce the size
    resized_image_path = resize_image(image_path)

    # Encode the resized image to base64
    base64_image = encode_image_to_base64(resized_image_path)

    # Define the message for the GPT-4 Vision API
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    }

    # URL for the GPT-4 Vision API
    url = 'https://api.openai.com/v1/chat/completions'

    # Define the headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Define the payload
    payload = {
        "model": "gpt-4o",
        "messages": [message],
        "temperature": 0.3
    }

    # Send the request to the API
    start_time = datetime.now()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = datetime.now()

    # Calculate the duration of the request
    duration = end_time - start_time

    # Calculate tokens used
    response_data = response.json()
    input_tokens = response_data.get('usage', {}).get('prompt_tokens', 0)
    output_tokens = response_data.get('usage', {}).get('completion_tokens', 0)

    # Log the request duration
    logging.info(f"Request for {image_path} took {duration.total_seconds()} seconds.")

    # Check if the request was successful
    if response.status_code == 200:
        structured_data = response_data['choices'][0]['message']['content']
        # Log the response
        logging.info(f"Response for {image_path}: {structured_data}")
        return structured_data, duration.total_seconds(), input_tokens, output_tokens
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None, 0, 0, 0

# Function to generate prompt for the second API call
def generate_prompt(report):
    prompt = (
        "The following is the JSON data of a health check report. Please review and identify any abnormalities.\n"
        "1. Check the health indicators, and if there are abnormalities, please indicate which indicators are abnormal and explain the reasons.\n"
        "2. Display some attribute information contained in the report, such as date, total amount, location, etc.\n"
        "If no relevant information is found, please return 'No relevant information found'.\n"
        f"Health check report JSON data:\n{report}\n"
        "Your output should include two aspects, displayed with two headings: '1. Abnormal conditions of health indicators; 2. Insurance information disclosure'\n"
        "For heading 1, if there are health-related abnormalities, please return the abnormal values and their explanations, formatted as: {'item_name': 'Indicator Name', 'result': 'Test Result', 'reference_range': 'Reference Range', 'remark': 'Remark', 'explanation': 'Explanation'}.\n"
        'If there are comprehensive diagnostic suggestions, print the diagnostic suggestions directly.\n'
        "If it does not fall into the above two situations, please return: 'No abnormalities found'.\n"
        "For heading 2, please display all information that may relate to insurance claims, including the time, place, invoice details, and expenses covered in the report, etc. Use JSON format to display, and if there is no relevant information, output N.A.\n"
        "Do not use omissions expression"
    )
    return prompt

# Function to call GPT-4 API and analyze the report
def analyze_report(report):
    prompt = generate_prompt(report)
    message = {"role": "user", "content": prompt}

    # URL for the GPT-4 API
    url = 'https://api.openai.com/v1/chat/completions'

    # Define the headers
    headers = {
        'Authorization': f'Bearer {openai.api_key}',
        'Content-Type': 'application/json'
    }

    # Define the payload
    payload = {
        "model": "gpt-4o",
        "messages": [message],
        # "max_tokens": 8192,  # Reduce max tokens
        "temperature": 0.3
    }

    # Send the request to the API
    start_time = datetime.now()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = datetime.now()

    # Calculate the duration of the request
    duration = end_time - start_time

    # Calculate tokens used
    response_data = response.json()
    input_tokens = response_data.get('usage', {}).get('prompt_tokens', 0)
    output_tokens = response_data.get('usage', {}).get('completion_tokens', 0)

    # Log the request duration
    logging.info(f"Request for analyzing report took {duration.total_seconds()} seconds.")

    # Check if the request was successful
    if response.status_code == 200:
        structured_data = response_data['choices'][0]['message']['content']
        # Log the response
        logging.info(f"Response for analyzing report: {structured_data}")
        return structured_data, duration.total_seconds(), input_tokens, output_tokens
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None, 0, 0, 0

# Function to clean the API response
def clean_response(response):
    return response.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')

# Function to process multiple images and merge results into one meta data
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

# Function to convert PDF pages to high-resolution images
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

# Gradio Interface Function
def process_file(files):
    custom_prompt = """
            Please extract the results in this image and turn them into structured data in JSON format. 
            Pay special attention to horizontal alignment when extracting text, there may have some skip part in one row of datalike '参考区间'. 
            When processing data in a table, grab the data row by row. 
            For content where some information in the image is blocked or unclear, use Not Visible as the output. Output content don't need to translate, keep it original. 
            Your output does not need to contain any additional information
            """

    results = {}
    total_duration = 0
    total_input_tokens = 0
    total_output_tokens = 0
    for file in files:
        file_path = file.name

        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(file_path, custom_prompt)
            results[file_path] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        elif file_path.lower().endswith('pdf'):
            output_folder = 'extracted_images'
            os.makedirs(output_folder, exist_ok=True)
            image_paths = pdf_to_images(file_path, output_folder, dpi=300)
            structured_data, duration, input_tokens, output_tokens = process_images_and_merge(image_paths, custom_prompt)
            results[file_path] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        else:
            results[file_path] = {"error": "Unsupported file type"}

    # Generate JSON with indent and ensure new lines are preserved
    json_results = json.dumps(results, ensure_ascii=False, indent=2)
    json_results = json_results.replace('\\n', '\n')  # Ensure new lines are preserved

    return json_results, total_duration, total_input_tokens, total_output_tokens

# Gradio Interface
def get_metadata(files):
    results, duration, input_tokens, output_tokens = process_file(files)
    return results, duration, input_tokens, output_tokens

def run_analysis(metadata):
    logging.info(f"Metadata: {metadata}")

    metadata = metadata.strip().strip('```json').strip('```')

    analysis_result, duration, input_tokens, output_tokens = analyze_report(metadata)
    return analysis_result, duration, input_tokens, output_tokens

with gr.Blocks() as demo:
    with gr.Column():
        file_input = gr.File(label="Upload Image(s) or PDF", type="file", file_count="multiple")
        metadata_output = gr.Textbox(label="Metadata", lines=10)
        with gr.Row():
            processing_time_output_1 = gr.Textbox(label="Processing Time 1", lines=1)
            input_tokens_output_1 = gr.Textbox(label="Input Tokens 1", lines=1)
            output_tokens_output_1 = gr.Textbox(label="Output Tokens 1", lines=1)
        risk_button = gr.Button("Risk Assessment")
        risk_output = gr.Textbox(label="Risk Assessment Report", lines=10)
        with gr.Row():
            processing_time_output_2 = gr.Textbox(label="Processing Time 2", lines=1)
            input_tokens_output_2 = gr.Textbox(label="Input Tokens 2", lines=1)
            output_tokens_output_2 = gr.Textbox(label="Output Tokens 2", lines=1)

    file_input.upload(fn=get_metadata, inputs=file_input, outputs=[metadata_output, processing_time_output_1, input_tokens_output_1, output_tokens_output_1])
    risk_button.click(fn=run_analysis, inputs=metadata_output, outputs=[risk_output, processing_time_output_2, input_tokens_output_2, output_tokens_output_2])

demo.launch(share=True)
