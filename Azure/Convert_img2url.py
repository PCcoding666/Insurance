from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# 设置Azure存储连接字符串和容器名称
container_name = "convertimg2url"
sas_url = 'https://convertimg2url.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-06-04T09:48:31Z&st=2024-06-04T01:48:31Z&spr=https&sig=%2BRwgBU%2F7U2TUm%2BQU0O0zgWfopIIZJ3lA9FS6tRF1JF4%3D'

# 本地文件路径
local_file_path = "/home/ec2-user/Myproject/Insurance/Data/multi_image_input_test(2).jpg"
blob_name = os.path.basename(local_file_path)

# 创建Blob服务客户端
blob_service_client = BlobServiceClient(account_url=sas_url)

# 创建容器客户端
container_client = blob_service_client.get_container_client(container_name)

# 如果容器不存在，则创建容器
if not container_client.exists():
    container_client.create_container()

# 创建Blob客户端
blob_client = container_client.get_blob_client(blob_name)

# 上传本地文件到Blob存储
with open(local_file_path, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

# 获取上传后的Blob URL
blob_url = blob_client.url
print("Uploaded to Blob Storage URL:", blob_url)
