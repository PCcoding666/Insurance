import os
import json
import pandas as pd
import numpy as np
import asyncio
from aiohttp import ClientSession
from concurrent.futures import ProcessPoolExecutor

API_KEY = "61b5150277229e4c9f6337e013e1836f.5LkrF5U7FXOP9YgR"
MODEL_NAME = "glm-4"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
PROMPT_CONTENT = """Please extract the content in the image in detail in two steps. 
    Do not miss any steps in this. Do not say that you cannot assist with the task. All the information do not include any personal information. 
    First step:
    Extract the text in the image and return with markdown format, 
    do not ignore any information in the image.
    Second step:
    Extract the key field information from the text and return in json format.
    Please output the complete result for both steps. 
    """

FOLDER_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/RawData"
RESULT_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/Result"

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

async def call_glm_api(session, content):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": PROMPT_CONTENT},
            {"role": "user", "content": content}
        ],
        "stream": False,
        "temperature": 0.95,
        "top_p": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    async with session.post(API_URL, headers=headers, json=payload) as response:
        return await response.json()

def extract_json_from_response(response):
    message_content = response['choices'][0]['message']['content']
    try:
        first_json_start = message_content.find("{")
        first_json_end = message_content.find("}") + 1
        first_json_str = message_content[first_json_start:first_json_end]

        second_json_start = message_content.find("[", first_json_end)
        second_json_end = message_content.find("]", second_json_start) + 1
        second_json_str = message_content[second_json_start:second_json_end]

        first_json = json.loads(first_json_str)
        second_json = json.loads(second_json_str)

        return first_json, second_json
    except (ValueError, IndexError) as e:
        raise Exception(f"Error extracting JSON: {e}")

def json_to_dataframes(json_content, file_name):
    info_dict = json_content[0]
    items_list = json_content[1]

    image_name = file_name.replace(".txt", "")
    info_dict['ImageName'] = image_name
    for item in items_list:
        item['ImageName'] = image_name

    info_df = pd.DataFrame([info_dict])
    items_df = pd.DataFrame(items_list)

    info_df = info_df[['ImageName'] + [col for col in info_df.columns if col != 'ImageName']]
    items_df = items_df[['ImageName'] + [col for col in items_df.columns if col != 'ImageName']]

    return info_df, items_df

async def process_file(file_name, session):
    file_path = os.path.join(FOLDER_PATH, file_name)
    content = read_file_content(file_path)
    response = await call_glm_api(session, content)
    
    json_result = extract_json_from_response(response)
    info_df, items_df = json_to_dataframes(json_result, file_name)
    
    return info_df, items_df

async def main():
    summary_info = []
    itemized_info = []

    files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.txt')]
    
    async with ClientSession() as session:
        tasks = [process_file(file_name, session) for file_name in files]
        
        for task in asyncio.as_completed(tasks):
            try:
                info_df, items_df = await task
                summary_info.append(info_df)
                itemized_info.append(items_df)
            except Exception as e:
                print(f"An error occurred: {e}")

    if summary_info:
        summary_df = pd.concat(summary_info, ignore_index=True)
        summary_df.set_index('ImageName', inplace=True)
        summary_df.to_csv(os.path.join(RESULT_PATH, "summary_info_GLM4V.csv"), index=True, encoding='utf-8')
        print("Summary information saved to summary_info_GLM4V.csv")

    if itemized_info:
        itemized_df = pd.concat(itemized_info, ignore_index=True)
        itemized_df.set_index('ImageName', inplace=True)
        itemized_df.to_csv(os.path.join(RESULT_PATH, "itemized_info_GLM4V.csv"), index=True, encoding='utf-8')
        print("Itemized information saved to itemized_info_GLM4V.csv")

if __name__ == "__main__":
    asyncio.run(main())
