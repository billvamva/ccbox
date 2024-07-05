import unittest
import json
from unittest.mock import patch, MagicMock
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from azure.identity import DefaultAzureCredential
from ccbox.storage_handler import AzureStorageHandler  # Replace with your actual module name

class TestAzureStorageHandler(unittest.TestCase):
    
        @patch('ccbox.storage_handler.BlobServiceClient')
        @patch('ccbox.storage_handler.DefaultAzureCredential')
        def setUp(self, mock_credential, mock_blob_service_client):
                self.mock_blob_service_client = mock_blob_service_client.return_value
                self.mock_container_client = MagicMock(spec=ContainerClient)
                self.mock_blob_service_client.get_container_client.return_value = self.mock_container_client
                
                self.handler = AzureStorageHandler(account_url='http://fake_account_url', container_name='fake_container')

        def test_init(self):
                self.mock_blob_service_client.get_container_client.assert_called_once_with('fake_container')
                self.mock_blob_service_client.create_container.assert_called_once_with(name='fake_container')

        def test_upload_from_bytes(self):
                mock_blob_client = MagicMock(spec=BlobClient)
                self.mock_blob_service_client.get_blob_client.return_value = mock_blob_client

                self.handler.upload_from_bytes('fake_container', 'fake_blob', b'test data')

                mock_blob_client.upload_blob.assert_called_once_with(b'test_data', overwrite=True)

        def test_upload_json(self):
                mock_blob_client = MagicMock(spec=BlobClient)
                self.mock_container_client.get_blob_client.return_value = mock_blob_client
                json_data = {"key": "value"}

                self.handler.upload_json(json_data, 'fake_blob')

                mock_blob_client.upload_blob.assert_called_once_with(json.dumps(json_data), overwrite=True)

        def test_download_json(self):
                mock_blob_client = MagicMock(spec=BlobClient)
                mock_download_stream = MagicMock()
                mock_blob_client.download_blob.return_value = mock_download_stream
                mock_download_stream.readall.return_value = b'{"key": "value"}'
                self.mock_container_client.get_blob_client.return_value = mock_blob_client

                result = self.handler.download_json('fake_blob')

                self.assertEqual(result, {"key": "value"})
                mock_blob_client.download_blob.assert_called_once()
                mock_download_stream.readall.assert_called_once()

        def test_to_dict(self):
                result = self.handler.to_dict()
                expected = {
                "account_url": "http://fake_account_url",
                "container_name": "fake_container"
                }
                self.assertEqual(result, expected)

        def test_from_dict(self):
                data = {
                "account_url": "http://fake_account_url",
                "container_name": "fake_container"
                }
                handler = AzureStorageHandler.from_dict(data)
                self.assertEqual(handler.account_url, "http://fake_account_url")
                self.assertEqual(handler.container_name, "fake_container")

if __name__ == '__main__':
    unittest.main()