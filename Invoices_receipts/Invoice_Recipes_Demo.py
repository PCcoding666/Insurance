#Invoices_receipts/Invoice_Recipes_Demo.py
import os
import numpy as np
import pandas as pd
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from PIL import Image

def is_supported_image(file_path):
    try:
        Image.open(file_path).verify()
        return True
    except (IOError, SyntaxError) as e:
        return False

def extract(file_path):
    key = st.secrets['key']
    endpoint = st.secrets['endpoint']
    # 创建客户端
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # 打开图片文件并读取为二进制流
    with open(file_path, "rb") as file:
        poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", document=file)
    # 获取分析结果
    invoices = poller.result()
    return invoices

def info_extract(invoices):
    docs = invoices.documents
    info_dict = {}
    items_list = []

    for doc in docs:
        fields = doc.fields

        CustomerName = fields.get('CustomerName')
        if CustomerName:
            info_dict['CustomerName'] = CustomerName.content
        else:
            info_dict['CustomerName'] = np.nan

        VendorName = fields.get('VendorName')
        if VendorName:
            info_dict['VendorName'] = VendorName.content
        else:
            info_dict['VendorName'] = np.nan

        CustomerAddress = fields.get('CustomerAddress')
        if CustomerAddress:
            info_dict['CustomerAddress'] = CustomerAddress.content
        else:
            info_dict['CustomerAddress'] = np.nan

        VendorAddress = fields.get('VendorAddress')
        if VendorAddress:
            info_dict['VendorAddress'] = VendorAddress.content
        else:
            info_dict['VendorAddress'] = np.nan

        InvoiceDate = fields.get('InvoiceDate')
        if InvoiceDate:
            info_dict['InvoiceDate'] = InvoiceDate.content
        else:
            info_dict['InvoiceDate'] = np.nan

        TotalTax = fields.get('TotalTax')
        if TotalTax:
            info_dict['TotalTax'] = TotalTax.content
        else:
            info_dict['TotalTax'] = np.nan

        InvoiceTotal = fields.get('InvoiceTotal')
        if InvoiceTotal:
            info_dict['InvoiceTotal'] = InvoiceTotal.content
        else:
            info_dict['InvoiceTotal'] = np.nan

        AmountDue = fields.get('AmountDue')
        if AmountDue:
            info_dict['AmountDue'] = AmountDue.content
        else:
            info_dict['AmountDue'] = np.nan

        Items = fields.get('Items')
        if Items:
            for item in Items.value:
                item_dict = {}
                item_dict['Description'] = item.value.get('Description').content if item.value.get(
                    'Description') else np.nan
                item_dict['Quantity'] = item.value.get('Quantity').content if item.value.get('Quantity') else np.nan
                item_dict['Unit'] = item.value.get('Unit').content if item.value.get('Unit') else np.nan
                item_dict['UnitPrice'] = item.value.get('UnitPrice').content if item.value.get('UnitPrice') else np.nan
                item_dict['ProductCode'] = item.value.get('ProductCode').content if item.value.get(
                    'ProductCode') else np.nan
                item_dict['Date'] = item.value.get('Date').content if item.value.get('Date') else np.nan
                item_dict['Tax'] = item.value.get('Tax').content if item.value.get('Tax') else np.nan
                item_dict['Amount'] = item.value.get('Amount').content if item.value.get('Amount') else np.nan

                items_list.append(item_dict)

    return info_dict, items_list

def save_to_dataframes(info_dict, items_list):
    info_df = pd.DataFrame([info_dict])
    items_df = pd.DataFrame(items_list)
    return info_df, items_df

# Streamlit App
st.title("Invoice, Recipes Data Extraction")

uploaded_file = st.file_uploader("Choose an invoice image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Ensure the 'temp' directory exists
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Save the uploaded file temporarily
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if is_supported_image(temp_file_path):
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        if st.button("Submit"):
            with st.spinner('Extracting data...'):
                invoices = extract(temp_file_path)
                info_dict, items_list = info_extract(invoices)
                info_df, items_df = save_to_dataframes(info_dict, items_list)

            st.success('Data extraction complete!')

            st.subheader("Extracted Information")
            st.dataframe(info_df)

            st.subheader("Extracted Items")
            st.dataframe(items_df)
    else:
        st.error("The uploaded file is not a valid image or is corrupted.")
