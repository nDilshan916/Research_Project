import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use Path for cross-platform path handling
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_data.xlsx"
VISUALIZATIONS_DIR = DATA_DIR / "visualizations"
VISUALIZATIONS_DIR.mkdir(exist_ok=True)

def create_found_profile(row):
    """Create a profile of how the job was found"""
    found = []
    if 'From_Newspaper' in row and row['From_Newspaper'] == 1:
        found.append("Newspaper")
    if 'From_Gazette' in row and row['From_Gazette'] == 1:
        found.append("Gazette")
    if 'From_Online' in row and row['From_Online'] == 1:
        found.append("Online")
    if 'From_personal contacts' in row and row['From_personal contacts'] == 1:
        found.append("Personal Contacts")
    if 'From_Competitive exam' in row and row['From_Competitive exam'] == 1:
        found.append("Competitive Exam")
    if 'From_Via university' in row and row['From_Via university'] == 1:
        found.append("University")
    if 'From_Job fair' in row and row['From_Job fair'] == 1:
        found.append("Job Fair")
    if 'From_Internship' in row and row['From_Internship'] == 1:
        found.append("Internship")
    return ' '.join(found)

def create_skill_profile(row):
    """Create a profile of skills required for the job"""
    skills = []
    if 'Factor_Research experience' in row and row['Factor_Research experience'] == 1:
        skills.append("research")
    if 'Factor_English proficiency' in row and row['Factor_English proficiency'] == 1:
        skills.append("english")
    if 'Factor_Other professional qualifications' in row and row['Factor_Other professional qualifications'] == 1:
        skills.append("professional qualifications")
    if 'Factor_Soft skills' in row and row['Factor_Soft skills'] == 1:
        skills.append("soft skills")
    if 'Factor_Computer literacy' in row and row['Factor_Computer literacy'] == 1:
        skills.append("computer literacy")
    if 'Student Associations' in row and row['Student Associations'] == 1:
        skills.append("teamwork")
    if 'Organizing Workshops & Seminars' in row and row['Organizing Workshops & Seminars'] == 1:
        skills.append("leadership")
    if 'Charities' in row and row['Charities'] == 1:
        skills.append("volunteering")
    if 'Sports' in row and row['Sports'] == 1:
        skills.append("sports")
    if 'Cultural Activities' in row and row['Cultural Activities'] == 1:
        skills.append("cultural activities")
    return ', '.join(skills)

def create_factor_profile(row):
    """Create a profile of factors important for the job"""
    factors = []
    if 'Factor_Degree' in row and row['Factor_Degree'] == 1:
        factors.append("A Degree")
    if 'Factor_Class of degree' in row and row['Factor_Class of degree'] == 1:
        factors.append("Class of degree")
    if 'Factor_University Project' in row and row['Factor_University Project'] == 1:
        factors.append("Projects")
    if 'Factor_Field of study' in row and row['Factor_Field of study'] == 1:
        factors.append("Courses")
    if 'Factor_Personal contacts' in row and row['Factor_Personal contacts'] == 1:
        factors.append("Social Networking")
    if 'Factor_Previous work experience' in row and row['Factor_Previous work experience'] == 1:
        factors.append("Work Experience")
    if 'Additional qualifications' in row and row['Additional qualifications'] == 1:
        factors.append("Additional Qualifications")
    return ', '.join(factors)

def load_data():
    """
    Load the cleaned data with robust error handling
    Returns DataFrame or None if loading fails
    """
    try:
        logger.info(f"Loading data from {CLEANED_DATA_PATH}")
        if not CLEANED_DATA_PATH.exists():
            paths_to_try = [
                BASE_DIR / "cleaned_data.xlsx",
                Path("data/cleaned_data.xlsx"),
                Path("../data/cleaned_data.xlsx"),
                Path("../../data/cleaned_data.xlsx")
            ]
            
            df = None
            for path in paths_to_try:
                if path.exists():
                    logger.info(f"Found data at alternative path: {path}")
                    df = pd.read_excel(path)
                    break
            
            if df is None:
                logger.error(f"Data file not found. Searched in: {CLEANED_DATA_PATH} and alternative paths")
                return None
        else:
            df = pd.read_excel(CLEANED_DATA_PATH)
        
        # Process the data to create profiles
        logger.info("Processing data and creating profiles...")
        
        # Clean data - only run these operations if they haven't been run before
        df['Job title'] = df['Job title'].str.lower() if 'Job title' in df.columns else df.index.astype(str)
        
        # Ensure category column exists
        if 'category' not in df.columns and 'Job Category' in df.columns:
            df['category'] = df['Job Category']
        elif 'category' not in df.columns:
            logger.warning("No category column found, creating a placeholder")
            df['category'] = "Uncategorized"
            
        # Create profiles if they don't already exist
        if 'Found_Profile' not in df.columns:
            logger.info("Creating Found_Profile column")
            df['Found_Profile'] = df.apply(create_found_profile, axis=1)
            df['Found_Profile'] = df['Found_Profile'].fillna('')
            df = df[df['Found_Profile'].str.strip() != '']

        if 'Skill_Profile' not in df.columns:
            logger.info("Creating Skill_Profile column")
            df['Skill_Profile'] = df.apply(create_skill_profile, axis=1)
            df['Skill_Profile'] = df['Skill_Profile'].fillna('')
            df = df[df['Skill_Profile'].str.strip() != '']

        if 'Factor_Profile' not in df.columns:
            logger.info("Creating Factor_Profile column")
            df['Factor_Profile'] = df.apply(create_factor_profile, axis=1)
            df['Factor_Profile'] = df['Factor_Profile'].fillna('')
            df = df[df['Factor_Profile'].str.strip() != '']
        
        # Reset index after filtering
        df.reset_index(drop=True, inplace=True)
        logger.info(f"Successfully processed data: {len(df)} rows after filtering")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None

# Load data once on module import
df = load_data()
if df is None:
    logger.warning("Running with no data. Functions will return empty results.")
    df = pd.DataFrame(columns=['Job title', 'category', 'Factor_Soft skills', 'Factor_Field of study'])

def recommend_by_category(category):
    """
    Enhanced recommendation function that provides more detailed analysis
    for a specific job category.
    
    Parameters:
    category (str): The job category to analyze
    
    Returns:
    dict: Detailed analysis including top skills, subjects, and their importance scores
    """
    if df.empty:
        logger.warning("No data available for recommendations")
        return {"TopSkills": [], "TopSubjects": [], "MatchCount": 0, "error": "No data available"}
    
    subset = df[df['category'] == category].fillna("")
    
    if subset.empty:
        logger.warning(f"No jobs found for category: {category}")
        return {"TopSkills": [], "TopSubjects": [], "MatchCount": 0, "error": f"No jobs found for category: {category}"}
    
    # Extract skills and subjects
    skills = ", ".join(subset['Factor_Soft skills'].astype(str)).lower().split(',')
    subjects = ", ".join(subset['Factor_Field of study'].astype(str)).lower().split(',')
    
    # Count and calculate importance scores (normalized frequency)
    skill_counts = Counter(s.strip() for s in skills if s.strip())
    subject_counts = Counter(s.strip() for s in subjects if s.strip())
    
    total_skills = sum(skill_counts.values())
    total_subjects = sum(subject_counts.values())
    
    # Calculate importance scores (normalized frequency)
    skill_importance = {s: count/total_skills for s, count in skill_counts.items()} if total_skills > 0 else {}
    subject_importance = {s: count/total_subjects for s, count in subject_counts.items()} if total_subjects > 0 else {}
    
    # Get top skills and subjects with importance scores
    top_skills = [(s, round(skill_importance[s], 3)) 
                 for s, _ in skill_counts.most_common(10)]
                 
    top_subjects = [(s, round(subject_importance[s], 3)) 
                   for s, _ in subject_counts.most_common(10)]
    
    # Generate skill network visualization if there are skills
    # if skill_counts:
    #     generate_skill_network(skill_counts, category)
    
    return {
        "TopSkills": [{"name": s, "importance": i} for s, i in top_skills],
        "TopSubjects": [{"name": s, "importance": i} for s, i in top_subjects],
        "MatchCount": len(subset),
        # "CategoryDescription": generate_category_description(subset, top_skills, top_subjects)
    }

# def predict_missing(job_title, user_skills, user_subjects):
#     """
#     Enhanced prediction function that uses TF-IDF and cosine similarity
#     to recommend missing skills and subjects for a specific job title.
    
#     Parameters:
#     job_title (str): The job title to analyze
#     user_skills (list): Skills the user already has
#     user_subjects (list): Subjects the user already knows
    
#     Returns:
#     dict: Recommendations for missing skills and subjects with relevance scores
#     """
#     if df.empty:
#         logger.warning("No data available for predictions")
#         return {"MissingSkills": [], "MissingSubjects": [], "JobMatchCount": 0, "error": "No data available"}
    
#     # Find relevant job titles using partial matching
#     subset = df[df['Job title'].str.lower().str.contains(job_title.lower())].fillna("")
    
#     if subset.empty:
#         # Try matching with more general terms if specific job title not found
#         terms = job_title.lower().split()
#         subset = df[df['Job title'].str.lower().apply(lambda x: any(term in x for term in terms))].fillna("")
        
#         if subset.empty:
#             logger.warning(f"No jobs found matching: {job_title}")
#             return {
#                 "MissingSkills": [], 
#                 "MissingSubjects": [], 
#                 "JobMatchCount": 0,
#                 "error": f"No jobs found matching: {job_title}"
#             }
    
#     # Extract all skills and subjects
#     all_skills = ", ".join(subset['Factor_Soft skills'].astype(str).tolist()).lower().split(',')
#     all_subjects = ", ".join(subset['Factor_Field of study'].astype(str).tolist()).lower().split(',')
    
#     # Clean lists
#     all_skills = [s.strip() for s in all_skills if s.strip()]
#     all_subjects = [s.strip() for s in all_subjects if s.strip()]
    
#     # Convert user inputs to lowercase sets for comparison
#     user_skills_set = set(s.lower().strip() for s in user_skills)
#     user_subjects_set = set(s.lower().strip() for s in user_subjects)
    
#     # Use TF-IDF to calculate importance of skills in the job context
#     skill_vectorizer = TfidfVectorizer(max_features=50)
#     subject_vectorizer = TfidfVectorizer(max_features=50)
    
#     # Create document for each skill and subject
#     skill_docs = [f"{skill} {job_title}" for skill in all_skills]
#     subject_docs = [f"{subject} {job_title}" for subject in all_subjects]
    
#     # Handle empty lists
#     if not skill_docs:
#         skill_scores = {}
#     else:
#         try:
#             skill_tfidf = skill_vectorizer.fit_transform(skill_docs)
#             skill_scores = {all_skills[i]: skill_tfidf[i].sum() 
#                           for i in range(len(all_skills))}
#         except Exception:
#             skill_scores = Counter(all_skills)
    
#     if not subject_docs:
#         subject_scores = {}
#     else:
#         try:
#             subject_tfidf = subject_vectorizer.fit_transform(subject_docs)
#             subject_scores = {all_subjects[i]: subject_tfidf[i].sum() 
#                             for i in range(len(all_subjects))}
#         except Exception:
#             subject_scores = Counter(all_subjects)
    
#     # Sort by importance score
#     sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
#     sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
    
#     # Get missing skills and subjects with their relevance scores
#     missing_skills = [(s, round(score, 3)) for s, score in sorted_skills 
#                      if s not in user_skills_set][:10]
    
#     missing_subjects = [(s, round(score, 3)) for s, score in sorted_subjects 
#                        if s not in user_subjects_set][:10]
    
#     return {
#         "MissingSkills": [{"name": s, "relevance": r} for s, r in missing_skills],
#         "MissingSubjects": [{"name": s, "relevance": r} for s, r in missing_subjects],
#         "JobMatchCount": len(subset),
#         "JobMatches": subset['Job title'].tolist()[:5]
#     }

# def generate_skill_network(skill_counts, category):
#     """
#     Generate a network visualization of related skills as mentioned in the paper.
    
#     Parameters:
#     skill_counts (Counter): Counter of skills and their frequencies
#     category (str): The job category for the filename
#     """
#     try:
#         # Create network graph
#         G = nx.Graph()
        
#         # Add top skills as nodes
#         top_skills = [s for s, _ in skill_counts.most_common(15)]
#         for skill in top_skills:
#             G.add_node(skill, size=skill_counts[skill])
        
#         # Create edges between skills that appear together
#         for i, skill1 in enumerate(top_skills):
#             for skill2 in top_skills[i+1:]:
#                 # Edge weight based on co-occurrence
#                 weight = min(skill_counts[skill1], skill_counts[skill2]) / max(skill_counts[skill1], skill_counts[skill2])
#                 if weight > 0.3:  # Only connect if there's significant relationship
#                     G.add_edge(skill1, skill2, weight=weight)
        
#         # Generate visualization
#         plt.figure(figsize=(12, 10))
        
#         # Layout with force-directed placement
#         pos = nx.spring_layout(G)
        
#         # Get node sizes based on frequency
#         node_sizes = [skill_counts[node] * 100 for node in G.nodes()]
        
#         # Draw the network
#         nx.draw_networkx(
#             G, pos, 
#             node_size=node_sizes,
#             font_size=10, 
#             width=[G[u][v]['weight'] * 2 for u, v in G.edges()],
#             alpha=0.7,
#             edge_color="gray"
#         )
        
#         # Save visualization
#         filename = f"{category.replace(' ', '_')}_skill_network.png"
#         plt.savefig(VISUALIZATIONS_DIR / filename)
#         plt.close()
#         logger.info(f"Generated skill network visualization for {category}")
#     except Exception as e:
#         logger.error(f"Error generating skill network: {str(e)}")

# def generate_category_description(subset, top_skills, top_subjects):
#     """
#     Generate a descriptive summary of the job category based on data analysis.
    
#     Parameters:
#     subset (DataFrame): The subset of jobs for this category
#     top_skills (list): Top skills with their importance
#     top_subjects (list): Top subjects with their importance
    
#     Returns:
#     str: A descriptive summary of the job category
#     """
#     job_count = len(subset['Job title'].unique())
#     skill_desc = ", ".join([s for s, _ in top_skills[:5]])
#     subject_desc = ", ".join([s for s, _ in top_subjects[:5]])
    
#     description = (
#         f"This category contains {job_count} jobs. "
#         f"The most important skills are {skill_desc}. "
#         f"Relevant fields of study include {subject_desc}."
#     )
    
#     return description

def get_combined_features():
    return df.apply(
        lambda x: f"{str(x.get('Skill_Profile', ''))} {str(x.get('Factor_Profile', ''))}",
        axis=1
    ).fillna("").tolist()
    
def get_alumni_dataframe():
    """Return the main alumni DataFrame, always up-to-date."""
    return df
    
def cluster_job_profiles(n_clusters=10):
    """
    Implement clustering of job profiles based on skills and subjects
    as described in the research paper.

    Parameters:
    n_clusters (int): Number of clusters to create

    Returns:
    dict: Cluster descriptions and job distributions
    """
    if df.empty:
        logger.warning("No data available for clustering")
        return {"error": "No data available for clustering"}

    # Prepare features for clustering
    vectorizer = TfidfVectorizer(max_features=100)

    # Combine only the profile columns for feature extraction
    combined_features = df.apply(
        lambda x: f"{str(x.get('Skill_Profile', ''))} {str(x.get('Factor_Profile', ''))}",
        axis=1
    ).fillna("")

    # Transform to TF-IDF features
    try:
        features = vectorizer.fit_transform(combined_features)

        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features)

        # Store temporarily in a copy to avoid modifying the original
        temp_df = df.copy()
        temp_df['cluster'] = cluster_labels

        # Get cluster characteristics
        cluster_data = {}
        for cluster_id in range(n_clusters):
            cluster_jobs = temp_df[temp_df['cluster'] == cluster_id]

            # Extract top skills and subjects per cluster using profile columns
            cluster_skills = ", ".join(cluster_jobs['Skill_Profile'].fillna("")).lower().split(',')
            cluster_factors = ", ".join(cluster_jobs['Factor_Profile'].fillna("")).lower().split(',')

            skill_counts = Counter(s.strip() for s in cluster_skills if s.strip())
            factor_counts = Counter(f.strip() for f in cluster_factors if f.strip())

            cluster_data[f"Cluster {cluster_id}"] = {
                "Size": len(cluster_jobs),
                "TopSkills": [s for s, _ in skill_counts.most_common(5)],
                "TopFactors": [f for f, _ in factor_counts.most_common(5)],
                "JobTitles": cluster_jobs['Job title'].tolist()[:10]
            }

        return {
            "ClusterData": cluster_data,
            "ClusterCount": n_clusters
        }

    except Exception as e:
        logger.error(f"Error in clustering: {str(e)}")
        return {"error": f"Clustering failed: {str(e)}"}
    
    
def get_job_details(job_title):
    """
    Given a job title, return the necessary skills, important factors, and how to get that job.
    Parameters:
        job_title (str): The job title to search for.
    Returns:
        dict: {
            "JobTitle": str,
            "Skills": list of str,
            "Factors": list of str,
            "HowToGet": list of str,
            "MatchCount": int,
            "JobMatches": list of str
        }
    """
    if df.empty:
        logger.warning("No data available for job details")
        return {
            "JobTitle": job_title,
            "Skills": [],
            "Factors": [],
            "HowToGet": [],
            "MatchCount": 0,
            "JobMatches": [],
            "error": "No data available"
        }

    # Find relevant job titles using partial matching
    subset = df[df['Job title'].str.lower().str.contains(job_title.lower())].fillna("")
    if subset.empty:
        logger.warning(f"No jobs found matching: {job_title}")
        return {
            "JobTitle": job_title,
            "Skills": [],
            "Factors": [],
            "HowToGet": [],
            "MatchCount": 0,
            "JobMatches": [],
            "error": f"No jobs found matching: {job_title}"
        }

    # Aggregate skills, factors, and how-to-get info
    skills = ", ".join(subset['Skill_Profile'].astype(str)).lower().split(',')
    factors = ", ".join(subset['Factor_Profile'].astype(str)).lower().split(',')
    how_to_get = ", ".join(subset['Found_Profile'].astype(str)).split(',')

    # Clean up lists
    skills = sorted(set(s.strip() for s in skills if s.strip()))
    factors = sorted(set(f.strip() for f in factors if f.strip()))
    how_to_get = sorted(set(h.strip() for h in how_to_get if h.strip()))

    return {
        "JobTitle": job_title,
        "Skills": skills,
        "Factors": factors,
        "HowToGet": how_to_get,
        "MatchCount": len(subset),
        "JobMatches": subset['Job title'].tolist()[:5]
    }
    
# def job_title_clusters(job_title):
#     """
#     For a job title, returns all clusters with that job title and their skill/factor breakdowns.
#     Assumes clustering has already been run and df['cluster'] exists.
#     """
#     if df.empty or 'cluster' not in df.columns:
#         return {"error": "No data available or clustering not run"}
#     result = []
#     subset = df[df['Job title'].str.lower().str.contains(job_title.lower())]
#     if subset.empty:
#         return {"error": f"No jobs found for title: {job_title}"}
#     for cluster_id in sorted(subset['cluster'].unique()):
#         cdf = subset[subset['cluster'] == cluster_id]
#         skills = ", ".join(cdf['Skill_Profile'].fillna("")).lower().split(',')
#         factors = ", ".join(cdf['Factor_Profile'].fillna("")).lower().split(',')
#         skill_counts = Counter(s.strip() for s in skills if s.strip())
#         factor_counts = Counter(f.strip() for f in factors if f.strip())
#         result.append({
#             "cluster_id": int(cluster_id),
#             "size": len(cdf),
#             "top_skills": [s for s, _ in skill_counts.most_common(7)],
#             "top_factors": [f for f, _ in factor_counts.most_common(7)],
#             "job_titles": cdf['Job title'].tolist()
#         })
#     return result