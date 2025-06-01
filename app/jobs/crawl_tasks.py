from app import celery
from app.crawlers.goodreads import GoodreadsCrawler
from app.services.cms_api_client import CmsApiClient

@celery.task
def crawl_goodreads_books_task(book_id):
    """
    Task để crawl thông tin sách từ Goodreads và gửi về CMS.
    """
    crawler = GoodreadsCrawler()
    cms_client = CmsApiClient()

    book_data = crawler.get_book_details(book_id)
    if book_data:
        response = cms_client.send_book_data(book_data)
        if response and response.status_code == 200:
            print(f"Successfully sent book {book_id} to CMS.")
        else:
            print(f"Failed to send book {book_id} to CMS. Status: {response.status_code if response else 'N/A'}")
    else:
        print(f"Failed to crawl book {book_id} from Goodreads.")

@celery.task
def crawl_goodreads_reviews_task(book_slug, page_limit=10):
    """
    Task để crawl reviews từ Goodreads và gửi về CMS.
    """
    crawler = GoodreadsCrawler()
    cms_client = CmsApiClient()

    reviews = crawler.get_reviews(book_slug, page_limit)
    if reviews:
        for review in reviews:
            response = cms_client.send_review_data(review)
            if response and response.status_code == 200:
                print(f"Successfully sent review ID {review.get('id')} to CMS.")
            else:
                print(f"Failed to send review ID {review.get('id')} to CMS. Status: {response.status_code if response else 'N/A'}")
    else:
        print(f"No reviews crawled for {book_slug}.")

# Ví dụ lập lịch chạy định kỳ (sử dụng Celery Beat)
# celery.conf.beat_schedule = {
#     'crawl-daily-new-books': {
#         'task': 'app.jobs.crawl_tasks.crawl_goodreads_books_task',
#         'schedule': timedelta(days=1),
#         'args': (12345,) # Ví dụ book ID
#     },
# }