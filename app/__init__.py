from flask import Flask
from celery import Celery
from app.config import Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Cấu hình Celery để sử dụng context của Flask
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    from app.api import routes
    app.register_blueprint(routes.bp) # Đăng ký Blueprint nếu có API

    return app