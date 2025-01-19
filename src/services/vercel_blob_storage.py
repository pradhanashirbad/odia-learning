import os
from datetime import datetime
import logging
from vercel_blob import put, delete

logger = logging.getLogger(__name__)

class VercelBlobStorage:
    def __init__(self, config):
        self.container_name = config['vercel_storage']['container_name']
        self.expiry_hours = config['vercel_storage']['expiry_hours']

    async def upload_blob(self, data, blob_name):
        """Upload data to Vercel Blob Storage"""
        try:
            logger.info(f"Attempting to upload blob: {blob_name}")
            
            # Convert data to bytes if it's not already
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Create blob path and upload
            pathname = f"{self.container_name}/{blob_name}"
            result = put(pathname, data, {'access': 'public'})
            
            logger.info(f"Upload successful. Result: {result}")
            return result['url'] if isinstance(result, dict) and 'url' in result else str(result)

        except Exception as e:
            logger.error(f"Detailed error uploading to Vercel Blob: {str(e)}")
            raise Exception(f"Vercel Blob upload failed: {str(e)}")

    async def delete_blob(self, blob_name):
        """Delete blob from Vercel Blob Storage"""
        try:
            pathname = f"{self.container_name}/{blob_name}"
            delete(pathname)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Vercel Blob: {e}")
            return False 