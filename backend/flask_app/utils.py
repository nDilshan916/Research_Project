categories = {
    "Software Development": ["software engineer", ...],
    # Add other categories and jobs
}

def map_job_to_category(job_title):
    job_title = job_title.lower()
    for category, keywords in categories.items():
        if any(keyword in job_title for keyword in keywords):
            return category
    return "Other"

def get_jobs_by_category(category):
    import pandas as pd
    df = pd.read_csv('data/alumni_clean.csv')
    df['Job Category'] = df['Job title'].apply(map_job_to_category)
    return df[df['Job Category'] == category]['Job title'].dropna().unique().tolist()

