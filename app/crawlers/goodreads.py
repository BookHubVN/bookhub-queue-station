import requests
from bs4 import BeautifulSoup

class GoodreadsCrawler:
    BASE_URL = "https://www.goodreads.com"

    def get_book_details(self, book_id):
        url = f"{self.BASE_URL}/book/show/{book_id}"
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract basic book info (simplified)
            title = soup.find('h1', class_='Text__title1').text.strip() if soup.find('h1', class_='Text__title1') else None
            author = soup.find('span', class_='ContributorLink__name').text.strip() if soup.find('span', class_='ContributorLink__name') else None
            description = soup.find('div', class_='BookPageMetadataSection__description').find('span', class_='Formatted').text.strip() if soup.find('div', class_='BookPageMetadataSection__description') else None

            return {
                'source': 'goodreads',
                'source_id': book_id,
                'title': title,
                'author': author,
                'description': description,
                # Thêm logic trích xuất tóm tắt/quotes
            }
        except requests.exceptions.RequestException as e:
            print(f"Error crawling book {book_id}: {e}")
            return None

    def get_reviews(self, book_slug, page_limit=1):
        # Đây là ví dụ phức tạp hơn, có thể cần tìm hiểu cấu trúc URL review hoặc dùng API nếu có
        # Đối với crawl review, thường cần xử lý phân trang và tránh bị chặn.
        print(f"Crawling reviews for {book_slug} (page limit: {page_limit})...")
        reviews = []
        for page in range(1, page_limit + 1):
            url = f"{self.BASE_URL}/book/show/{book_slug}/reviews?page={page}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                # Logic để parse từng review trên trang
                # Ví dụ:
                # review_elements = soup.find_all('div', class_='ReviewCard')
                # for el in review_elements:
                #     review_text = el.find('div', class_='ReviewCard__content').text.strip()
                #     rating = el.find('span', class_='RatingStars__small').get('aria-label')
                #     reviews.append({'book_slug': book_slug, 'text': review_text, 'rating': rating, 'page': page})
            except requests.exceptions.RequestException as e:
                print(f"Error crawling reviews for {book_slug} on page {page}: {e}")
                break # Dừng nếu có lỗi
        return reviews