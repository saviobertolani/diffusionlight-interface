import os
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image
import io

from src.config.database import db, SupabaseStorage
from src.models.job import Job, FileUpload
from src.services.runpod_service import get_runpod_service
from src.workers.tasks import process_hdri_task

api_bp = Blueprint('api', __name__)

# Initialize services
storage = SupabaseStorage()
runpod_service = get_runpod_service()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': 'connected',
            'storage': 'available' if storage.client else 'unavailable',
            'runpod': 'available' if runpod_service.is_available() else 'mock'
        }
    })

@api_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """Upload file endpoint with Supabase Storage"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'tiff', 'tif'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Supported: JPG, PNG, TIFF'}), 400
    
    try:
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        
        # Validate file size (200MB max)
        max_size = 200 * 1024 * 1024
        if file_size > max_size:
            return jsonify({'error': 'File too large. Maximum size: 200MB'}), 400
        
        # Calculate checksum
        checksum = hashlib.sha256(file_data).hexdigest()
        
        # Get image metadata
        image_metadata = {}
        try:
            image = Image.open(io.BytesIO(file_data))
            image_metadata = {
                'width': image.width,
                'height': image.height,
                'format': image.format
            }
        except Exception as e:
            print(f"Error reading image metadata: {e}")
        
        # Create file record
        file_upload = FileUpload(
            filename=secure_filename(file.filename),
            original_filename=file.filename,
            file_size=file_size,
            content_type=file.content_type,
            checksum=checksum,
            **image_metadata
        )
        
        # Generate storage path
        storage_path = f"uploads/{file_upload.id}/{file_upload.filename}"
        
        # Upload to Supabase Storage
        upload_result = storage.upload_file(
            file_path=storage_path,
            file_data=file_data,
            content_type=file.content_type
        )
        
        if upload_result:
            # Get public URL
            public_url = storage.get_public_url(storage_path)
            
            file_upload.storage_path = storage_path
            file_upload.public_url = public_url
            
            # Save to database
            db.session.add(file_upload)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'file': file_upload.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to upload file to storage'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/jobs', methods=['POST'])
def create_job():
    """Create new processing job"""
    data = request.get_json()
    
    if not data or 'file_id' not in data:
        return jsonify({'error': 'file_id is required'}), 400
    
    # Get file upload record
    file_upload = FileUpload.query.get(data['file_id'])
    if not file_upload:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Create job record
        job = Job(
            name=data.get('name', f"HDRI - {file_upload.original_filename}"),
            input_file_id=file_upload.id,
            input_file_name=file_upload.original_filename,
            status='pending'
        )
        
        # Set configuration
        configuration = data.get('configuration', {})
        job.set_configuration(configuration)
        
        # Save to database
        db.session.add(job)
        db.session.commit()
        
        # Submit to processing queue
        if runpod_service.is_available():
            # Use RunPod for processing
            runpod_input = runpod_service.prepare_diffusionlight_input(
                image_url=file_upload.public_url,
                configuration=configuration
            )
            
            runpod_job_id = runpod_service.submit_job(runpod_input)
            
            if runpod_job_id:
                # Start monitoring task
                process_hdri_task.delay(job.id, runpod_job_id)
                job.status = 'processing'
                job.started_at = datetime.utcnow()
                db.session.commit()
            else:
                job.status = 'failed'
                job.error_message = 'Failed to submit job to RunPod'
                db.session.commit()
        else:
            # Use local/mock processing
            process_hdri_task.delay(job.id)
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'job': job.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create job: {str(e)}'}), 500

@api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict())

@api_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List jobs with pagination"""
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    jobs = Job.query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify([job.to_dict() for job in jobs])

@api_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.status not in ['pending', 'processing']:
        return jsonify({'error': 'Job cannot be cancelled'}), 400
    
    try:
        # Cancel on RunPod if applicable
        if runpod_service.is_available():
            # Note: Would need to store RunPod job ID to cancel
            pass
        
        job.status = 'cancelled'
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel job: {str(e)}'}), 500

@api_bp.route('/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get job results"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    result_files = job.get_result_files()
    
    return jsonify({
        'job_id': job.id,
        'status': job.status,
        'files': result_files,
        'metadata': {
            'processing_time': job.processing_time,
            'configuration': job.get_configuration(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }
    })

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        # Job statistics
        total_jobs = Job.query.count()
        completed_jobs = Job.query.filter_by(status='completed').count()
        processing_jobs = Job.query.filter_by(status='processing').count()
        failed_jobs = Job.query.filter_by(status='failed').count()
        
        # Calculate success rate
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Average processing time
        avg_processing_time = db.session.query(db.func.avg(Job.processing_time)).filter(
            Job.status == 'completed',
            Job.processing_time.isnot(None)
        ).scalar() or 0
        
        # File statistics
        total_files = FileUpload.query.count()
        total_storage_size = db.session.query(db.func.sum(FileUpload.file_size)).scalar() or 0
        
        return jsonify({
            'jobs': {
                'total': total_jobs,
                'completed': completed_jobs,
                'processing': processing_jobs,
                'failed': failed_jobs,
                'success_rate': round(success_rate, 1),
                'avg_processing_time': round(avg_processing_time, 1)
            },
            'files': {
                'total': total_files,
                'total_size_mb': round(total_storage_size / 1024 / 1024, 2)
            },
            'services': {
                'runpod_available': runpod_service.is_available(),
                'storage_available': storage.client is not None
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@api_bp.route('/files/<file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download file from storage"""
    file_upload = FileUpload.query.get(file_id)
    if not file_upload:
        return jsonify({'error': 'File not found'}), 404
    
    if file_upload.public_url:
        return jsonify({
            'download_url': file_upload.public_url,
            'filename': file_upload.filename
        })
    else:
        return jsonify({'error': 'File not available for download'}), 404

