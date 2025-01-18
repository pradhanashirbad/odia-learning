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
            # Upload to Vercel Blob
            blob = await put(blob_name, data, {'access': 'public'})
            return blob.url
        except Exception as e:
            logger.error(f"Error uploading to Vercel Blob: {e}")
            return None

    async def delete_blob(self, blob_name):
        """Delete blob from Vercel Blob Storage"""
        try:
            await delete(blob_name)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Vercel Blob: {e}")
            return False 