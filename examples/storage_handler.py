from ccbox.storage_handler import AzureStorageHandler
from ccbox.virtual_drive import Virtual_Drive        
        
if __name__ == "__main__":
        # Replace this with your actual account URL and container name
        vd = Virtual_Drive()
        
        account_url = 'https://saccbox.blob.core.windows.net'
        container_name = f'virtual-drive-{vd._id}'
        azure_storage = AzureStorageHandler(account_url, container_name=container_name)
        
        vd.add_remote(azure_storage)
        vd.mount_directory("../data/mnt")
        vd.show_contents()
        vd.upload_contents()
        # vd.load_from_remote('virtual_drive_1.json')  # Load from Azure Storage