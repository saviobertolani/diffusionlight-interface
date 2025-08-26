import os
import requests
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class RunPodService:
    """Service for integrating with RunPod for GPU processing"""
    
    def __init__(self):
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        self.base_url = "https://api.runpod.ai/v2"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def is_available(self) -> bool:
        """Check if RunPod service is available"""
        return bool(self.api_key and self.endpoint_id)
    
    def submit_job(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Submit a job to RunPod endpoint"""
        if not self.is_available():
            raise Exception("RunPod service not configured")
        
        url = f"{self.base_url}/{self.endpoint_id}/run"
        
        payload = {
            "input": input_data
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get('id')
            
        except requests.exceptions.RequestException as e:
            print(f"Error submitting job to RunPod: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from RunPod"""
        if not self.is_available():
            return None
        
        url = f"{self.base_url}/{self.endpoint_id}/status/{job_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting job status from RunPod: {e}")
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job on RunPod"""
        if not self.is_available():
            return False
        
        url = f"{self.base_url}/{self.endpoint_id}/cancel/{job_id}"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error canceling job on RunPod: {e}")
            return False
    
    def wait_for_completion(self, job_id: str, timeout: int = 600, poll_interval: int = 5) -> Optional[Dict[str, Any]]:
        """Wait for job completion with polling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if not status:
                return None
            
            job_status = status.get('status')
            
            if job_status == 'COMPLETED':
                return status
            elif job_status in ['FAILED', 'CANCELLED']:
                return status
            
            time.sleep(poll_interval)
        
        return None  # Timeout
    
    def prepare_diffusionlight_input(self, image_url: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for DiffusionLight processing"""
        return {
            "workflow_type": "diffusionlight",
            "input_image_url": image_url,
            "configuration": {
                "resolution": configuration.get('resolution', 1024),
                "output_format": configuration.get('output_format', 'hdr'),
                "anti_aliasing": configuration.get('anti_aliasing', '4'),
                "preset": configuration.get('preset', 'automotivo')
            },
            "output_settings": {
                "return_urls": True,
                "webhook_url": os.getenv('WEBHOOK_URL')  # For async notifications
            }
        }

class MockRunPodService:
    """Mock service for development/testing"""
    
    def __init__(self):
        self.jobs = {}
    
    def is_available(self) -> bool:
        return True
    
    def submit_job(self, input_data: Dict[str, Any]) -> str:
        """Submit a mock job"""
        import uuid
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            'id': job_id,
            'status': 'IN_QUEUE',
            'input': input_data,
            'created_at': time.time()
        }
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get mock job status with simulated progression"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        elapsed = time.time() - job['created_at']
        
        # Simulate job progression
        if elapsed < 10:
            status = 'IN_QUEUE'
        elif elapsed < 30:
            status = 'IN_PROGRESS'
        else:
            status = 'COMPLETED'
            # Add mock output
            job['output'] = {
                'result_urls': [
                    'https://example.com/result.hdr',
                    'https://example.com/preview.jpg'
                ],
                'metadata': {
                    'processing_time': elapsed,
                    'resolution': job['input']['configuration']['resolution'],
                    'format': job['input']['configuration']['output_format']
                }
            }
        
        job['status'] = status
        return job
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel mock job"""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'CANCELLED'
            return True
        return False
    
    def wait_for_completion(self, job_id: str, timeout: int = 600, poll_interval: int = 5) -> Optional[Dict[str, Any]]:
        """Wait for mock job completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if not status:
                return None
            
            job_status = status.get('status')
            
            if job_status in ['COMPLETED', 'FAILED', 'CANCELLED']:
                return status
            
            time.sleep(poll_interval)
        
        return None
    
    def prepare_diffusionlight_input(self, image_url: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare mock input data"""
        return {
            "workflow_type": "diffusionlight",
            "input_image_url": image_url,
            "configuration": configuration
        }

def get_runpod_service():
    """Get RunPod service instance (real or mock)"""
    if os.getenv('RUNPOD_ENABLED', 'false').lower() == 'true':
        return RunPodService()
    else:
        return MockRunPodService()

