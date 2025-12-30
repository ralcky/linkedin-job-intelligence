"""
LinkedIn SaaS Jobs Spider - Production Grade 2025
Targets: VP/Director/CTO roles at Series B-D SaaS companies
Anti-detection: Full stealth mode enabled
"""

import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime, timedelta
import json
import re


class SaasJobsSpider(scrapy.Spider):
    name = "saas_jobs"
    
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
        'CONCURRENT_REQUESTS': 1,  # LinkedIn defense: slow and steady
        'DOWNLOAD_DELAY': 8,  # 8 seconds between requests (human-like)
    }
    
    # Target job titles (VP+ only)
    JOB_TITLES = [
        "VP of Engineering",
        "Director of Engineering",
        "Head of Data",
        "Senior Engineering Manager",
        "VP of Product",
        "Director of Product",
        "CTO",
        "Head of Machine Learning",
        "VP of Data",
        "Director of Data Engineering"
    ]
    
    def start_requests(self):
        """Generate LinkedIn job search URLs for each target role"""
        
        base_url = "https://www.linkedin.com/jobs/search/"
        
        # Search params (last 10 days, US only, remote OK)
        for job_title in self.JOB_TITLES:
            params = {
                "keywords": job_title,
                "location": "United States",
                "f_TPR": "r604800",  # Last 7 days (604800 seconds)
                "f_WT": "2",  # Remote jobs included
                "position": 1,
                "pageNum": 0
            }
            
            # Build URL
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}?{query_string}"
            
            self.logger.info(f"🎯 Searching: {job_title}")
            
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "ul.jobs-search__results-list", timeout=30000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 3000),
                    ],
                    "job_title_searched": job_title
                },
                callback=self.parse_job_listings,
                errback=self.errback_close_page,
            )
    
    async def parse_job_listings(self, response):
        """Extract individual job URLs from search results"""
        
        job_cards = response.css("ul.jobs-search__results-list li")
        
        self.logger.info(f"✅ Found {len(job_cards)} job cards for '{response.meta['job_title_searched']}'")
        
        for card in job_cards[:15]:  # Limit to 15 per search to avoid overload
            job_url = card.css("a.base-card__full-link::attr(href)").get()
            
            if job_url:
                # Clean URL
                job_url = job_url.split("?")[0]
                
                yield scrapy.Request(
                    url=job_url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", ".top-card-layout", timeout=20000),
                            PageMethod("wait_for_timeout", 2000),
                        ],
                    },
                    callback=self.parse_job_details,
                    errback=self.errback_close_page,
                )
    
    async def parse_job_details(self, response):
        """Extract all job details from individual job page"""
        
        # Extract job title
        job_title = response.css("h1.top-card-layout__title::text").get()
        if job_title:
            job_title = job_title.strip()
        
        # Extract company name
        company_name = response.css("a.topcard__org-name-link::text").get()
        if not company_name:
            company_name = response.css(".topcard__flavor--black-link::text").get()
        if company_name:
            company_name = company_name.strip()
        
        # Extract location
        location = response.css(".topcard__flavor--bullet::text").get()
        if location:
            location = location.strip()
        
        # Extract posted date
        posted_date_raw = response.css(".topcard__flavor--metadata time::attr(datetime)").get()
        posted_date = self.parse_date(posted_date_raw)
        
        # Extract job description
        description_html = response.css(".description__text").get()
        description_text = response.css(".description__text::text").getall()
        description = " ".join([t.strip() for t in description_text if t.strip()])
        
        # Extract company LinkedIn URL
        company_url = response.css("a.topcard__org-name-link::attr(href)").get()
        
        # Job URL
        job_url = response.url
        
        # Extract applicant count (if visible)
        applicants_raw = response.css(".num-applicants__caption::text").get()
        applicants = self.extract_number(applicants_raw) if applicants_raw else None
        
        self.logger.info(f"📄 Scraped: {job_title} at {company_name}")
        
        yield {
            "job_title": job_title,
            "company_name": company_name,
            "company_linkedin_url": company_url,
            "location": location,
            "posted_date": posted_date,
            "job_url": job_url,
            "description": description[:500] if description else None,  # First 500 chars
            "applicant_count": applicants,
            "scraped_at": datetime.now().isoformat(),
        }
    
    def parse_date(self, date_string):
        """Convert LinkedIn date format to readable format"""
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except:
            return None
    
    def extract_number(self, text):
        """Extract first number from text"""
        if not text:
            return None
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None
    
    async def errback_close_page(self, failure):
        """Handle errors gracefully"""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"❌ Error on {failure.request.url}: {failure.value}")