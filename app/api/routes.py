# bookhub-queue-station/app/api/routes.py
from app.api import bp # Import blueprint từ __init__.py của gói api
from flask import jsonify

@bp.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "API is running"}), 200

# Thêm các route API khác tại đây
# Ví dụ: để kích hoạt một task Celery
# from app.jobs.crawl_tasks import crawl_goodreads_books_task
# @bp.route('/crawl/goodreads/<int:book_id>', methods=['POST'])
# def trigger_goodreads_crawl(book_id):
#     crawl_goodreads_books_task.delay(book_id)
#     return jsonify({"message": f"Crawling task for book {book_id} dispatched."}), 202