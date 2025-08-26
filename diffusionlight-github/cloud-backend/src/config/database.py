import os
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# SQLAlchemy instance
db = SQLAlchemy()

# Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

def init_database(app):
    """Initialize database with Flask app"""
    
    # Configure PostgreSQL for Supabase
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to SQLite for local development
        database_url = 'sqlite:///local_app.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return db

def get_supabase_client():
    """Get Supabase client instance"""
    return supabase

class SupabaseStorage:
    """Helper class for Supabase Storage operations"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.bucket_name = os.getenv('SUPABASE_BUCKET', 'diffusionlight-files')
    
    def upload_file(self, file_path: str, file_data: bytes, content_type: str = None):
        """Upload file to Supabase Storage"""
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            result = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_data,
                file_options={
                    "content-type": content_type or "application/octet-stream"
                }
            )
            return result
        except Exception as e:
            print(f"Error uploading file to Supabase: {e}")
            return None
    
    def download_file(self, file_path: str):
        """Download file from Supabase Storage"""
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            result = self.client.storage.from_(self.bucket_name).download(file_path)
            return result
        except Exception as e:
            print(f"Error downloading file from Supabase: {e}")
            return None
    
    def get_public_url(self, file_path: str):
        """Get public URL for file"""
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            result = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return result
        except Exception as e:
            print(f"Error getting public URL: {e}")
            return None
    
    def delete_file(self, file_path: str):
        """Delete file from Supabase Storage"""
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            result = self.client.storage.from_(self.bucket_name).remove([file_path])
            return result
        except Exception as e:
            print(f"Error deleting file from Supabase: {e}")
            return None

