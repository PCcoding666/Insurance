# api_calls.py

import requests
import json
import logging
from datetime import datetime
from config import api_key, qwen_api_key
from utils import encode_image_to_base64

def get_structured_data_from_image(image_path, prompt, model):
    """
    Get structured data from an image using the specified model.

    :param image_path: Path to the image file.
    :param prompt: The prompt to be used for the API call.
    :param model: The model to be used ('gpt-4o' or 'qwen-vl-max').
    :return: The structured data, duration of the API call, input tokens, and output tokens.
    """
    base64_image = encode_image_to_base64(image_path)
    if model == 'gpt-4o':
        return call_gpt_4o(base64_image, prompt, image_path)
    elif model == 'qwen-vl-max':
        return call_qwen_vl_max(image_path, prompt, qwen_api_key)
    else:
        raise ValueError(f"Unsupported model: {model}")

def call_gpt_4o(base64_image, prompt, image_path):
    """
    Call the GPT-4o API with the specified parameters.

    :param base64_image: Base64 encoded image.
    :param prompt: The prompt for the API.
    :param image_path: Path to the original image file.
    :return: The structured data, duration of the API call, input tokens, and output tokens.
    """
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    }
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-4o",
        "messages": [message],
        "max_tokens": 4096,
        "temperature": 0
    }
    start_time = datetime.now()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = datetime.now()
    duration = end_time - start_time
    response_data = response.json()
    input_tokens = response_data.get('usage', {}).get('prompt_tokens', 0)
    output_tokens = response_data.get('usage', {}).get('completion_tokens', 0)
    logging.info(f"Request for {image_path} took {duration.total_seconds()} seconds.")
    if response.status_code == 200:
        structured_data = response_data['choices'][0]['message']['content']
        logging.info(f"Response for {image_path}: {structured_data}")
        return structured_data, duration.total_seconds(), input_tokens, output_tokens
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None, 0, 0, 0

def call_qwen_vl_max(image_path, prompt, qwen_api_key):
    """
    Call the Qwen-vl-max API with the specified parameters.

    :param image_path: Path to the image file.
    :param prompt: The prompt for the API.
    :param qwen_api_key: API key for Qwen-vl-max.
    :return: The structured data, duration of the API call.
    """
    local_file_path = f"file://{os.path.abspath(image_path)}"
    messages = [{
        'role': 'user',
        'content': [
            {
                'image': local_file_path
            },
            {
                'text': prompt
            },
        ]
    }]
    start_time = datetime.now()
    response = MultiModalConversation.call(
        model='qwen-vl-max',
        messages=messages,
        api_key=qwen_api_key
    )
    end_time = datetime.now()
    duration = end_time - start_time
    if response.status_code == 200:
        structured_data = response.output
        logging.info(f"Response for {image_path}: {structured_data}")
        return structured_data, duration.total_seconds(), 0, 0
    else:
        logging.error(f"Error: {response.code}")
        logging.error(response.message)
        return None, 0, 0, 0