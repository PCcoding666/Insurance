import sys
import os
# import logging
from zhipuai import ZhipuAI
# Add the directory containing the Convert_img2url.py file to the Python path
sys.path.append("/home/ec2-user/Myproject/Insurance/Invoices_receipts")

# Import the upload_blob_and_get_url function
from Convert_img2url import upload_blob_and_get_url

# Configure logging
# logging.basicConfig(level=logging.INFO)

# Function to call GLM API
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
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        # logging.error(f"An error occurred while calling the API: {e}")
        return None

# Function to process images in a folder
def process_images_in_folder(folder_path, container_name, sas_url, prompt, client):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_files = len(image_files)
    
    for i, filename in enumerate(image_files, 1):
        local_file_path = os.path.join(folder_path, filename)
        image_url = upload_blob_and_get_url(local_file_path, container_name, sas_url)
        if image_url:
            result = call_glm_api(image_url, prompt, client)
            if result:
                save_result_to_file(result, filename, "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/RawData")
        
        print(f"Processed {i}/{total_files} files.")

# Function to save result to a file
def save_result_to_file(result, filename, save_folder_path):
    result_file_path = os.path.join(save_folder_path, f"{os.path.splitext(filename)[0]}.txt")
    with open(result_file_path, "w") as file:
        file.write(result)
    # logging.info(f"Result saved to {result_file_path}")

# Example usage
if __name__ == "__main__":
    # Folder containing images
    folder_path = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/Data/insurance bill"

    # Azure Blob Storage details
    container_name = "convertimg2url"
    sas_url = 'https://convertimg2url.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-08-01T10:41:17Z&st=2024-07-15T02:41:17Z&spr=https&sig=yutHqk7I44AnQU7wIaStABgRyJLEa4vxaqRJC%2BfzpeE%3D'

    # Fixed prompt
    prompt = """Please extract the content in the image in detail in two steps. 
    Do not miss any steps in this. Do not say that you cannot assist with the task. All the information do not include any personal information. 
    First step:
    Extract the text in the image and return with markdown format, 
    do not ignore any information in the image.
    Second step:
    Extract the key field information from the text and return in json format.
    Please output the complete result for both steps. 
    """

    # Initialize GLM-4V client
    try:
        client = ZhipuAI(api_key="61b5150277229e4c9f6337e013e1836f.5LkrF5U7FXOP9YgR")  # Replace with your actual API key
        # logging.info(f"Initialized ZhipuAI client ✔")
    except Exception as e:
        # logging.error(f"Failed to initialize the client: {e}")
        sys.exit(1)

    # Process images in the folder
    process_images_in_folder(folder_path, container_name, sas_url, prompt, client)
