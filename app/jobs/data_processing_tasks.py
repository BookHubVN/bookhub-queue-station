from app import celery
from app.services.cms_api_client import CmsApiClient

@celery.task
def process_and_store_book_data_task(raw_book_data: dict):
    """
    Task để xử lý dữ liệu sách thô và gửi nó đến Laravel CMS.
    """
    print(f"Processing raw book data: {raw_book_data.get('source_id')}")

    # Bước 1: Làm sạch và chuẩn hóa dữ liệu
    # Đây là nơi bạn thêm logic để làm sạch text, định dạng lại các trường,
    # xử lý giá trị null, v.v.
    processed_data = {
        'source': raw_book_data.get('source'),
        'source_id': raw_book_data.get('source_id'),
        'title': raw_book_data.get('title', '').strip(),
        'author': raw_book_data.get('author', '').strip(),
        'description': raw_book_data.get('description', '').strip(),
        'isbn': raw_book_data.get('isbn'),
        'publisher': raw_book_data.get('publisher'),
        'publication_date': raw_book_data.get('publication_date'),
        'average_rating': raw_book_data.get('average_rating'),
        'num_ratings': raw_book_data.get('num_ratings'),
        'genres': raw_book_data.get('genres', []),
        'cover_image_url': raw_book_data.get('cover_image_url'),
        # Thêm các trường khác cần thiết
    }

    # Ví dụ: Chuẩn hóa rating nếu nó ở định dạng string hoặc sai kiểu
    try:
        processed_data['average_rating'] = float(processed_data['average_rating'])
    except (ValueError, TypeError):
        processed_data['average_rating'] = None

    # Bước 2: Gửi dữ liệu đã xử lý đến CMS
    cms_client = CmsApiClient()
    response = cms_client.send_book_data(processed_data)

    if response and response.status_code < 400: # Kiểm tra mã trạng thái thành công (2xx, 3xx)
        print(f"Successfully processed and sent book {processed_data.get('source_id')} to CMS.")
        return True
    else:
        print(f"Failed to process and send book {processed_data.get('source_id')} to CMS. Status: {response.status_code if response else 'N/A'}")
        return False

@celery.task
def process_and_store_review_data_task(raw_review_data: dict):
    """
    Task để xử lý dữ liệu review thô và gửi nó đến Laravel CMS.
    """
    print(f"Processing raw review data for book {raw_review_data.get('book_source_id')}")

    processed_data = {
        'source': raw_review_data.get('source'),
        'source_id': raw_review_data.get('source_id'), # ID của review từ nguồn gốc
        'book_source_id': raw_review_data.get('book_source_id'), # ID của sách từ nguồn gốc
        'user_name': raw_review_data.get('user_name', 'Anonymous').strip(),
        'rating': raw_review_data.get('rating'),
        'text': raw_review_data.get('text', '').strip(),
        'published_date': raw_review_data.get('published_date'),
        # Thêm các trường khác cần thiết
    }

    # Ví dụ: Chuẩn hóa rating
    try:
        processed_data['rating'] = int(processed_data['rating'])
        if not (1 <= processed_data['rating'] <= 5): # Đảm bảo rating nằm trong khoảng 1-5
            processed_data['rating'] = None
    except (ValueError, TypeError):
        processed_data['rating'] = None

    cms_client = CmsApiClient()
    response = cms_client.send_review_data(processed_data)

    if response and response.status_code < 400:
        print(f"Successfully processed and sent review {processed_data.get('source_id')} to CMS.")
        return True
    else:
        print(f"Failed to process and send review {processed_data.get('source_id')} to CMS. Status: {response.status_code if response else 'N/A'}")
        return False

# Bạn có thể thêm các task khác cho tóm tắt (summaries), trích dẫn (quotes), v.v.
# @celery.task
# def process_and_store_summary_data_task(raw_summary_data: dict):
#     # Logic xử lý và gửi tóm tắt
#     pass