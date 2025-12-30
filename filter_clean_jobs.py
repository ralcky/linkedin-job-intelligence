"""
Filter out jobs with masked data (****)
Keep only complete, usable records
"""

import json
import pandas as pd

def is_clean_job(job):
    """Check if job has no masked data"""
    
    fields_to_check = ['job_title', 'company_name', 'location']
    
    for field in fields_to_check:
        value = job.get(field, '')
        if '*' in str(value):
            return False
    
    return True

def main():
    print("="*60)
    print("FILTERING CLEAN JOBS ONLY")
    print("="*60 + "\n")
    
    # Load all jobs
    with open('output/jobs_FINAL_DELIVERY.json', 'r', encoding='utf-8') as f:
        all_jobs = json.load(f)
    
    print(f"📂 Total jobs before filtering: {len(all_jobs)}")
    
    # Filter clean jobs
    clean_jobs = [job for job in all_jobs if is_clean_job(job)]
    
    print(f"✅ Clean jobs after filtering: {len(clean_jobs)}")
    print(f"🗑️  Removed {len(all_jobs) - len(clean_jobs)} jobs with masked data\n")
    
    # Save clean version
    output_json = 'output/SaaS_Jobs_CLEAN_FINAL.json'
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(clean_jobs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved clean jobs to: {output_json}")
    
    # Create clean Excel
    df = pd.DataFrame(clean_jobs)
    
    if 'tech_stack' in df.columns:
        df['tech_stack'] = df['tech_stack'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    
    col_order = [
        'job_title', 'company_name', 'location', 
        'employee_count', 'company_revenue_range', 'funding_stage',
        'company_industry', 'tech_stack', 'posted_date',
        'company_linkedin_url', 'job_url', 'scraped_at'
    ]
    
    cols = [c for c in col_order if c in df.columns]
    df = df[cols]
    
    excel_file = 'output/SaaS_Jobs_CLEAN_FINAL.xlsx'
    df.to_excel(excel_file, index=False, sheet_name='Clean VP+ Jobs')
    
    print(f"✅ Excel saved to: {excel_file}")
    
    # Stats
    print("\n" + "="*60)
    print("CLEAN DATASET SUMMARY")
    print("="*60)
    print(f"Total jobs: {len(df)}")
    print(f"Unique companies: {df['company_name'].nunique()}")
    print(f"Jobs with tech stack: {df['tech_stack'].astype(bool).sum()}")
    print(f"Date range: {df['posted_date'].min()} to {df['posted_date'].max()}")
    
    # Top companies
    print(f"\nTop companies by job count:")
    for company, count in df['company_name'].value_counts().head(5).items():
        print(f"  - {company}: {count} jobs")
    
    print("="*60)

if __name__ == "__main__":
    main()