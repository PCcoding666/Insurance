import os
import numpy as np
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

def is_supported_image(file_path):
    try:
        Image.open(file_path).verify()
        return True
    except (IOError, SyntaxError) as e:
        return False

def extract(file_path, client):
    # 打开图片文件并读取为二进制流
    with open(file_path, "rb") as file:
        poller = client.begin_analyze_document("prebuilt-invoice", document=file)
    # 获取分析结果
    invoices = poller.result()
    return invoices

def info_extract(invoices, file_name):
    docs = invoices.documents
    info_dict = {'FileName': file_name}
    items_list = []

    for doc in docs:
        fields = doc.fields

        CustomerName = fields.get('CustomerName')
        if CustomerName:
            info_dict['CustomerName'] = CustomerName.content
        else:
            info_dict['CustomerName'] = None

        VendorName = fields.get('VendorName')
        if VendorName:
            info_dict['VendorName'] = VendorName.content
        else:
            info_dict['VendorName'] = None

        CustomerAddress = fields.get('CustomerAddress')
        if CustomerAddress:
            info_dict['CustomerAddress'] = CustomerAddress.content
        else:
            info_dict['CustomerAddress'] = None

        VendorAddress = fields.get('VendorAddress')
        if VendorAddress:
            info_dict['VendorAddress'] = VendorAddress.content
        else:
            info_dict['VendorAddress'] = None

        InvoiceDate = fields.get('InvoiceDate')
        if InvoiceDate:
            info_dict['InvoiceDate'] = InvoiceDate.content
        else:
            info_dict['InvoiceDate'] = None

        TotalTax = fields.get('TotalTax')
        if TotalTax:
            info_dict['TotalTax'] = TotalTax.content
        else:
            info_dict['TotalTax'] = None

        InvoiceTotal = fields.get('InvoiceTotal')
        if InvoiceTotal:
            info_dict['InvoiceTotal'] = InvoiceTotal.content
        else:
            info_dict['InvoiceTotal'] = None

        AmountDue = fields.get('AmountDue')
        if AmountDue:
            info_dict['AmountDue'] = AmountDue.content
        else:
            info_dict['AmountDue'] = None

        Items = fields.get('Items')
        if Items:
            for item in Items.value:
                item_dict = {'FileName': file_name}
                item_dict['Description'] = item.value.get('Description').content if item.value.get('Description') else None
                item_dict['Quantity'] = item.value.get('Quantity').content if item.value.get('Quantity') else None
                item_dict['Unit'] = item.value.get('Unit').content if item.value.get('Unit') else None
                item_dict['UnitPrice'] = item.value.get('UnitPrice').content if item.value.get('UnitPrice') else None
                item_dict['ProductCode'] = item.value.get('ProductCode').content if item.value.get('ProductCode') else None
                item_dict['Date'] = item.value.get('Date').content if item.value.get('Date') else None
                item_dict['Tax'] = item.value.get('Tax').content if item.value.get('Tax') else None
                item_dict['Amount'] = item.value.get('Amount').content if item.value.get('Amount') else None

                items_list.append(item_dict)

    return info_dict, items_list

def save_to_dataframes(info_dict, items_list):
    info_df = pd.DataFrame([info_dict])
    items_df = pd.DataFrame(items_list)
    return info_df, items_df

def process_file(file_path, client):
    try:
        invoices = extract(file_path, client)
        info_dict, items_list = info_extract(invoices, os.path.basename(file_path))
        return info_dict, items_list
    except Exception as e:
        print(f"An error occurred while processing file {file_path}: {e}")
        return None, None

def main():
    # Azure Form Recognizer 认证
    key = "6d166f7906c849f886727c9d50e19b40"
    endpoint = "https://validationcomparisonwithgpt4o.cognitiveservices.azure.com/"
    
    # 创建客户端
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
    # 文件夹路径
    folder_path = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_Azure/Data'
    result_path = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_Azure/Result'
    
    all_info_df = pd.DataFrame()
    all_items_df = pd.DataFrame()
    
    # 处理文件夹中的所有图片文件
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if is_supported_image(os.path.join(folder_path, f))]
    total_files = len(files)
    print(f"Total number of files to process: {total_files}")
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, file, document_analysis_client) for file in files]
        
        for i, future in enumerate(as_completed(futures)):
            file_name = os.path.basename(files[i])
            print(f"Processing file {i + 1}/{total_files}: {file_name}")
            info_dict, items_list = future.result()
            
            if info_dict and items_list:
                info_df, items_df = save_to_dataframes(info_dict, items_list)
                
                all_info_df = pd.concat([all_info_df, info_df], ignore_index=True)
                all_items_df = pd.concat([all_items_df, items_df], ignore_index=True)
    
    # 将np.nan替换为None
    all_info_df = all_info_df.where(pd.notnull(all_info_df), None)
    all_items_df = all_items_df.where(pd.notnull(all_items_df), None)
    
    # 保存到CSV文件，使用UTF-8编码
    info_csv_path = os.path.join(result_path, "summary_info_azure.csv")
    items_csv_path = os.path.join(result_path, "itemized_info_azure.csv")
    
    all_info_df.to_csv(info_csv_path, index=False, encoding='utf-8')
    all_items_df.to_csv(items_csv_path, index=False, encoding='utf-8')
    
    print(f"Data extraction complete. CSV files have been saved to {result_path}")

if __name__ == "__main__":
    main()
