import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, List, Dict, Any

class AmazonCrawler:
    """
    Crawler cho trang Amazon để thu thập thông tin sách và reviews.
    Lưu ý: Amazon có các biện pháp chống scraping rất mạnh.
    Để sử dụng hiệu quả, bạn có thể cần:
    - Các HTTP headers phức tạp (User-Agent, Accept-Language, v.v.)
    - Proxy rotations
    - Throttling (giới hạn tốc độ request)
    - Browser automation (Selenium/Playwright) cho các trang có JS động
    - Amazon Product Advertising API (PA-API) là phương pháp chính thức.
    """
    BASE_URL = "https://www.amazon.com"
    # Một số User-Agent phổ biến để tránh bị chặn ngay lập tức
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
    }

    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Thực hiện HTTP request và trả về đối tượng BeautifulSoup."""
        try:
            print(f"Making request to: {url}")
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status() # Ném lỗi cho các mã trạng thái HTTP không thành công (4xx hoặc 5xx)
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None

    def get_book_details_by_asin(self, asin: str) -> Optional[Dict[str, Any]]:
        """
        Thu thập thông tin chi tiết của sách từ Amazon bằng ASIN.
        ASIN (Amazon Standard Identification Number) là định danh duy nhất của sản phẩm Amazon.
        """
        url = f"{self.BASE_URL}/dp/{asin}"
        soup = self._make_request(url)
        if not soup:
            return None

        title = soup.find('span', {'id': 'productTitle'})
        title = title.text.strip() if title else None

        author = soup.find('a', {'data-action': 'contributor-link'})
        author = author.text.strip() if author else None

        # Ví dụ đơn giản để lấy mô tả (có thể phức tạp hơn)
        description = soup.find('div', {'id': 'bookDescription_feature_div'})
        description = description.find('noscript').text.strip() if description and description.find('noscript') else None

        # Lấy giá trị rating trung bình
        avg_rating_span = soup.find('span', {'data-hook': 'rating-out-of-text'})
        avg_rating = float(avg_rating_span.text.split(' ')[0]) if avg_rating_span else None

        # Lấy số lượng ratings
        num_ratings_span = soup.find('span', {'id': 'acrCustomerReviewText'})
        num_ratings = int(re.sub(r'[^0-9]', '', num_ratings_span.text)) if num_ratings_span else None

        # Cố gắng lấy ISBN (thường nằm trong Product details)
        isbn = None
        detail_bullets = soup.find('div', {'id': 'detailBullets_feature_div'})
        if detail_bullets:
            isbn_li = detail_bullets.find('li', string=re.compile(r'ISBN-10|ISBN-13'))
            if isbn_li:
                isbn = isbn_li.text.strip().split(':')[-1].strip()

        # Thêm các trường khác như nhà xuất bản, ngày xuất bản, hình ảnh bìa...
        cover_image_tag = soup.find('img', {'id': 'imgBlkFront'})
        cover_image_url = cover_image_tag['src'] if cover_image_tag else None


        return {
            'source': 'amazon',
            'source_id': asin, # ASIN làm ID nguồn
            'title': title,
            'author': author,
            'description': description,
            'isbn': isbn,
            'average_rating': avg_rating,
            'num_ratings': num_ratings,
            'cover_image_url': cover_image_url,
            # Các trường khác có thể thêm: publisher, publication_date, language, ...
        }

    def get_reviews(self, asin: str, page_limit: int = 1) -> List[Dict[str, Any]]:
        """
        Thu thập các review của sách từ Amazon bằng ASIN.
        Lưu ý: Amazon thường có các review được tải động (JavaScript).
        Để lấy được hết, có thể cần browser automation hoặc tìm API nội bộ của Amazon.
        """
        reviews = []
        for page in range(1, page_limit + 1):
            # URL cho trang review, có thể khác tùy sản phẩm và Amazon có thể thay đổi
            # Đây là một URL mẫu, bạn cần kiểm tra URL thực tế trên Amazon.
            url = f"{self.BASE_URL}/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_{page}?pageNumber={page}"
            soup = self._make_request(url)
            if not soup:
                break # Dừng nếu request thất bại

            review_elements = soup.find_all('div', {'data-hook': 'review'})
            if not review_elements:
                print(f"No reviews found on page {page} for ASIN {asin}.")
                break # Dừng nếu không còn review nào trên trang này

            for review_el in review_elements:
                review_id = review_el.get('id')
                user_name_tag = review_el.find('span', class_='a-profile-name')
                user_name = user_name_tag.text.strip() if user_name_tag else 'Anonymous'

                rating_tag = review_el.find('span', class_='a-icon-alt')
                rating_text = rating_tag.text.strip() if rating_tag else None
                rating_match = re.search(r'(\d+\.?\d*) out of 5 stars', rating_text) if rating_text else None
                rating = float(rating_match.group(1)) if rating_match else None

                review_text_tag = review_el.find('span', {'data-hook': 'review-body'})
                review_text = review_text_tag.text.strip() if review_text_tag else None

                # Có thể cần tìm cách lấy ngày đăng review
                published_date_tag = review_el.find('span', {'data-hook': 'review-date'})
                published_date = published_date_tag.text.strip() if published_date_tag else None
                # Bạn sẽ cần parse published_date thành định dạng chuẩn (ví dụ: ISO 8601)

                if review_text: # Chỉ thêm review nếu có nội dung
                    reviews.append({
                        'source': 'amazon',
                        'source_id': review_id,
                        'book_source_id': asin,
                        'user_name': user_name,
                        'rating': rating,
                        'text': review_text,
                        'published_date': published_date,
                    })
            print(f"Finished crawling page {page} for ASIN {asin}. Found {len(review_elements)} reviews.")
        return reviews

# Ví dụ về cách sử dụng (chỉ để test nhanh)
if __name__ == '__main__':
    crawler = AmazonCrawler()
    # Bạn có thể tìm một ASIN hợp lệ của sách trên Amazon để thử
    test_asin = "0321765726" # Ví dụ: "The Lord of the Rings" (có thể không chính xác)

    print(f"\n--- Crawling book details for ASIN: {test_asin} ---")
    book_details = crawler.get_book_details_by_asin(test_asin)
    if book_details:
        for key, value in book_details.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to get book details.")

    print(f"\n--- Crawling reviews for ASIN: {test_asin} ---")
    # Cẩn thận khi chạy crawl reviews, Amazon có thể chặn nhanh chóng
    book_reviews = crawler.get_reviews(test_asin, page_limit=1)
    if book_reviews:
        for i, review in enumerate(book_reviews[:3]): # In ra 3 review đầu tiên
            print(f"\n  Review {i+1}:")
            for key, value in review.items():
                print(f"    {key}: {value}")
    else:
        print("Failed to get reviews or no reviews found.")