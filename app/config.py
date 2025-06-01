import os

class Config:
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh' # Hoặc múi giờ phù hợp
    CELERY_ENABLE_UTC = False # Set False nếu timezone không phải UTC

    # URL của Laravel CMS API để gửi dữ liệu đã crawl
    CMS_API_BASE_URL = os.environ.get('CMS_API_BASE_URL', 'http://cms_app:8000/api')
    # Thêm các cấu hình khác như API keys nếu cần