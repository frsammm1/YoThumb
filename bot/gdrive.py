import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from bot.config import GOOGLE_CREDENTIALS, GDRIVE_FOLDER_ID, GDRIVE_ENABLED

class GDrive:
    def __init__(self):
        if not GDRIVE_ENABLED or not GOOGLE_CREDENTIALS:
            raise ValueError("Google Drive is not configured")
        
        self.credentials = service_account.Credentials.from_service_account_info(
            GOOGLE_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = GDRIVE_FOLDER_ID
    
    async def upload_file(self, file_path, file_name=None):
        if not file_name:
            file_name = os.path.basename(file_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [self.folder_id] if self.folder_id else []
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype='video/mp4',
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        
        self.service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return file.get('webContentLink') or file.get('webViewLink')
    
    def list_files(self, max_results=10):
        query = f"'{self.folder_id}' in parents" if self.folder_id else None
        
        results = self.service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, createdTime, size)"
        ).execute()
        
        return results.get('files', [])
