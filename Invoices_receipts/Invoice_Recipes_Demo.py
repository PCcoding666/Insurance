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
    print(invoices)
    return invoices

def info_extract(invoices):
    docs = invoices.documents
    info_dict = {}
    items_list = []

    for doc in docs:
        fields = doc.fields

        CustomerName = fields.get('CustomerName')
        info_dict['CustomerName'] = CustomerName.content if CustomerName else np.nan

        CustomerId = fields.get('CustomerId')
        info_dict['CustomerId'] = CustomerId.content if CustomerId else np.nan

        PurchaseOrder = fields.get('PurchaseOrder')
        info_dict['PurchaseOrder'] = PurchaseOrder.content if PurchaseOrder else np.nan

        Invoiceld = fields.get('Invoiceld')
        info_dict['Invoiceld'] = Invoiceld.content if Invoiceld else np.nan

        InvoiceDate = fields.get('InvoiceDate')
        info_dict['InvoiceDate'] = InvoiceDate.content if InvoiceDate else np.nan

        DueDate = fields.get('DueDate')
        info_dict['DueDate'] = DueDate.content if DueDate else np.nan

        VendorName = fields.get('VendorName')
        info_dict['VendorName'] = VendorName.content if VendorName else np.nan

        VendorAddress = fields.get('VendorAddress')
        info_dict['VendorAddress'] = VendorAddress.content if VendorAddress else np.nan

        VendorAddressRecipient = fields.get('VendorAddressRecipient')
        info_dict['VendorAddressRecipient'] = VendorAddressRecipient.content if VendorAddressRecipient else np.nan

        CustomerAddress = fields.get('CustomerAddress')
        info_dict['CustomerAddress'] = CustomerAddress.content if CustomerAddress else np.nan

        CustomerAddressRecipient = fields.get('CustomerAddressRecipient')
        info_dict['CustomerAddressRecipient'] = CustomerAddressRecipient.content if CustomerAddressRecipient else np.nan

        BillingAddress = fields.get('BillingAddress')
        info_dict['BillingAddress'] = BillingAddress.content if BillingAddress else np.nan

        BillingAddressRecipient = fields.get('BillingAddressRecipient')
        info_dict['BillingAddressRecipient'] = BillingAddressRecipient.content if BillingAddressRecipient else np.nan

        ShippingAddress = fields.get('ShippingAddress')
        info_dict['ShippingAddress'] = ShippingAddress.content if ShippingAddress else np.nan

        ShippingAddressRecipient = fields.get('ShippingAddressRecipient')
        info_dict['ShippingAddressRecipient'] = ShippingAddressRecipient.content if ShippingAddressRecipient else np.nan

        SubTotal = fields.get('SubTotal')
        info_dict['SubTotal'] = SubTotal.content if SubTotal else np.nan

        TotalDiscount = fields.get('TotalDiscount')
        info_dict['TotalDiscount'] = TotalDiscount.content if TotalDiscount else np.nan

        TotalTax = fields.get('TotalTax')
        info_dict['TotalTax'] = TotalTax.content if TotalTax else np.nan

        InvoiceTotal = fields.get('InvoiceTotal')
        info_dict['InvoiceTotal'] = InvoiceTotal.content if InvoiceTotal else np.nan

        AmountDue = fields.get('AmountDue')
        info_dict['AmountDue'] = AmountDue.content if AmountDue else np.nan

        PreviousUnpaidBalance = fields.get('PreviousUnpaidBalance')
        info_dict['PreviousUnpaidBalance'] = PreviousUnpaidBalance.content if PreviousUnpaidBalance else np.nan

        RemittanceAddress = fields.get('RemittanceAddress')
        info_dict['RemittanceAddress'] = RemittanceAddress.content if RemittanceAddress else np.nan

        RemittanceAddressRecipient = fields.get('RemittanceAddressRecipient')
        info_dict['RemittanceAddressRecipient'] = RemittanceAddressRecipient.content if RemittanceAddressRecipient else np.nan

        ServiceAddress = fields.get('ServiceAddress')
        info_dict['ServiceAddress'] = ServiceAddress.content if ServiceAddress else np.nan

        ServiceAddressRecipient = fields.get('ServiceAddressRecipient')
        info_dict['ServiceAddressRecipient'] = ServiceAddressRecipient.content if ServiceAddressRecipient else np.nan

        ServiceStartDate = fields.get('ServiceStartDate')
        info_dict['ServiceStartDate'] = ServiceStartDate.content if ServiceStartDate else np.nan

        ServiceEndDate = fields.get('ServiceEndDate')
        info_dict['ServiceEndDate'] = ServiceEndDate.content if ServiceEndDate else np.nan

        VendorTaxId = fields.get('VendorTaxId')
        info_dict['VendorTaxId'] = VendorTaxId.content if VendorTaxId else np.nan

        CustomerTaxId = fields.get('CustomerTaxId')
        info_dict['CustomerTaxId'] = CustomerTaxId.content if CustomerTaxId else np.nan

        PaymentTerm = fields.get('PaymentTerm')
        info_dict['PaymentTerm'] = PaymentTerm.content if PaymentTerm else np.nan

        Items = fields.get('Items')
        if Items:
            for item in Items.value:
                item_dict = {}
                item_dict['Amount'] = item.value.get('Amount').content if item.value.get('Amount') else np.nan
                item_dict['Date'] = item.value.get('Date').content if item.value.get('Date') else np.nan
                item_dict['Description'] = item.value.get('Description').content if item.value.get('Description') else np.nan
                item_dict['Quantity'] = item.value.get('Quantity').content if item.value.get('Quantity') else np.nan
                item_dict['ProductCode'] = item.value.get('ProductCode').content if item.value.get('ProductCode') else np.nan
                item_dict['Tax'] = item.value.get('Tax').content if item.value.get('Tax') else np.nan
                item_dict['TaxRate'] = item.value.get('TaxRate').content if item.value.get('TaxRate') else np.nan
                item_dict['Unit'] = item.value.get('Unit').content if item.value.get('Unit') else np.nan
                item_dict['UnitPrice'] = item.value.get('UnitPrice').content if item.value.get('UnitPrice') else np.nan
                items_list.append(item_dict)

                items_list.append(item_dict)

    return info_dict, items_list

def save_to_dataframes(info_dict, items_list):
    info_df = pd.DataFrame([info_dict])
    items_df = pd.DataFrame(items_list)
    return info_df, items_df

# Streamlit App
st.set_page_config(page_title="Invoice Data Extraction", layout="wide")
st.title("Invoice and Receipt Data Extraction")

uploaded_file = st.file_uploader("Upload an invoice image", type=["jpg", "jpeg", "png"])

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
        st.image(uploaded_file, caption='Uploaded Image', use_container_width=True)

        if st.button("Extract Data"):
            with st.spinner('Extracting data...'):
                invoices = extract(temp_file_path)
                info_dict, items_list = info_extract(invoices)
                info_df, items_df = save_to_dataframes(info_dict, items_list)

            st.success('Data extraction complete!')

            st.subheader("Extracted Information")
            st.dataframe(info_df.transpose())  # Transpose the DataFrame to switch rows and columns

            st.subheader("Extracted Items")
            st.dataframe(items_df)
    else:
        st.error("The uploaded file is not a valid image or is corrupted.")
