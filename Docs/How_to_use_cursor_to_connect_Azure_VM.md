
# How to use Cursor to Connect Azure VM

In this guide, we will show you how to use Cursor and SSH to connect to your Azure virtual machine.

## SSH Command Format

In the SSH connection command prompt of Cursor, you need to input the following SSH command to connect to your Azure VM:

```bash
ssh <username>@<public-ip-address> -i <path-to-pem-file>
```

### Steps to fill the command:

1. **<username>**: This should be your SSH username for the Azure VM. For example, if your username is `azureuser`, you would use that.
   
2. **<public-ip-address>**: This is the public IP address of your Azure VM. For example, if your VM's public IP is `4.227.167.167`, you would input that IP.
   
3. **<path-to-pem-file>**: This is the path to your private SSH key file (`.pem`). If your `.pem` file is stored locally, for example, at `~/.ssh/my_key.pem`, you should specify this path.

### Example

If your username is `azureuser`, the public IP address of your VM is `4.227.167.167`, and the `.pem` file is located at `~/.ssh/my_key.pem`, the command would look like:

```bash
ssh azureuser@4.227.167.167 -i ~/.ssh/my_key.pem
```

After entering this command and pressing `Enter`, Cursor will connect to your Azure VM through SSH.

## Troubleshooting

If you encounter any issues or cannot find your `.pem` file, you may need to regenerate or locate the key pair.

