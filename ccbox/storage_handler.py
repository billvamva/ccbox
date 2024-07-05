from abc import ABC, abstractmethod
from typing import Union, List, Dict, Optional, Any, ClassVar, Callable
import json
import time

from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


class StorageHandler(ABC):
    
        @abstractmethod
        def upload_json(self, json_data: Dict, blob_name: str):
                pass

        @abstractmethod
        def download_json(self, blob_name: str) -> Dict:
                pass

        @abstractmethod
        def upload_from_bytes(self, container_name: str, blob_name: str, data: bytes) -> None:
                pass
        
        @abstractmethod
        def to_dict(self) -> Dict:
                pass

        @classmethod
        @abstractmethod
        def from_dict(cls, data: dict) -> "StorageHandler":
                pass



class AzureStorageHandler(StorageHandler):
        def __init__(self, account_url: str, container_name: str):
                self.account_url = account_url
                self.container_name = container_name
                credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
                self.create_blob_container(self.blob_service_client, container_name)
                self.container_client = self.blob_service_client.get_container_client(container_name)
                self.container_name = container_name
        
        def create_blob_container(self, blob_service_client: BlobServiceClient, container_name: str):
                try:
                        container_client = blob_service_client.create_container(name=container_name)
                except Exception as e:
                        print(f'Error: {e}')

        
        def upload_from_bytes(self, container_name: str, blob_name: str, data: bytes) -> None:
                try:
                        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                        blob_client.upload_blob(data, overwrite=True)
                except Exception as e:
                        time.sleep(1)
                

        def upload_json(self, json_data: Dict, blob_name: str) -> None:
                blob_client = self.container_client.get_blob_client(blob_name)
                blob_client.upload_blob(json.dumps(json_data), overwrite=True)
                print(f"Uploaded {blob_name} to Azure Storage")

        def download_json(self, blob_name: str) -> dict:
                try:
                        blob_client = self.container_client.get_blob_client(blob_name)
                        download_stream = blob_client.download_blob()
                        json_data = json.loads(download_stream.readall())
                        print(f"Downloaded {blob_name} from Azure Storage")
                        return json_data
                except Exception as e:
                        print(f'Error: {e}')
        
        def to_dict(self) -> dict:
                return {
                        "account_url" : self.account_url,
                        "container_name" : self.container_name
                } 
        
        @classmethod
        def from_dict(cls, data:dict) -> "StorageHandler":
                return cls(data["account_url"], data["container_name"])
        