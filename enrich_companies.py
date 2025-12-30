"""
Company Data Enrichment - Phase 2
Visits company pages directly to extract employee count
"""

import json
import asyncio
from playwright.async_api import async_playwright
import re


async def enrich_company_data(job):
    """Visit company LinkedIn page and extract employee count"""
    
    company_url = job.get('company_linkedin_url')
    
    if not company_url or company_url == 'Unknown':
        return job
    
    # Ensure we're visiting the /about/ page
    if not company_url.endswith('/'):
        company_url += '/'
    about_url = company_url + 'about/'
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(about_url, wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(3)
            
            # Try multiple selectors for employee count
            page_content = await page.content()
            
            # Pattern 1: Look for "X-Y employees" or "X employees"
            patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*employees',
                r'(\d{1,3}(?:,\d{3})*)\s*employees',
                r'Company size[:\s•]+(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 1 and match.group(2):
                        employee_count = f"{match.group(1)}-{match.group(2)} employees"
                    else:
                        employee_count = f"{match.group(1)} employees"
                    
                    job['employee_count'] = employee_count
                    
                    # Estimate revenue based on employee count
                    job['company_revenue_range'] = estimate_revenue(employee_count)
                    
                    print(f"   ✓ {job['company_name']}: {employee_count}")
                    break
            
            await browser.close()
            
    except Exception as e:
        print(f"   ✗ Failed for {job['company_name']}: {str(e)[:80]}")
    
    return job


def estimate_revenue(employee_count_str):
    """Estimate SaaS revenue based on employee count"""
    
    if not employee_count_str or 'Unknown' in employee_count_str:
        return 'Unknown'
    
    # Extract the lower bound number
    match = re.search(r'(\d+(?:,\d+)?)', employee_count_str.replace(',', ''))
    if not match:
        return 'Unknown'
    
    count = int(match.group(1))
    
    # SaaS revenue-per-employee multiples (conservative estimates)
    if count < 50:
        return '$1M - $10M'
    elif count < 100:
        return '$10M - $30M'
    elif count < 200:
        return '$30M - $75M'
    elif count < 500:
        return '$75M - $200M'
    elif count < 1000:
        return '$200M - $500M'
    elif count < 2000:
        return '$500M - $1B'
    else:
        return '$1B+'


async def main():
    print("="*60)
    print("COMPANY DATA ENRICHMENT - EMPLOYEE COUNT EXTRACTION")
    print("="*60)
    
    # Load enriched jobs
    input_file = "output/jobs_raw_20251230_112529_enriched_v2.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print(f"\n📂 Loaded {len(jobs)} jobs")
    print("🔍 Extracting employee counts from company pages...\n")
    
    enriched_jobs = []
    
    for i, job in enumerate(jobs):
        print(f"[{i+1}/{len(jobs)}] {job['company_name']}")
        enriched = await enrich_company_data(job)
        enriched_jobs.append(enriched)
        await asyncio.sleep(4)  # Rate limit: 4 seconds between requests
    
    # Save final enriched data
    output_file = input_file.replace('_v2.json', '_v3_final.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {output_file}")
    
    # Also update Excel
    try:
        import pandas as pd
        
        df = pd.DataFrame(enriched_jobs)
        
        # Convert tech_stack to string
        if 'tech_stack' in df.columns:
            df['tech_stack'] = df['tech_stack'].apply(lambda x: ', '.join(x) if x else '')
        
        excel_file = output_file.replace('.json', '.xlsx')
        df.to_excel(excel_file, index=False, sheet_name='Final Enriched')
        
        print(f"✅ Excel saved to: {excel_file}")
        
    except Exception as e:
        print(f"⚠️  Excel export failed: {e}")
    
    print("\n" + "="*60)
    print("ENRICHMENT COMPLETE - FINAL VERSION READY")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())