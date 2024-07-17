import os
import json
import pandas as pd
import re

# 文件夹路径
ERROR_FOLDER_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/Error"
RESULT_FOLDER_PATH = "/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GLM-4V/Result"

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_json_objects(content):
    content = re.sub(r'//.*?\n', '', content)  # 去除注释
    json_objects = []
    start = 0
    while True:
        json_start = content.find('{', start)
        if json_start == -1:
            break
        json_end = content.find('}', json_start) + 1
        if json_end == -1:
            break
        json_str = content[json_start:json_end].strip()
        json_objects.append(json_str)
        start = json_end
    return json_objects

def json_to_dataframes(json_content, file_name):
    info_dict = json.loads(json_content[0])
    items_list = json.loads(json_content[1])

    # 验证items_list是否是一个列表，并且每个元素都是字典
    if not isinstance(items_list, list) or not all(isinstance(item, dict) for item in items_list):
        raise TypeError("Items list is not a list of dictionaries")

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
    items_df = items_df[['ImageName'] + [col for col在items_df.columns if col != 'ImageName']]

    return info_df, items_df

def main():
    summary_info = []
    itemized_info = []

    files = [f for f in os.listdir(ERROR_FOLDER_PATH) if f.endswith('.txt')]
    
    for i, file_name in enumerate(files):  # 处理所有文件
        file_path = os.path.join(ERROR_FOLDER_PATH, file_name)
        content = read_file_content(file_path)
        print(f"Processing corrected file {i + 1}/{len(files)}: {file_name}")
        
        try:
            json_objects = extract_json_objects(content)
            if len(json_objects) < 2:
                raise ValueError("Expected JSON objects not found")
            info_df, items_df = json_to_dataframes(json_objects, file_name)
            
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
