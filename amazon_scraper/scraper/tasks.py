# scraper/tasks.py

from celery import shared_task
from .scraper import save_products_to_db
from .models import Brand

@shared_task
def scrape_products_for_brands():
    for brand in Brand.objects.all():
        save_products_to_db(brand.name)
