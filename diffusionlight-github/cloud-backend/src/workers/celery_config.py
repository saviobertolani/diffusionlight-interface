import os
from dotenv import load_dotenv

load_dotenv()

# Celery Configuration
broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task routing
task_routes = {
    'src.workers.tasks.process_hdri_task': {'queue': 'hdri_processing'},
    'src.workers.tasks.cleanup_old_files': {'queue': 'maintenance'},
    'src.workers.tasks.health_check_task': {'queue': 'monitoring'},
}

# Worker settings
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000

# Task time limits
task_soft_time_limit = 600  # 10 minutes
task_time_limit = 900       # 15 minutes

# Retry settings
task_default_retry_delay = 60
task_max_retries = 3

# Beat schedule for periodic tasks
beat_schedule = {
    'cleanup-old-files': {
        'task': 'src.workers.tasks.cleanup_old_files',
        'schedule': 86400.0,  # Run daily
    },
    'health-check': {
        'task': 'src.workers.tasks.health_check_task',
        'schedule': 300.0,    # Run every 5 minutes
    },
}

