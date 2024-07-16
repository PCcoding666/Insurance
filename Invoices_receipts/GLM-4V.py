import os
import sys
import logging
from zhipuai import ZhipuAI

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the directory containing the Convert_img2url.py file to the Python path
sys.path.append("/home/ec2-user/Myproject/Insurance/Invoices_receipts")

# Import the upload_blob_and_get_url function
from Convert_img2url import upload_blob_and_get_url

# GLM-4V API call function
def call_glm_api(image_url, prompt, client):
    try:
        response = client.chat.completions.create(
            model="glm-4v",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message
    except Exception as e:
        logging.error(f"An error occurred while calling the API: {e}")
        return None

# Main function to process the dataset
def process_dataset(image_paths, container_name, sas_url, prompt, client):
    for image_path in image_paths:
        image_url = upload_blob_and_get_url(image_path, container_name, sas_url)
        if image_url:
            result = call_glm_api(image_url, prompt, client)
            logging.info(f"Result for {image_path}: {result}")

# Example usage
if __name__ == "__main__":
    # List of local image file paths
    image_paths = [
        "/home/ec2-user/Myproject/Insurance/Data/Sample_Image (9).jpg",
        # "/home/ec2-user/Myproject/Insurance/Data/multi_image_input_test.jpg",
        # Add more image paths as needed
    ]

    # Azure Blob Storage details
    container_name = "convertimg2url"
    sas_url = 'https://convertimg2url.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-08-01T10:41:17Z&st=2024-07-15T02:41:17Z&spr=https&sig=yutHqk7I44AnQU7wIaStABgRyJLEa4vxaqRJC%2BfzpeE%3D'

    # Fixed prompt
    prompt = """Please analyze the content in the image in detail in two steps. Do not miss any steps in this. 
    First step:
    extract the text in the image and return with markdown format, 
    do not ignore any information in the image,
    Second step:
    Extract the key field information from the text and return in json format."""

    # Initialize GLM-4V client
    try:
        client = ZhipuAI(api_key="f1fffd05f347fb8ab934e778ead5a927.67tKXxp4rDTdmrFi")  # Replace with your actual API key
        logging.info(f"Initialized ZhipuAI client ✔")
    except Exception as e:
        logging.error(f"Failed to initialize the client: {e}")
        sys.exit(1)

    # Process the dataset
    process_dataset(image_paths, container_name, sas_url, prompt, client)
