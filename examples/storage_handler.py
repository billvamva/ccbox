from ccbox.storage_handler import AzureStorageHandler
from ccbox.virtual_drive import Virtual_Drive        
        
if __name__ == "__main__":
        # Replace this with your actual account URL and container name
        def create_vd():

                vd = Virtual_Drive()
                
                account_url = 'https://saccbox.blob.core.windows.net'
                container_name = f'virtual-drive-0'
                azure_storage = AzureStorageHandler(account_url, container_name=container_name)
                vd.add_remote(azure_storage)
                
                vd.mount_directory("../data/mnt")
                current_folder = vd.change_directory("mnt")
                current_folder.show_contents()
                current_folder = current_folder.change_directory("subfolder")
                current_folder.show_contents()
                vd.save_to_remote()
                vd.upload_contents()
        
        def retrieve_vd():
                vd = Virtual_Drive(_id=0, _from_dict=True)
                account_url = 'https://saccbox.blob.core.windows.net'
                container_name = f'virtual-drive-0'
                azure_storage = AzureStorageHandler(account_url, container_name=container_name)
                vd.add_remote(azure_storage)
                vd.load_from_remote('virtual_drive_0.json')  # Load from Azure Storage
                print(vd.to_dict())
        
        retrieve_vd()