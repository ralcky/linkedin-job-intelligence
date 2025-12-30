"""
Job Data Enrichment Pipeline v2
Actually extracts real company data from LinkedIn
"""

import json
import time
import re
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright


class JobEnricher:
    
    def __init__(self, input_file):
        self.input_file = input_file
        self.jobs = []
        self.enriched_jobs = []
        
    def load_jobs(self):
        """Load scraped jobs from JSON"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.jobs = json.load(f)
        print(f"📂 Loaded {len(self.jobs)} jobs from {self.input_file}")
    
    async def enrich_all(self):
        """Enrich all jobs with company data"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            for i, job in enumerate(self.jobs):
                print(f"\n[{i+1}/{len(self.jobs)}] Enriching: {job['company_name']}")
                
                enriched = await self.enrich_job(page, job)
                self.enriched_jobs.append(enriched)
                
                await asyncio.sleep(2)
            
            await browser.close()
        
        self.save_enriched()
    
    async def enrich_job(self, page, job):
        """Enrich a single job by visiting the actual job page"""
        
        enriched = job.copy()
        
        enriched['employee_count'] = 'Unknown'
        enriched['company_revenue_range'] = 'Unknown'
        enriched['funding_stage'] = 'Private (estimated)'
        enriched['company_industry'] = 'Unknown'
        enriched['company_linkedin_url'] = 'Unknown'
        enriched['tech_stack'] = []
        
        job_url = job.get('job_url')
        
        if not job_url:
            return enriched
        
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            
            company_link = await page.query_selector("a.topcard__org-name-link")
            if company_link:
                company_url = await company_link.get_attribute("href")
                if company_url:
                    enriched['company_linkedin_url'] = company_url.split("?")[0]
                    print(f"   ✓ Company URL: {enriched['company_linkedin_url']}")
            
            description_elem = await page.query_selector(".description__text")
            if description_elem:
                full_description = await description_elem.inner_text()
                enriched['tech_stack'] = self.extract_tech_stack(full_description)
                
                if enriched['tech_stack']:
                    print(f"   ✓ Tech stack: {', '.join(enriched['tech_stack'][:5])}")
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:80]}")
        
        return enriched
    
    def extract_tech_stack(self, description):
        """Extract tech stack keywords from job description"""
        
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#',
            'Ruby', 'PHP', 'Kotlin', 'Swift', 'Scala',
            'React', 'Vue', 'Angular', 'Next.js', 'Svelte', 'Redux',
            'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Rails', 'Express',
            'AWS', 'Azure', 'GCP', 'Google Cloud',
            'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitLab CI', 'GitHub Actions',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB', 'Elasticsearch',
            'Snowflake', 'Databricks', 'Airflow', 'dbt', 'Spark', 'Kafka', 'Redshift',
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Jupyter',
            'GraphQL', 'REST', 'gRPC', 'WebSockets'
        ]
        
        found_tech = set()
        description_lower = description.lower()
        
        for tech in tech_keywords:
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            if re.search(pattern, description_lower):
                found_tech.add(tech)
        
        return sorted(list(found_tech))
    
    def save_enriched(self):
        """Save enriched jobs to JSON and Excel"""
        
        output_json = self.input_file.replace('.json', '_enriched_v2.json')
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(self.enriched_jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(self.enriched_jobs)} enriched jobs to: {output_json}")
        
        self.export_to_excel(output_json.replace('.json', '.xlsx'))
    
    def export_to_excel(self, filename):
        """Export to Excel with formatting"""
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(self.enriched_jobs)
            
            priority_cols = [
                'job_title', 'company_name', 'location',
                'employee_count', 'company_revenue_range',
                'company_industry', 'posted_date',
                'company_linkedin_url', 'job_url',
                'tech_stack', 'scraped_at'
            ]
            
            cols = [c for c in priority_cols if c in df.columns]
            remaining = [c for c in df.columns if c not in cols]
            final_cols = cols + remaining
            
            df = df[final_cols]
            
            if 'tech_stack' in df.columns:
                df['tech_stack'] = df['tech_stack'].apply(lambda x: ', '.join(x) if x else '')
            
            df.to_excel(filename, index=False, sheet_name='Enriched Jobs')
            print(f"✅ Excel file created: {filename}")
            
        except Exception as e:
            print(f"⚠️  Excel export failed: {e}")


async def main():
    print("="*60)
    print("JOB ENRICHMENT PIPELINE V2 - WORKING VERSION")
    print("="*60)
    
    input_file = "output/jobs_SCALED_20251230_140903.json"
    
    enricher = JobEnricher(input_file)
    enricher.load_jobs()
    
    await enricher.enrich_all()
    
    print("\n" + "="*60)
    print("ENRICHMENT COMPLETE - CHECK EXCEL FILE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())