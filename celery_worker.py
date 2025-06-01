from app import create_app, celery

app = create_app()
# Dòng này cần thiết để Celery có thể tìm thấy các task
# from app.jobs import crawl_tasks, data_processing_tasks