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
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Create container if it doesn't exist
            if not self.container_client.exists():
                self.container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        
        except Exception as e:
            logger.error(f"Error initializing blob storage: {e}")
            raise

    def upload_file(self, file_path: str, blob_name: str = None) -> str:
        """
        Upload a file to blob storage and return a SAS URL
        """
        try:
            if blob_name is None:
                blob_name = os.path.basename(file_path)

            # Make sure file exists and is accessible
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Upload the file
                    with open(file_path, "rb") as data:
                        blob_client = self.container_client.get_blob_client(blob_name)
                        blob_client.upload_blob(data, overwrite=True)
                    break  # If successful, break the retry loop
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise  # Re-raise the last exception
                    logger.warning(f"Upload attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(retry_delay)

            # Generate SAS URL
            sas_url = self.generate_sas_url(blob_name)
            return sas_url

        except Exception as e:
            logger.error(f"Error uploading file to blob storage: {e}")
            raise

    def generate_sas_url(self, blob_name: str) -> str:
        """
        Generate a SAS URL for the blob that expires after the configured hours
        """
        try:
            # Calculate expiry time
            expiry = datetime.utcnow() + timedelta(hours=self.expiry_hours)

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=expiry
            )

            # Construct the full URL
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            
            return blob_url

        except Exception as e:
            logger.error(f"Error generating SAS URL: {e}")
            raise

    def cleanup_expired_blobs(self):
        """
        Clean up expired blobs from the container
        """
        try:
            expiry_time = datetime.utcnow() - timedelta(hours=self.expiry_hours)
            
            blobs = self.container_client.list_blobs()
            for blob in blobs:
                if blob.last_modified < expiry_time:
                    self.container_client.delete_blob(blob.name)
                    logger.info(f"Deleted expired blob: {blob.name}")

        except Exception as e:
            logger.error(f"Error cleaning up expired blobs: {e}")
            raise 