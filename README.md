# Django Project with Celery and Redis

This is a Django project configured with Celery for background task processing, Redis as the message broker, and Django REST Framework for building RESTful APIs. This README provides steps to set up the environment, install dependencies, configure Redis, and run the Django server and Celery.

## Prerequisites

- Python 3.x
- Redis
- Virtual environment (optional, but recommended)

---

## Table of Contents

- [Installation](#installation)
- [Setting Up Redis](#setting-up-redis)
- [Running the Project](#running-the-project)
- [Celery Commands](#celery-commands)

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone
   cd
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   Copy code
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

# Setting Up Redis

Redis is required as the message broker for Celery. Follow these steps to install and configure Redis on Linux.

**Step 1: Update Package List**

```bash
sudo apt update
```

**Step 2: Install Redis**

```bash
sudo apt install redis-server
```

**Step 3: Run Redis**

```bash
sudo systemctl enable redis
```

**To verify that Redis is running, use:**

```bash
redis-cli
> ping
```

If everything is set up correctly, it should return:

```bash
PONG
```

# Running the Project

**Run Database Migrations**

```bash
python manage.py migrate
```

**Start the Django Development Server**

```bash
python manage.py runserver
```

## Celery Commands

**Running the Celery Worker**

To start a Celery worker, run the following command in a new terminal (make sure Redis is running):

```bash
celery -A amazon_scrapper worker --loglevel=info
```

**Running Celery Beat**

Celery Beat is used for scheduling tasks. In another new terminal, run:

```bash
celery -A amazon_scrapper beat --loglevel=info
```

# Web Scraping Implementation

## Overview

This project uses requests and BeautifulSoup to scrape product data from Amazon for a specified brand. Scraped data includes product name, ASIN, SKU, and image URL. The scraper is set up to:

- Handle pagination on Amazon’s results pages.
- Parse the required data from each result page.
- Handle any CAPTCHA or rate-limit issues.

## Anti-Scraping Measures

To avoid being blocked by Amazon’s anti-scraping mechanisms, we implement:

- Randomized User-Agent rotation: Requests use randomly chosen user-agents to simulate different browsers.
- Randomized delays: Each request has a random delay to reduce detection risk.
- Retry logic: If CAPTCHA or rate limits are encountered, the scraper will retry the request with a delay.

## Key Files

- `scraper.py`: Contains the core scraping logic.
- `tasks.py`: Contains Celery tasks to handle scraping periodically.
- `celery.py`: Initializes Celery and configures periodic tasks.

## Assumptions and Design Decisions

1.  **Scraping Frequency:**

    - Tasks are set to run four times a day to update product information regularly.
    - The interval can be adjusted in the Django Admin under Periodic Tasks.

2.  **Data Storage:**

    - Product information is stored in a Django model, with fields for name, ASIN, SKU, image URL, and a foreign key to the associated brand.
    - If a product already exists in the database, the scraper updates its information.

3.  **Pagination Handling:**

    - The scraper iterates through search result pages for each brand until no further products are found or a maximum number of pages is reached.

4.  **Error Handling:**

    - We assume that network errors, CAPTCHA, and rate limits might occur during scraping. The scraper retries failed requests and logs errors if all attempts fail.

5.  **Celery and Redis Setup:**
    - We assume Redis is running locally. Redis is used for both Celery's broker and result backend, but these settings can be modified if another broker is preferred.
