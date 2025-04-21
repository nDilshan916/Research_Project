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
        
        # Create wat to find profile
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
        
    def create_found_profile(self, row):
        """Generate a found profile for each row."""
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

    def create_skill_profile(self, row):
        """Generate a skill profile for each row."""
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
        return ' '.join(skills)
    
    def create_factor_profile(self, row):
        """Generate a factor profile for each row."""
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
        return ' '.join(factors)

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
        return self.df.iloc[job_indices][['Job title', 'Found_Profile', 'Skill_Profile', 'Factor_Profile', 'Type of Degree', 'Department']]

    def recommend_career_path(self, job_title):
        """Provide the best career path for a given job title."""
        job_title = job_title.lower()
        if job_title not in self.df['Job title'].values:
            return f"'{job_title}' not found in the dataset."

        job_info = self.df[self.df['Job title'] == job_title].iloc[0]
        return {
            "Job Title": job_info['Job title'],
            "Way to Find": job_info['Found_Profile'],
            "Required Skills": job_info['Skill_Profile'],
            "Required Factors": job_info['Factor_Profile'],
            "Recommended Degree": job_info['Type of Degree'],
            "Recommended Department": job_info['Department']
        }