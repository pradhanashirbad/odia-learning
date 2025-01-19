import os
from azure.storage.blob import BlobServiceClient
import logging

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, config):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = config['storage']['container_name']
        
        try:
            # Just initialize the client
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            logger.info("Blob storage client initialized")
        except Exception as e:
            logger.error(f"Error initializing blob storage: {e}")
            # Don't raise the error, just log it 