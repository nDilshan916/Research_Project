import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

class RecommendationSystem:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.cosine_sim = None
        self.kmeans = None

    def load_data(self):
        """Load dataset from the specified path and create skill profiles."""
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

        self.df.reset_index(drop=True, inplace=True)

    def create_found_profile(self, row):
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


    def get_all_categories(self):
        """Return all unique categories (for dropdowns)."""
        if 'category' in self.df.columns:
            return sorted(self.df['category'].dropna().unique().tolist())
        return []

    def recommend(self, category, top_n=5):
        """Recommend jobs for a given category (from the 'category' column)."""
        if 'category' not in self.df.columns:
            return []
        jobs = self.df[self.df['category'].str.strip().str.lower() == category.strip().lower()]
        if jobs.empty:
            return []
        jobs = jobs.head(top_n)
        return jobs[['Job title', 'Found_Profile', 'Skill_Profile', 'Factor_Profile', 'Type of Degree', 'Department']].to_dict(orient='records')
    

    def get_job_titles_by_semantic_category(self):
        """
        Returns a dictionary where keys are semantic categories (from the 'category' column)
        and values are lists of job titles in that category.
        """
        grouped = {}
        if 'category' not in self.df.columns:
            raise ValueError("The DataFrame does not have a 'category' column.")
        for cat in sorted(self.df['category'].dropna().unique()):
            titles = sorted(self.df[self.df['category'] == cat]['Job title'].unique())
            grouped[cat] = titles
        return grouped