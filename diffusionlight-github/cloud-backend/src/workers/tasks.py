import os
import time
from datetime import datetime
from celery import Celery
from src.config.database import db, get_supabase_client
from src.models.job import Job
from src.services.runpod_service import get_runpod_service

# Initialize Celery
celery_app = Celery('diffusionlight')
celery_app.config_from_object('src.workers.celery_config')

# Initialize services
runpod_service = get_runpod_service()

@celery_app.task(bind=True)
def process_hdri_task(self, job_id, runpod_job_id=None):
    """Process HDRI generation task"""
    
    # Import here to avoid circular imports
    from src.main import app
    
    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            return {'error': 'Job not found'}
        
        try:
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            job.progress = 10
            db.session.commit()
            
            if runpod_job_id and runpod_service.is_available():
                # Process with RunPod
                result = process_with_runpod(job, runpod_job_id, self)
            else:
                # Process with mock/local
                result = process_with_mock(job, self)
            
            if result['success']:
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                job.processing_time = (job.completed_at - job.started_at).total_seconds()
                job.progress = 100
                job.set_result_files(result['files'])
            else:
                job.status = 'failed'
                job.error_message = result.get('error', 'Unknown error')
                job.completed_at = datetime.utcnow()
            
            db.session.commit()
            return result
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            return {'error': str(e)}

def process_with_runpod(job, runpod_job_id, task):
    """Process job using RunPod"""
    try:
        # Monitor RunPod job progress
        start_time = time.time()
        timeout = 600  # 10 minutes timeout
        
        while time.time() - start_time < timeout:
            # Update progress
            elapsed = time.time() - start_time
            progress = min(10 + int(elapsed / timeout * 80), 90)
            
            job.progress = progress
            db.session.commit()
            
            # Check RunPod status
            status = runpod_service.get_job_status(runpod_job_id)
            
            if not status:
                time.sleep(5)
                continue
            
            runpod_status = status.get('status')
            
            if runpod_status == 'COMPLETED':
                # Process completed successfully
                output = status.get('output', {})
                result_urls = output.get('result_urls', [])
                
                # Download and store results
                result_files = []
                for i, url in enumerate(result_urls):
                    file_info = download_and_store_result(url, job.id, f"result_{i}")
                    if file_info:
                        result_files.append(file_info)
                
                return {
                    'success': True,
                    'files': result_files,
                    'metadata': output.get('metadata', {})
                }
                
            elif runpod_status in ['FAILED', 'CANCELLED']:
                error_msg = status.get('error', 'RunPod job failed')
                return {'success': False, 'error': error_msg}
            
            time.sleep(5)
        
        # Timeout
        return {'success': False, 'error': 'Processing timeout'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_with_mock(job, task):
    """Process job with mock/local processing"""
    try:
        # Simulate processing steps
        steps = [
            ("Validating input image", 20),
            ("Detecting chrome ball", 40),
            ("Converting to environment map", 60),
            ("Applying tone mapping", 80),
            ("Generating HDR file", 95),
            ("Finalizing output", 100)
        ]
        
        for step_name, progress in steps:
            job.progress = progress
            db.session.commit()
            
            # Simulate processing time
            time.sleep(2)
        
        # Generate mock result files
        config = job.get_configuration()
        output_format = config.get('output_format', 'hdr')
        resolution = config.get('resolution', 1024)
        
        result_files = [
            {
                'filename': f'result_{job.id}.{output_format}',
                'size': 1024 * 1024 * 5,  # 5MB mock size
                'download_url': f'/api/files/{job.id}/download',
                'type': 'hdri',
                'format': output_format,
                'resolution': f'{resolution}x{resolution//2}'
            }
        ]
        
        # Add preview if available
        if output_format in ['hdr', 'exr']:
            result_files.append({
                'filename': f'preview_{job.id}.jpg',
                'size': 1024 * 512,  # 512KB mock size
                'download_url': f'/api/files/{job.id}/preview',
                'type': 'preview',
                'format': 'jpg',
                'resolution': '512x256'
            })
        
        return {
            'success': True,
            'files': result_files,
            'metadata': {
                'processing_method': 'mock',
                'configuration': config
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def download_and_store_result(url, job_id, filename_prefix):
    """Download result file from URL and store in Supabase"""
    try:
        import requests
        from src.config.database import SupabaseStorage
        
        storage = SupabaseStorage()
        
        # Download file
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        file_data = response.content
        file_size = len(file_data)
        
        # Determine file extension from URL or content type
        content_type = response.headers.get('content-type', '')
        if 'hdr' in url.lower() or 'radiance' in content_type:
            ext = 'hdr'
        elif 'exr' in url.lower() or 'openexr' in content_type:
            ext = 'exr'
        elif 'jpg' in url.lower() or 'jpeg' in content_type:
            ext = 'jpg'
        else:
            ext = 'bin'
        
        filename = f"{filename_prefix}_{job_id}.{ext}"
        storage_path = f"results/{job_id}/{filename}"
        
        # Upload to Supabase Storage
        upload_result = storage.upload_file(
            file_path=storage_path,
            file_data=file_data,
            content_type=content_type
        )
        
        if upload_result:
            public_url = storage.get_public_url(storage_path)
            
            return {
                'filename': filename,
                'size': file_size,
                'download_url': public_url,
                'storage_path': storage_path,
                'type': 'result',
                'format': ext
            }
        
        return None
        
    except Exception as e:
        print(f"Error downloading and storing result: {e}")
        return None

@celery_app.task
def cleanup_old_files():
    """Cleanup old files from storage"""
    try:
        from datetime import timedelta
        from src.config.database import SupabaseStorage
        
        # Delete files older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_jobs = Job.query.filter(
            Job.completed_at < cutoff_date,
            Job.status.in_(['completed', 'failed'])
        ).all()
        
        storage = SupabaseStorage()
        deleted_count = 0
        
        for job in old_jobs:
            result_files = job.get_result_files()
            
            for file_info in result_files:
                storage_path = file_info.get('storage_path')
                if storage_path:
                    if storage.delete_file(storage_path):
                        deleted_count += 1
            
            # Clear result files from job
            job.set_result_files([])
            db.session.commit()
        
        return {'deleted_files': deleted_count}
        
    except Exception as e:
        return {'error': str(e)}

@celery_app.task
def health_check_task():
    """Health check task for monitoring"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'worker_id': os.getenv('HOSTNAME', 'unknown')
    }

