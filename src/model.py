import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RecommendationSystem:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.cosine_sim = None

    def load_data(self):
        """Load dataset from the specified path and create skill profiles."""
        self.df = pd.read_excel(self.data_path)
        self.df.dropna(inplace=True)
        self.df['Job title'] = self.df['Job title'].str.lower()

        # Create skill profiles
        self.df['Skill_Profile'] = self.df.apply(self.create_skill_profile, axis=1)
        self.df['Skill_Profile'] = self.df['Skill_Profile'].fillna('')
        self.df = self.df[self.df['Skill_Profile'].str.strip() != '']

    def create_skill_profile(self, row):
        """Generate a skill profile for each row."""
        skills = []
        if 'Factor_Research experience' in row and row['Factor_Research experience'] == 1:
            skills.append("research")
        if 'Factor_English proficiency' in row and row['Factor_English proficiency'] == 1:
            skills.append("english")
        if 'Student Associations' in row and row['Student Associations'] == 1:
            skills.append("teamwork")
        if 'Organizing Workshops & Seminars' in row and row['Organizing Workshops & Seminars'] == 1:
            skills.append("leadership")
        return ' '.join(skills)

    def build_similarity_matrix(self):
        """Build a TF-IDF-based cosine similarity matrix for job titles."""
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.df['Job title'])
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    def recommend(self, job_title, top_n=5):
        """Recommend jobs similar to the given job title and include relevant skills."""
        job_title = job_title.lower()
        if job_title not in self.df['Job title'].values:
            return f"'{job_title}' not found in the dataset."

        idx = self.df[self.df['Job title'] == job_title].index[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]
        job_indices = [i[0] for i in sim_scores]
        return self.df.iloc[job_indices][['Job title', 'Skill_Profile', 'Type of Degree', 'Department']]

    def recommend_career_path(self, job_title):
        """Provide the best career path for a given job title."""
        job_title = job_title.lower()
        if job_title not in self.df['Job title'].values:
            return f"'{job_title}' not found in the dataset."

        job_info = self.df[self.df['Job title'] == job_title].iloc[0]
        return {
            "Job Title": job_info['Job title'],
            "Required Skills": job_info['Skill_Profile'],
            "Recommended Degree": job_info['Type of Degree'],
            "Recommended Department": job_info['Department']
        }