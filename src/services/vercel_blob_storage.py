import os
from datetime import datetime
import logging
from vercel_blob import put, delete

logger = logging.getLogger(__name__)

class VercelBlobStorage:
    def __init__(self, config):
        self.container_name = config['storage']['container_name']
        self.expiry_hours = config['storage']['expiry_hours']

    async def upload_blob(self, data, blob_name):
        """Upload data to Vercel Blob Storage"""
        try:
            # Add more logging
            logger.info(f"Attempting to upload blob: {blob_name}")
            
            # Upload to Vercel Blob with pathname
            pathname = f"{self.container_name}/{blob_name}"
            blob = await put(pathname, data, {'access': 'public'})
            
            logger.info(f"Upload successful. URL: {blob.url}")
            return blob.url

        except Exception as e:
            logger.error(f"Detailed error uploading to Vercel Blob: {str(e)}")
            # Re-raise with more context
            raise Exception(f"Vercel Blob upload failed: {str(e)}")

    async def delete_blob(self, blob_name):
        """Delete blob from Vercel Blob Storage"""
        try:
            pathname = f"{self.container_name}/{blob_name}"
            await delete(pathname)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Vercel Blob: {e}")
            return False 