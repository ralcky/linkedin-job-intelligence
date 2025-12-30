"""
LinkedIn SaaS Jobs Scraper - SCALED VERSION
Targets 100+ VP/Director jobs across multiple searches
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time


class LinkedInJobScraperScaled:
    
    # EXPANDED JOB TITLE LIST (20 searches instead of 5)
    JOB_TITLES = [
        # Engineering Leadership
        "VP of Engineering",
        "VP Engineering",
        "Director of Engineering",
        "Head of Engineering",
        "SVP Engineering",
        "Chief Technology Officer",
        "CTO",
        "VP of Software Engineering",
        
        # Product Leadership  
        "VP of Product",
        "VP Product Management",
        "Director of Product",
        "Head of Product",
        "Chief Product Officer",
        
        # Data Leadership
        "VP of Data",
        "Head of Data",
        "Director of Data Science",
        "VP Data Engineering",
        "Chief Data Officer",
        
        # Platform/Infrastructure
        "VP of Platform",
        "VP Infrastructure",
    ]
    
    def __init__(self):
        self.jobs = []
        self.seen_urls = set()  # Deduplicate
        
    async def scrape_jobs(self):
        """Main scraping function - scaled version"""
        
        async with async_playwright() as p:
            print("🚀 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,  # Run in background
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage"
                ]
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            for job_title in self.JOB_TITLES:
                print(f"\n🎯 Searching: {job_title}")
                await self.search_and_extract(page, job_title)
                await asyncio.sleep(3)  # Rate limiting
            
            await browser.close()
            
        # Remove duplicates
        unique_jobs = self.deduplicate_jobs()
        
        print(f"\n✅ Total unique jobs scraped: {len(unique_jobs)}")
        self.save_to_json(unique_jobs)
    
    async def search_and_extract(self, page, job_title):
        """Search LinkedIn and extract job listings"""
        
        # Build search URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}&location=United%20States&f_TPR=r604800"
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Wait for results
            await page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)
            
            # Get job cards
            job_cards = await page.query_selector_all("ul.jobs-search__results-list li")
            
            print(f"   Found {len(job_cards)} listings")
            
            # Extract from ALL cards (not just first 10)
            for i, card in enumerate(job_cards):
                try:
                    job_data = await self.extract_job_card(card)
                    if job_data and job_data['job_url'] not in self.seen_urls:
                        self.jobs.append(job_data)
                        self.seen_urls.add(job_data['job_url'])
                        print(f"   ✓ [{i+1}] {job_data['job_title']} at {job_data['company_name']}")
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    async def extract_job_card(self, card):
        """Extract data from a single job card"""
        
        # Job title
        title_elem = await card.query_selector("h3.base-search-card__title")
        job_title = await title_elem.inner_text() if title_elem else None
        
        # Company name
        company_elem = await card.query_selector("h4.base-search-card__subtitle")
        company_name = await company_elem.inner_text() if company_elem else None
        
        # Location
        location_elem = await card.query_selector("span.job-search-card__location")
        location = await location_elem.inner_text() if location_elem else None
        
        # Job URL
        link_elem = await card.query_selector("a.base-card__full-link")
        job_url = await link_elem.get_attribute("href") if link_elem else None
        if job_url:
            job_url = job_url.split("?")[0]
        
        # Posted date
        time_elem = await card.query_selector("time")
        posted_date = await time_elem.get_attribute("datetime") if time_elem else None
        
        # Skip if essential data missing
        if not job_title or not company_name or not job_url:
            return None
        
        # Skip if has masked data
        if '*' in job_title or '*' in company_name:
            return None
            
        return {
            "job_title": job_title.strip(),
            "company_name": company_name.strip(),
            "location": location.strip() if location else "Not specified",
            "job_url": job_url,
            "posted_date": posted_date,
            "scraped_at": datetime.now().isoformat()
        }
    
    def deduplicate_jobs(self):
        """Remove duplicate jobs by URL"""
        seen = set()
        unique = []
        
        for job in self.jobs:
            if job['job_url'] not in seen:
                seen.add(job['job_url'])
                unique.append(job)
        
        return unique
    
    def save_to_json(self, jobs):
        """Save scraped jobs to JSON file"""
        
        filename = f"output/jobs_SCALED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved to: {filename}")


async def main():
    print("="*60)
    print("LINKEDIN JOBS SCRAPER - SCALED PRODUCTION VERSION")
    print("Targeting 100+ VP/Director positions")
    print("="*60)
    
    scraper = LinkedInJobScraperScaled()
    await scraper.scrape_jobs()
    
    print("\n" + "="*60)
    print("SCRAPING COMPLETE - PROCEED TO ENRICHMENT")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())