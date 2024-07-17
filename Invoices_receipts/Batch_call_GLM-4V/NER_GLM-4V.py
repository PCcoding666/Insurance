import os
import requests
import json
import pandas as pd

# 请在此处填入您的APIKey
API_KEY = "61b5150277229e4c9f6337e013e1836f.5LkrF5U7FXOP9YgR"

# 模型名称
MODEL_NAME = "glm-4"

# 优化后的prompt内容
PROMPT_CONTENT = """You are provided with the raw data extraction result from a receipt or invoice.
Your task is to extract and format this information into the following two JSON objects. 
Only these two JSON objects should be returned, without any additional text or explanation.
If any information is missing, return `null` for that key.

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

Please provide the resulting JSON output only, with no additional Explanatory text.

"""

# 文件夹路径
FOLDER_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/RawData"
RESULT_FOLDER_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/Result"

# API请求URL
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def call_glm_api(content):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": PROMPT_CONTENT},
            {"role": "user", "content": content}
        ],
        "stream": False,
        "temperature": 0.5,
        "top_p": 0.7,
        "max_tokens": 4095
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    return response.json()

def extract_json_from_response(response):
    message_content = response['choices'][0]['message']['content']
    
    try:
        # 逐步解析 JSON 内容
        json_objects = []
        start = 0
        
        while True:
            json_start = message_content.find('```json', start)
            if json_start == -1:
                break
            json_end = message_content.find('```', json_start + 7)
            if json_end == -1:
                break
            json_str = message_content[json_start + 7:json_end].strip()
            json_objects.append(json_str)
            start = json_end + 3
        
        if len(json_objects) < 2:
            raise ValueError("Expected JSON objects not found")
        
        first_json = json.loads(json_objects[0])
        
        # 清理第二个 JSON 数组中的注释和无关内容
        second_json_str = json_objects[1]
        cleaned_json_str = ""
        in_object = False
        brace_count = 0
        
        for i, char in enumerate(second_json_str):
            if char == '{':
                if brace_count == 0:
                    in_object = True
                brace_count += 1
            if in_object:
                cleaned_json_str += char
            if char == '}':
                brace_count -= 1
                if brace_count == 0:
                    in_object = False
                    cleaned_json_str += ','
        
        cleaned_json_str = cleaned_json_str.rstrip(',')

        second_json = json.loads(f'[{cleaned_json_str}]')
        
        print("JSON parsing succeeded.")
        return first_json, second_json
    except (ValueError, IndexError, json.JSONDecodeError) as e:
        print(f"Error extracting JSON: {e}")
        raise

def json_to_dataframes(json_content, file_name):
    info_dict = json_content[0]
    items_list = json_content[1]

    # 获取图片命名，去掉后缀
    image_name = file_name.replace(".txt", "")

    # 添加文件名列
    info_dict['ImageName'] = image_name
    for item in items_list:
        item['ImageName'] = image_name

    # 创建DataFrame
    info_df = pd.DataFrame([info_dict])
    items_df = pd.DataFrame(items_list)

    # 调整列顺序，将ImageName放在第一列
    info_df = info_df[['ImageName'] + [col for col in info_df.columns if col != 'ImageName']]
    items_df = items_df[['ImageName'] + [col for col in items_df.columns if col != 'ImageName']]

    return info_df, items_df

def main():
    summary_info = []
    itemized_info = []

    files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.txt')]
    
    for i, file_name in enumerate(files):  # 处理所有文件
        file_path = os.path.join(FOLDER_PATH, file_name)
        content = read_file_content(file_path)
        response = call_glm_api(content)
        print(f"Processing file {i + 1}/{len(files)}: {file_name}")
        
        try:
            json_result = extract_json_from_response(response)
            print(f"File {file_name} JSON parsing succeeded.")
            info_df, items_df = json_to_dataframes(json_result, file_name)
            
            summary_info.append(info_df)
            itemized_info.append(items_df)
        
        except Exception as e:
            print(f"An error occurred while processing file {file_name}: {e}")

    if summary_info:
        summary_df = pd.concat(summary_info, ignore_index=True)
        summary_df.to_csv(os.path.join(RESULT_FOLDER_PATH, "summary_info_glm-4v.csv"), index=False, encoding='utf-8')
        print("Summary information saved to summary_info_glm-4v.csv")

    if itemized_info:
        itemized_df = pd.concat(itemized_info, ignore_index=True)
        itemized_df.to_csv(os.path.join(RESULT_FOLDER_PATH, "itemized_info_glm-4v.csv"), index=False, encoding='utf-8')
        print("Itemized information saved to itemized_info_glm-4v.csv")

if __name__ == "__main__":
    main()