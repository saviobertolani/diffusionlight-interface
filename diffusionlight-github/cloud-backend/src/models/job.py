from datetime import datetime
from src.config.database import db
import json

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    progress = db.Column(db.Integer, default=0)
    
    # External job tracking
    external_job_id = db.Column(db.String(255))  # RunPod job ID
    
    # File information
    input_file_id = db.Column(db.String(36), db.ForeignKey('file_uploads.id'), nullable=False)
    input_file_name = db.Column(db.String(255), nullable=False)
    
    # Configuration
    configuration = db.Column(db.Text)  # JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Processing info
    processing_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    
    # Results
    result_files = db.Column(db.Text)  # JSON string with file paths
    
    # Relationships
    input_file = db.relationship('FileUpload', backref='jobs')
    
    def __init__(self, **kwargs):
        super(Job, self).__init__(**kwargs)
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
    
    def set_configuration(self, config_dict):
        """Set configuration as JSON string"""
        self.configuration = json.dumps(config_dict) if config_dict else None
    
    def get_configuration(self):
        """Get configuration as dictionary"""
        if self.configuration:
            try:
                return json.loads(self.configuration)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_result_files(self, files_list):
        """Set result files as JSON string"""
        self.result_files = json.dumps(files_list) if files_list else None
    
    def get_result_files(self):
        """Get result files as list"""
        if self.result_files:
            try:
                return json.loads(self.result_files)
            except json.JSONDecodeError:
                return []
        return []
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'input_file_id': self.input_file_id,
            'input_file_name': self.input_file_name,
            'configuration': self.get_configuration(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time,
            'error_message': self.error_message,
            'result_files': self.get_result_files()
        }

class FileUpload(db.Model):
    __tablename__ = 'file_uploads'
    
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    content_type = db.Column(db.String(100))
    
    # File metadata
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    format = db.Column(db.String(10))
    
    # Storage paths
    local_path = db.Column(db.String(500))  # Local temp path
    storage_path = db.Column(db.String(500))  # Supabase storage path
    public_url = db.Column(db.String(1000))  # Public URL
    
    # File integrity
    checksum = db.Column(db.String(64))
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(FileUpload, self).__init__(**kwargs)
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'file_id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'size': self.file_size,
            'content_type': self.content_type,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'storage_path': self.storage_path,
            'public_url': self.public_url,
            'checksum': self.checksum,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

