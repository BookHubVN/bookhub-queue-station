# Sử dụng base image Python chính thức
FROM python:3.10-slim-buster

# Cài đặt các thư viện hệ thống cần thiết (nếu có, ví dụ git, hoặc build tools cho một số lib Python)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt trước để tận dụng cache của Docker layer
COPY requirements.txt .

# Cài đặt các dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code ứng dụng
COPY . .

# Thiết lập biến môi trường (sẽ được ghi đè bởi docker-compose.yml trong dev)
ENV FLASK_APP=manage.py
ENV FLASK_DEBUG=0 # Production setting
ENV CELERY_BROKER_URL="redis://localhost:6379/0" # Default, overridden by compose
ENV CELERY_RESULT_BACKEND="redis://localhost:6379/0" # Default, overridden by compose
ENV CMS_API_BASE_URL="http://localhost:8000/api" # Default, overridden by compose

# Không cần EXPOSE một cổng cụ thể nếu đây là worker chạy nền.
# Nếu bạn muốn có API Flask để kích hoạt job, thì EXPOSE một cổng.
# EXPOSE 5000 # Nếu có Flask API server

# Command mặc định khi container chạy (chạy Celery worker)
# Để chạy Celery worker:
CMD ["celery", "-A", "app.jobs.crawl_tasks", "worker", "--loglevel=info"]

# Để chạy Celery Beat (lập lịch):
# CMD ["celery", "-A", "app.jobs.crawl_tasks", "beat", "--loglevel=info"]

# Nếu muốn chạy Flask API (thường chỉ dùng để kích hoạt job)
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]