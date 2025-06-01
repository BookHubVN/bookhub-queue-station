# bookhub-queue-station/app/api/__init__.py
from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

# Import các route từ module routes.py để chúng được đăng ký vào blueprint này
from app.api import routes