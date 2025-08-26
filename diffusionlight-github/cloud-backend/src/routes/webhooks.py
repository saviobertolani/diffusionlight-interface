import os
import hmac
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from src.config.database import db
from src.models.job import Job

webhooks_bp = Blueprint('webhooks', __name__)

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature for security"""
    secret = os.getenv('WEBHOOK_SECRET', 'default-secret')
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@webhooks_bp.route('/runpod', methods=['POST'])
def runpod_webhook():
    """Handle RunPod webhook notifications"""
    try:
        # Verify signature if provided
        signature = request.headers.get('X-Signature')
        if signature:
            if not verify_webhook_signature(request.data, signature):
                return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract job information
        runpod_job_id = data.get('id')
        status = data.get('status')
        output = data.get('output', {})
        error = data.get('error')
        
        if not runpod_job_id:
            return jsonify({'error': 'No job ID provided'}), 400
        
        # Find corresponding job in database
        # Note: We need to store RunPod job ID in our Job model
        job = Job.query.filter_by(external_job_id=runpod_job_id).first()
        
        if not job:
            current_app.logger.warning(f"Received webhook for unknown job: {runpod_job_id}")
            return jsonify({'message': 'Job not found, but webhook received'}), 200
        
        # Update job based on RunPod status
        if status == 'COMPLETED':
            handle_completed_job(job, output)
        elif status == 'FAILED':
            handle_failed_job(job, error)
        elif status == 'IN_PROGRESS':
            handle_progress_update(job, data)
        elif status == 'CANCELLED':
            handle_cancelled_job(job)
        
        db.session.commit()
        
        return jsonify({'message': 'Webhook processed successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Webhook processing error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_completed_job(job: Job, output: dict):
    """Handle completed job webhook"""
    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    job.progress = 100
    
    if job.started_at:
        job.processing_time = (job.completed_at - job.started_at).total_seconds()
    
    # Process output files
    result_files = []
    
    # Extract result URLs from output
    if 'images' in output:
        for i, image_info in enumerate(output['images']):
            if isinstance(image_info, dict):
                url = image_info.get('url')
                filename = image_info.get('filename', f'result_{i}.hdr')
            else:
                url = image_info
                filename = f'result_{i}.hdr'
            
            if url:
                result_files.append({
                    'filename': filename,
                    'download_url': url,
                    'type': 'result',
                    'format': filename.split('.')[-1] if '.' in filename else 'hdr'
                })
    
    # Extract metadata
    metadata = output.get('metadata', {})
    if metadata:
        result_files.append({
            'filename': 'metadata.json',
            'content': metadata,
            'type': 'metadata',
            'format': 'json'
        })
    
    job.set_result_files(result_files)
    
    current_app.logger.info(f"Job {job.id} completed successfully")

def handle_failed_job(job: Job, error: str):
    """Handle failed job webhook"""
    job.status = 'failed'
    job.completed_at = datetime.utcnow()
    job.error_message = error or 'Job failed on RunPod'
    
    if job.started_at:
        job.processing_time = (job.completed_at - job.started_at).total_seconds()
    
    current_app.logger.error(f"Job {job.id} failed: {error}")

def handle_progress_update(job: Job, data: dict):
    """Handle progress update webhook"""
    if job.status == 'pending':
        job.status = 'processing'
        job.started_at = datetime.utcnow()
    
    # Extract progress information
    progress_info = data.get('progress', {})
    
    if isinstance(progress_info, dict):
        progress = progress_info.get('percentage', job.progress)
        current_step = progress_info.get('current_step', '')
        total_steps = progress_info.get('total_steps', 0)
        
        if isinstance(progress, (int, float)):
            job.progress = min(max(int(progress), 0), 99)  # Keep between 0-99 until completion
    
    current_app.logger.info(f"Job {job.id} progress: {job.progress}%")

def handle_cancelled_job(job: Job):
    """Handle cancelled job webhook"""
    job.status = 'cancelled'
    job.completed_at = datetime.utcnow()
    
    if job.started_at:
        job.processing_time = (job.completed_at - job.started_at).total_seconds()
    
    current_app.logger.info(f"Job {job.id} was cancelled")

@webhooks_bp.route('/test', methods=['POST'])
def test_webhook():
    """Test webhook endpoint for development"""
    data = request.get_json()
    
    current_app.logger.info(f"Test webhook received: {data}")
    
    return jsonify({
        'message': 'Test webhook received',
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@webhooks_bp.route('/health', methods=['GET'])
def webhook_health():
    """Health check for webhook service"""
    return jsonify({
        'status': 'healthy',
        'service': 'webhooks',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

