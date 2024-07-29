import os
import json
import csv

# 文件目录
input_dir = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GPT-4o_mini/RawData_gpt4o_mini'
output_dir = '/home/ec2-user/Myproject/Insurance/Invoices_receipts/Batch_call_GPT-4o_mini/ProcessedData/'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# CSV 文件头
csv1_header = ["FileName", "CustomerName", "VendorName", "CustomerAddress", "VendorAddress", "InvoiceDate", "TotalTax", "InvoiceTotal", "AmountDue"]
csv2_header = ["FileName", "Description", "Quantity", "Unit", "UnitPrice", "ProductCode", "Date", "Tax", "Amount"]

# 打开CSV文件
with open(os.path.join(output_dir, 'summary_info_gpt_4o_mini.csv'), 'w', newline='', encoding='utf-8') as csv1_file, \
     open(os.path.join(output_dir, 'itemized_info_gpt_4o_mini.csv'), 'w', newline='', encoding='utf-8') as csv2_file:
    
    csv1_writer = csv.writer(csv1_file)
    csv2_writer = csv.writer(csv2_file)
    
    # 写入头部
    csv1_writer.writerow(csv1_header)
    csv2_writer.writerow(csv2_header)

    # 遍历输入目录中的每个TXT文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as file:
                data = file.read()
                # 去掉```json ```标记
                json_data = data.replace('```json', '').replace('```', '').strip()
                
                # 分离主JSON和明细JSON
                json_parts = json_data.split('\n\n')
                if len(json_parts) == 2:
                    main_json = json.loads(json_parts[0])
                    details_json = json.loads(json_parts[1])
                    
                    # 写入主CSV文件
                    csv1_writer.writerow([
                        filename,
                        main_json.get("CustomerName"),
                        main_json.get("VendorName"),
                        main_json.get("CustomerAddress"),
                        main_json.get("VendorAddress"),
                        main_json.get("InvoiceDate"),
                        main_json.get("TotalTax"),
                        main_json.get("InvoiceTotal"),
                        main_json.get("AmountDue")
                    ])
                    
                    # 写入明细CSV文件
                    for detail in details_json:
                        csv2_writer.writerow([
                            filename,
                            detail.get("Description"),
                            detail.get("Quantity"),
                            detail.get("Unit"),
                            detail.get("UnitPrice"),
                            detail.get("ProductCode"),
                            detail.get("Date"),
                            detail.get("Tax"),
                            detail.get("Amount")
                        ])
