# scraper/scraper.py

import requests
from bs4 import BeautifulSoup
from .models import Product, Brand
from django.utils.timezone import now
import random
import time
import logging
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# List of user-agents to rotate
HEADERS = [
    {"accept-language": "en-US,en;q=0.9", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
    {"accept-language": "en-GB,en;q=0.5", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"accept-language": "en-US,en;q=0.9", "accept-encoding": "gzip, deflate", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"},
    {"accept-language": "en-US,en;q=0.9", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"accept-language": "en-US,en;q=0.9", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8"},
    {"accept-language": "en-CA,en;q=0.9", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8"},
]

# List of proxy servers (replace with your actual proxies)
PROXIES = [
    "http://proxy1:port",
    "http://proxy2:port",
    "http://proxy3:port",
]

def get_random_headers():
    return random.choice(HEADERS)

def get_random_proxy():
    return {"http": random.choice(PROXIES), "https": random.choice(PROXIES)}

def scrape_amazon_products(brand_name):
    products_data = []
    page = 1
    max_pages = 20
    logger.debug(f"Scraping Amazon for brand {brand_name}")
    while page <= max_pages:
        url = f"https://www.amazon.com/s?k={brand_name.replace(' ', '+')}&page={page}"
        attempts = 3  # Number of attempts to handle CAPTCHA or other issues

        for attempt in range(attempts):
            try:
                headers = get_random_headers()
                response = requests.get(url, headers=headers, timeout=10)
                logger.debug(f"Scraping page {page} for brand {brand_name}")
                logger.debug(f"Response status code: {response.content}")    
                
                # Check if CAPTCHA or rate limiting occurred
                if "captcha" in response.url or response.status_code == 429:
                    logger.warning("Captcha or rate limit hit; retrying...")
                    time.sleep(random.uniform(5, 10))  # Pause before retrying
                    continue  # Retry the request

                # Parse response with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                products_found = False
                # Extract product information
                for product in soup.select('.s-result-item'):
                    name = product.select_one('.a-text-normal')
                    asin = product.get('data-asin')
                    image = product.select_one('.s-image')

                    if name and asin and image:
                        products_data.append({
                            'name': name.get_text().strip(),
                            'asin': asin,
                            'image_url': image['src'],
                            'sku': None  # SKU might not always be available
                        })

                # Random delay to reduce detection
                time.sleep(random.uniform(2, 5))

                # If no products were found on this page, we assume we’ve reached the end
                if not products_found:
                    logger.error("No more products found, stopping pagination.")
                    return products_data

                break  # Exit retry loop on successful request

            except requests.exceptions.RequestException as e:
                logger.error(f"Error occurred: {e}")
                time.sleep(random.uniform(5, 10))  # Delay before retrying

        # Move to the next page
        page += 1

    print(f"Scraped a total of {len(products_data)} products.")
    return products_data

def save_products_to_db(brand_name):
    brand, created = Brand.objects.get_or_create(name=brand_name)
    logger.debug(f"Started updating products for brand {brand_name}")
    products = scrape_amazon_products(brand_name)
    print(products)
    for product_data in products:
        product, created = Product.objects.update_or_create(
            asin=product_data['asin'],
            defaults={
                'name': product_data['name'],
                'image_url': product_data['image_url'],
                'brand': brand,
                'updated_at': now(),
            }
        )

    logger.info(f"Finished updating products for brand {brand_name}")
