#Invoices_receipts/Convert_img2url.py
import os
from azure.storage.blob import BlobServiceClient, ContentSettings

def upload_blob_and_get_url(local_file_path, container_name, sas_url):
    """
    Upload a local file to Azure Blob storage and get its URL.

    Parameters:
    local_file_path (str): Path to the local file
    container_name (str): Azure Blob storage container name
    sas_url (str): Blob storage service URL with SAS token

    Returns:
    str: URL of the uploaded Blob
    """
    try:
        # Get the file name
        blob_name = os.path.basename(local_file_path)
        # Create the Blob service client
        blob_service_client = BlobServiceClient(account_url=sas_url)
        # Create the container client
        container_client = blob_service_client.get_container_client(container_name)
        # If the container does not exist, create it
        if not container_client.exists():
            container_client.create_container()
        # Create the Blob client
        blob_client = container_client.get_blob_client(blob_name)
        # Upload the local file to Blob storage
        with open(local_file_path, "rb") as data:
            content_settings = ContentSettings(content_type='image/jpeg')
            blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
        # Get the URL of the uploaded Blob
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        return blob_url

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"SAS URL: {sas_url}")
        return None


# Example call
if __name__ == "__main__":
    container_name = "convertimg2url"
    sas_url = 'https://convertimg2url.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-08-01T10:41:17Z&st=2024-07-15T02:41:17Z&spr=https&sig=yutHqk7I44AnQU7wIaStABgRyJLEa4vxaqRJC%2BfzpeE%3D'
    local_file_path = "/home/ec2-user/Myproject/Insurance/Data/multi_image_input_test.jpg"

    blob_url = upload_blob_and_get_url(local_file_path, container_name, sas_url)

    if blob_url:
        print("File uploaded successfully. Blob URL:", blob_url)
    else:
        print("Failed to upload file.")
