import requests
from app.config import Config

class CmsApiClient:
    def __init__(self):
        self.base_url = Config.CMS_API_BASE_URL
        # Có thể thêm headers cho authentication nếu CMS API cần
        self.headers = {'Content-Type': 'application/json'}

    def send_book_data(self, book_data):
        url = f"{self.base_url}/books/create-from-crawler" # API endpoint để nhận data sách
        try:
            response = requests.post(url, json=book_data, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending book data to CMS: {e}")
            return None

    def send_review_data(self, review_data):
        url = f"{self.base_url}/reviews/create-from-crawler" # API endpoint để nhận data review
        try:
            response = requests.post(url, json=review_data, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending review data to CMS: {e}")
            return None