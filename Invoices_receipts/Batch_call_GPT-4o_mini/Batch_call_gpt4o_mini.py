import base64
import requests
import json
import logging
from datetime import datetime
import os

api_key = 'sk-proj-PvSwVKlrovGHfKfGXsHRT3BlbkFJEfDwnjQHH4wsZvsP9sk4'


def encode_image_to_base64(image_path):
    """
    Encode image file to a base64 string.

    :param image_path: The path to the image file.
    :return: Base64 encoded string of the image.
    """
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return base64_image

def save_response_to_file(response_data, image_path, output_folder):
    """
    Save the API response to a text file.

    :param response_data: The response data from the API.
    :param image_path: Path to the image file.
    :param output_folder: Folder to save the text file.
    """
    base_name = os.path.basename(image_path)
    file_name = os.path.splitext(base_name)[0] + ".txt"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, file_name)
    
    with open(output_path, 'w') as file:
        file.write(response_data)

def save_durations_to_file(durations, output_folder):
    """
    Save the durations of API requests to a text file.

    :param durations: List of durations.
    :param output_folder: Folder to save the durations file.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "durations.txt")
    
    with open(output_path, 'w') as file:
        for duration in durations:
            file.write(f"{duration}\n")

def get_structured_data_from_image(image_path, prompt, model, output_folder, durations):
    """
    Get structured data from an image using the specified model.

    :param image_path: Path to the image file.
    :param prompt: The prompt to be used for the API call.
    :param model: The model to be used ('gpt-4o' or 'qwen-vl-max').
    :param output_folder: Folder to save the response text file.
    :param durations: List to store durations of API calls.
    :return: The structured data from the API call.
    """
    print(f"Encoding image {image_path} to base64...")
    base64_image = encode_image_to_base64(image_path)
    print(f"Calling GPT-4o API for image {image_path}...")
    if model == 'gpt-4o-mini-2024-07-18':
        return call_gpt_4o(base64_image, prompt, image_path, output_folder, durations)

def call_gpt_4o(base64_image, prompt, image_path, output_folder, durations):
    """
    Call the GPT-4o API with the specified parameters.

    :param base64_image: Base64 encoded image.
    :param prompt: The prompt for the API.
    :param image_path: Path to the original image file.
    :param output_folder: Folder to save the response text file.
    :param durations: List to store durations of API calls.
    :return: The structured data from the API call.
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
        "model": "gpt-4o-mini-2024-07-18",
        "messages": [message],
        "max_tokens": 4096,
        "temperature": 0
    }

    start_time = datetime.now()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    durations.append(duration)

    response_data = response.json()

    if response.status_code == 200:
        structured_data = response_data['choices'][0]['message']['content']
        logging.info(f"Response for {image_path}: {structured_data}")
        print(f"Success: Received response for image {image_path} in {duration} seconds")
        save_response_to_file(structured_data, image_path, output_folder)
        return structured_data
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        print(f"Error: {response.status_code} for image {image_path}")
        save_response_to_file(response.text, image_path, output_folder)
        return None

# 示例调用
image_folder = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GPT-4o_mini/Data'
output_folder = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GPT-4o_mini/RawData'
prompt = '''Please extract the content in detail from the provided image of a receipt or invoice. 
Do not miss any information in the image. The extracted content should be formatted and returned in the following two JSON objects. Only these two JSON objects should be returned, without any additional text or explanation. If any information is missing, return `null` for that key.

The first JSON object should contain the following keys:
- CustomerName: The name of the customer.
- VendorName: The name of the vendor.
- CustomerAddress: The address of the customer.
- VendorAddress: The address of the vendor.
- InvoiceDate: The date of the invoice.
- TotalTax: The total tax amount.
- InvoiceTotal: The total amount of the invoice.
- AmountDue: The amount due.

The second JSON object should be an array of items, each containing the following keys:
- Description: The description of each item or service.
- Quantity: The quantity of each item.
- Unit: The unit of measurement for each item.
- UnitPrice: The unit price of each item.
- ProductCode: The product code of each item.
- Date: The date associated with each item.
- Tax: The tax amount for each item.
- Amount: The amount for each item.

Please provide the resulting JSON output only, with no additional explanatory text.
'''
model = 'gpt-4o-mini-2024-07-18'

durations = []

# 获取文件夹中的所有图片
for image_file in os.listdir(image_folder):
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(image_folder, image_file)
        print(f"Processing image {image_path}...")
        get_structured_data_from_image(image_path, prompt, model, output_folder, durations)

# 保存所有请求时长到一个txt文件中
save_durations_to_file(durations, output_folder)