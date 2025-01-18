import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import logging
import time

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, config):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        self.container_name = config['storage']['container_name']
        self.expiry_hours = config['storage']['expiry_hours']
        
        # Initialize client only when needed
        self._blob_service_client = None
        self._container_client = None

    @property
    def blob_service_client(self):
        if not self._blob_service_client:
            self._blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        return self._blob_service_client

    @property
    def container_client(self):
        if not self._container_client:
            self._container_client = self.blob_service_client.get_container_client(self.container_name)
            if not self._container_client.exists():
                self._container_client.create_container()
        return self._container_client

    def generate_sas_url(self, blob_name):
        """Generate SAS URL with minimal operations"""
        try:
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=self.expiry_hours)
            )
            
            # Construct URL without checking blob existence
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            return blob_url

        except Exception as e:
            logger.error(f"Error generating SAS URL: {e}")
            return None

    def upload_blob(self, data, blob_name):
        """Upload blob with minimal checks"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            return self.generate_sas_url(blob_name)
        except Exception as e:
            logger.error(f"Error uploading blob: {e}")
            return None

    def delete_blob(self, blob_name):
        """Delete blob without checking existence"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob(delete_snapshots="include")
            return True
        except Exception:
            return False 