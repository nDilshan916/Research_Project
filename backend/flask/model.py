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

class JobProfileModel:
    def __init__(self, data_path=None):
        """Initialize the model with a data path"""
        self.data_path = data_path or CLEANED_DATA_PATH
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load dataset from the specified path and create skill profiles."""
        try:
            logger.info(f"Loading data from {self.data_path}")
            
            # Try multiple paths if the primary one doesn't exist
            if not Path(self.data_path).exists():
                paths_to_try = [
                    BASE_DIR / "cleaned_data.xlsx",
                    Path("data/cleaned_data.xlsx"),
                    Path("../data/cleaned_data.xlsx"),
                    Path("../../data/cleaned_data.xlsx")
                ]
                
                for path in paths_to_try:
                    if path.exists():
                        logger.info(f"Found data at alternative path: {path}")
                        self.data_path = path
                        break
                else:
                    logger.error(f"Data file not found. Searched in: {self.data_path} and alternative paths")
                    self.df = pd.DataFrame(columns=['Job title', 'category', 'Factor_Soft skills', 'Factor_Field of study'])
                    return
            
            # Load the data
            self.df = pd.read_excel(self.data_path)
            self.df.dropna(inplace=True)
            self.df['Job title'] = self.df['Job title'].str.lower()

            # Create way to find profile
            self.df['Found_Profile'] = self.df.apply(self.create_found_profile, axis=1)
            self.df['Found_Profile'] = self.df['Found_Profile'].fillna('')
            self.df = self.df[self.df['Found_Profile'].str.strip() != '']

            # Create skill profiles
            self.df['Skill_Profile'] = self.df.apply(self.create_skill_profile, axis=1)
            self.df['Skill_Profile'] = self.df['Skill_Profile'].fillna('')
            self.df = self.df[self.df['Skill_Profile'].str.strip() != '']

            # Create factors for job titles
            self.df['Factor_Profile'] = self.df.apply(self.create_factor_profile, axis=1)
            self.df['Factor_Profile'] = self.df['Factor_Profile'].fillna('')
            self.df = self.df[self.df['Factor_Profile'].str.strip() != '']

            # If you have a 'category' column from semantic classification, keep it
            if 'category' in self.df.columns:
                self.df['category'] = self.df['category'].fillna('')
            elif 'Sector' in self.df.columns:
                # Use Sector as category if no category column exists
                self.df['category'] = self.df['Sector'].fillna('Other')
            else:
                # Create a placeholder category
                self.df['category'] = "Uncategorized"

            self.df.reset_index(drop=True, inplace=True)
            logger.info(f"Successfully loaded and processed {len(self.df)} job profiles")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            self.df = pd.DataFrame(columns=['Job title', 'category', 'Factor_Soft skills', 'Factor_Field of study'])

    def create_found_profile(self, row):
        """Create a profile of how the job was found"""
        found = []
        if 'From_Newspaper' in row and row['From_Newspaper'] == 1:
            found.append("can be found from Newspaper")
        if 'From_Gazette' in row and row['From_Gazette'] == 1:
            found.append("can be found from Gazette")
        if 'From_Online' in row and row['From_Online'] == 1:
            found.append("can be found from Online")
        if 'From_personal contacts' in row and row['From_personal contacts'] == 1:
            found.append("need some Personal Contacts")
        if 'From_Competitive exam' in row and row['From_Competitive exam'] == 1:
            found.append("face Competitive Exam")
        if 'From_Via internship (training)' in row and row['From_Via internship (training)'] == 1:
            found.append("from Internship")
        if 'From_Via university' in row and row['From_Via university'] == 1:
            found.append("from University connections")
        if 'From_Job fair/Career Guidance' in row and row['From_Job fair/Career Guidance'] == 1:
            found.append("from Job Fair")
        if 'From_Continuing with same job held during university education' in row and row['From_Continuing with same job held during university education'] == 1:
            found.append("from Continuing Job")
        return ' '.join(found)

    def create_skill_profile(self, row):
        """Create a profile of skills required for the job"""
        skills = []
        if 'Factor_Research experience' in row and row['Factor_Research experience'] == 1:
            skills.append("research skills")
        if 'Factor_English proficiency' in row and row['Factor_English proficiency'] == 1:
            skills.append("english skills")
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
        return ' '.join(skills)

    def create_factor_profile(self, row):
        """Create a profile of factors important for the job"""
        factors = []
        if 'Factor_Degree' in row and row['Factor_Degree'] == 1:
            factors.append("Should have a Degree")
        if 'Factor_Class of degree' in row and row['Factor_Class of degree'] == 1:
            factors.append("Should have a Class of degree")
        if 'Factor_University Project' in row and row['Factor_University Project'] == 1:
            factors.append("Should have University Projects")
        if 'Factor_Field of study' in row and row['Factor_Field of study'] == 1:
            factors.append("Should learn relevant Courses")
        if 'Factor_Personal contacts' in row and row['Factor_Personal contacts'] == 1:
            factors.append("Should have Social Networking")
        if 'Factor_Previous work experience' in row and row['Factor_Previous work experience'] == 1:
            factors.append("Should have Work Experience")
        if 'Additional qualifications' in row and row['Additional qualifications'] == 1:
            factors.append("Should have Additional Qualifications")
        return ' '.join(factors)
        
    def recommend_by_category(self, category):
        """
        Enhanced recommendation function that provides more detailed analysis
        for a specific job category.
        """
        if self.df.empty:
            logger.warning("No data available for recommendations")
            return {"TopSkills": [], "MatchCount": 0, "error": "No data available"}
        
        subset = self.df[self.df['category'] == category].fillna("")
        
        if subset.empty:
            logger.warning(f"No jobs found for category: {category}")
            return {"TopSkills": [], "MatchCount": 0, "error": f"No jobs found for category: {category}"}
        
        # Use Skill_Profile instead of Factor_Soft skills to get actual skill names
        # Split by space since skills are space-separated in Skill_Profile
        skills = []
        for profile in subset['Skill_Profile'].astype(str).tolist():
            skills.extend([s.strip() for s in profile.split() if s.strip()])
        
        # Count and calculate importance scores (normalized frequency)
        skill_counts = Counter(skills)
        
        total_skills = sum(skill_counts.values())
        
        # Calculate importance scores (normalized frequency)
        skill_importance = {s: count/total_skills for s, count in skill_counts.items()} if total_skills > 0 else {}
        
        # Get top skills with importance scores
        top_skills = [(s, round(skill_importance[s], 3)) 
                     for s, _ in skill_counts.most_common(10)]
                            
        # Generate skill network visualization if there are skills
        if skill_counts:
            self.generate_skill_network(skill_counts, category)
        
        return {
            "TopSkills": [{"name": s, "importance": i} for s, i in top_skills],
            "MatchCount": len(subset),
            "CategoryDescription": self.generate_category_description(subset, top_skills)
        }

    def predict_missing(self, job_title, user_skills):
        """
        Enhanced prediction function that uses TF-IDF and cosine similarity
        to recommend missing skills for a specific job title.
        """
        if self.df.empty:
            logger.warning("No data available for predictions")
            return {"MissingSkills": [], "JobMatchCount": 0, "error": "No data available"}
        
        # Find relevant job titles using partial matching
        subset = self.df[self.df['Job title'].str.lower().str.contains(job_title.lower())].fillna("")
        
        if subset.empty:
            # Try matching with more general terms if specific job title not found
            terms = job_title.lower().split()
            subset = self.df[self.df['Job title'].str.lower().apply(lambda x: any(term in x for term in terms))].fillna("")
            
            if subset.empty:
                logger.warning(f"No jobs found matching: {job_title}")
                return {
                    "MissingSkills": [], 
                    "JobMatchCount": 0,
                    "error": f"No jobs found matching: {job_title}"
                }
        
        # Extract all skills from Skill_Profile instead of Factor_Soft skills
        all_skills = []
        for profile in subset['Skill_Profile'].astype(str).tolist():
            all_skills.extend([s.strip() for s in profile.split() if s.strip()])
        
        # Remove duplicates while preserving order
        all_skills = list(dict.fromkeys(all_skills))
        
        # Convert user inputs to lowercase sets for comparison
        user_skills_set = set(s.lower().strip() for s in user_skills)
        
        # Use TF-IDF to calculate importance of skills in the job context
        if not all_skills:
            return {
                "MissingSkills": [],
                "JobMatchCount": len(subset),
                "JobMatches": subset['Job title'].tolist()[:5],
                "message": "No specific skills found for this job title"
            }
        
        skill_vectorizer = TfidfVectorizer(max_features=50)
        
        # Create document for each skill
        skill_docs = [f"{skill} {job_title}" for skill in all_skills]
        
        try:
            skill_tfidf = skill_vectorizer.fit_transform(skill_docs)
            skill_scores = {all_skills[i]: skill_tfidf[i].sum() 
                          for i in range(len(all_skills))}
        except Exception:
            skill_scores = Counter(all_skills)
        
        # Sort by importance score
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get missing skills with their relevance scores
        missing_skills = [(s, round(score, 3)) for s, score in sorted_skills 
                         if s not in user_skills_set][:10]
        
        return {
            "MissingSkills": [{"name": s, "relevance": r} for s, r in missing_skills],
            "JobMatchCount": len(subset),
            "JobMatches": subset['Job title'].tolist()[:5]
        }

    def generate_skill_network(self, skill_counts, category):
        """
        Generate a network visualization of related skills as mentioned in the paper.
        """
        try:
            # Create network graph
            G = nx.Graph()
            
            # Add top skills as nodes
            top_skills = [s for s, _ in skill_counts.most_common(15)]
            for skill in top_skills:
                G.add_node(skill, size=skill_counts[skill])
            
            # Create edges between skills that appear together
            for i, skill1 in enumerate(top_skills):
                for skill2 in top_skills[i+1:]:
                    # Edge weight based on co-occurrence
                    weight = min(skill_counts[skill1], skill_counts[skill2]) / max(skill_counts[skill1], skill_counts[skill2])
                    if weight > 0.3:  # Only connect if there's significant relationship
                        G.add_edge(skill1, skill2, weight=weight)
            
            # Generate visualization
            plt.figure(figsize=(12, 10))
            
            # Layout with force-directed placement
            pos = nx.spring_layout(G)
            
            # Get node sizes based on frequency
            node_sizes = [skill_counts[node] * 100 for node in G.nodes()]
            
            # Draw the network
            nx.draw_networkx(
                G, pos, 
                node_size=node_sizes,
                font_size=10, 
                width=[G[u][v]['weight'] * 2 for u, v in G.edges()],
                alpha=0.7,
                edge_color="gray"
            )
            
            # Save visualization
            filename = f"{category.replace(' ', '_')}_skill_network.png"
            plt.savefig(VISUALIZATIONS_DIR / filename)
            plt.close()
            logger.info(f"Generated skill network visualization for {category}")
        except Exception as e:
            logger.error(f"Error generating skill network: {str(e)}")

    def generate_category_description(self, subset, top_skills):
        """
        Generate a descriptive summary of the job category based on data analysis.
        """
        job_count = len(subset)
        skill_desc = ", ".join([s for s, _ in top_skills[:5]])
        
        description = (
            f"This category contains {job_count} jobs. "
            f"The most important skills are {skill_desc}. "
        )
        
        return description

    def cluster_job_profiles(self, n_clusters=5):
        """
        Implement clustering of job profiles based on skills
        as described in the research paper.
        """
        if self.df.empty:
            logger.warning("No data available for clustering")
            return {"error": "No data available for clustering"}
        
        # Prepare features for clustering
        vectorizer = TfidfVectorizer(max_features=100)
        
        # Combine skills for feature extraction
        combined_features = self.df.apply(
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
            temp_df = self.df.copy()
            temp_df['cluster'] = cluster_labels
            
            # Get cluster characteristics
            cluster_data = {}
            for cluster_id in range(n_clusters):
                cluster_jobs = temp_df[temp_df['cluster'] == cluster_id]
                
                # Extract skills from Skill_Profile column to get actual skill names
                cluster_skills = []
                for profile in cluster_jobs['Skill_Profile'].fillna("").astype(str).tolist():
                    cluster_skills.extend([s.strip() for s in profile.split() if s.strip()])
                    
                skill_counts = Counter(cluster_skills)
                
                cluster_data[f"Cluster {cluster_id}"] = {
                    "Size": len(cluster_jobs),
                    "TopSkills": [s for s, _ in skill_counts.most_common(5)],
                    "JobTitles": cluster_jobs['Job title'].tolist()[:10]
                }
            
            return {
                "ClusterData": cluster_data,
                "ClusterCount": n_clusters
            }
            
        except Exception as e:
            logger.error(f"Error in clustering: {str(e)}")
            return {"error": f"Clustering failed: {str(e)}"}

# Create an instance of the model for use in the Flask app
model = JobProfileModel()

# Export functions that match the original API
def recommend_by_category(category):
    return model.recommend_by_category(category)

def predict_missing(job_title, user_skills):
    return model.predict_missing(job_title, user_skills)

def cluster_job_profiles(n_clusters=5):
    return model.cluster_job_profiles(n_clusters)

# For backward compatibility
df = model.df