import json
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from datetime import date, datetime, time  


endpoint = "https://validationcomparisonwithgpt4o.cognitiveservices.azure.com/"
key = "6d166f7906c849f886727c9d50e19b40"


document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# Local file path
file_path = "/home/ec2-user/Myproject/Insurance/Data/Sample_Image (9).jpg"
# print(f"File path: {file_path}")clear


# Open and analyze the local file
with open(file_path, "rb") as f:
    poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", f)
    result = poller.result()
    # print(f"Result.documents: {result.documents}")

# Convert result to dictionary format
result_dict = result.to_dict()
# print(result_dict)

# Custom JSON encoder to handle date and time objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        return super().default(obj)

# Save the result to a JSON file
output_file = "/home/ec2-user/Myproject/Insurance/Data/Sample_Image (9)_output.json"
with open(output_file, "w") as json_file:
    json.dump(result_dict, json_file, indent=4, cls=CustomJSONEncoder)

for idx, invoice in enumerate(result.documents):
    print("--------Recognizing invoice #{}--------".format(idx + 1))
    vendor_name = invoice.fields.get("VendorName")
    if vendor_name:
        print("Vendor Name: {}".format(vendor_name.value))
        
    vendor_address = invoice.fields.get("VendorAddress")
    if vendor_address:
        print("Vendor Address: {}".format(vendor_address.value))
        
    vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
    if vendor_address_recipient:
        print("Vendor Address Recipient: {}".format(vendor_address_recipient.value))
        
    customer_name = invoice.fields.get("CustomerName")
    if customer_name:
        print("Customer Name: {}".format(customer_name.value))
        
    customer_id = invoice.fields.get("CustomerId")
    if customer_id:
        print("Customer Id: {}".format(customer_id.value))
        
    customer_address = invoice.fields.get("CustomerAddress")
    if customer_address:
        print("Customer Address: {}".format(customer_address.value))
        
    customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
    if customer_address_recipient:
        print("Customer Address Recipient: {}".format(customer_address_recipient.value))
        
    invoice_id = invoice.fields.get("InvoiceId")
    if invoice_id:
        print("Invoice Id: {}".format(invoice_id.value))
        
    invoice_date = invoice.fields.get("InvoiceDate")
    if invoice_date:
        print("Invoice Date: {}".format(invoice_date.value))
        
    invoice_total = invoice.fields.get("InvoiceTotal")
    if invoice_total:
        print("Invoice Total: {}".format(invoice_total.value))
        
    due_date = invoice.fields.get("DueDate")
    if due_date:
        print("Due Date: {}".format(due_date.value))
        
    purchase_order = invoice.fields.get("PurchaseOrder")
    if purchase_order:
        print("Purchase Order: {}".format(purchase_order.value))
        
    billing_address = invoice.fields.get("BillingAddress")
    if billing_address:
        print("Billing Address: {}".format(billing_address.value))
        
    billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
    if billing_address_recipient:
        print("Billing Address Recipient: {}".format(billing_address_recipient.value))
        
    shipping_address = invoice.fields.get("ShippingAddress")
    if shipping_address:
        print("Shipping Address: {}".format(shipping_address.value))
        
    shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
    if shipping_address_recipient:
        print("Shipping Address Recipient: {}".format(shipping_address_recipient.value))
        
    print("Invoice items:")
    for idx, item in enumerate(invoice.fields.get("Items").value):
        print("...Item #{}".format(idx + 1))
        item_description = item.value.get("Description")
        if item_description:
            print("......Description: {}".format(item_description.value))
            
        item_quantity = item.value.get("Quantity")
        if item_quantity:
            print("......Quantity: {}".format(item_quantity.value))
            
        unit = item.value.get("Unit")
        if unit:
            print("......Unit: {}".format(unit.value))
            
        unit_price = item.value.get("UnitPrice")
        if unit_price:
            print("......Unit Price: {}".format(unit_price.value))
            
        product_code = item.value.get("ProductCode")
        if product_code:
            print("......Product Code: {}".format(product_code.value))
            
        item_date = item.value.get("Date")
        if item_date:
            print("......Date: {}".format(item_date.value))
            
        tax = item.value.get("Tax")
        if tax:
            print("......Tax: {}".format(tax.value))
            
        amount = item.value.get("Amount")
        if amount:
            print("......Amount: {}".format(amount.value))
            
    subtotal = invoice.fields.get("SubTotal")
    if subtotal:
        print("Subtotal: {}".format(subtotal.value))
        
    total_tax = invoice.fields.get("TotalTax")
    if total_tax:
        print("Total Tax: {}".format(total_tax.value))
        
    previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
    if previous_unpaid_balance:
        print("Previous Unpaid Balance: {}".format(previous_unpaid_balance.value))
        
    amount_due = invoice.fields.get("AmountDue")
    if amount_due:
        print("Amount Due: {}".format(amount_due.value))
        
    service_start_date = invoice.fields.get("ServiceStartDate")
    if service_start_date:
        print("Service Start Date: {}".format(service_start_date.value))
        
    service_end_date = invoice.fields.get("ServiceEndDate")
    if service_end_date:
        print("Service End Date: {}".format(service_end_date.value))
        
    service_address = invoice.fields.get("ServiceAddress")
    if service_address:
        print("Service Address: {}".format(service_address.value))
        
    service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
    if service_address_recipient:
        print("Service Address Recipient: {}".format(service_address_recipient.value))
        
    remittance_address = invoice.fields.get("RemittanceAddress")
    if remittance_address:
        print("Remittance Address: {}".format(remittance_address.value))
        
    remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
    if remittance_address_recipient:
        print("Remittance Address Recipient: {}".format(remittance_address_recipient.value))
        
    print("----------------------------------------")
