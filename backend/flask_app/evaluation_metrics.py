import pandas as pd
import numpy as np
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_alumni_data():
    """Load your alumni data - adjust the path as needed"""
    try:
        # Try different possible paths for your data file
        possible_paths = [
            "data/cleaned_data.xlsx",
            "../data/cleaned_data.xlsx", 
            "../../data/cleaned_data.xlsx",
            "cleaned_data.xlsx"
        ]
        
        df = None
        for path in possible_paths:
            try:
                df = pd.read_excel(path)
                print(f"✓ Data loaded from: {path}")
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            print("❌ Could not find data file. Please ensure cleaned_data.xlsx is in the correct location.")
            return None
            
        print(f"✓ Loaded {len(df)} alumni records")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def prepare_evaluation_data(df):
    """Prepare the data for evaluation by creating skill and subject profiles"""
    
    # Create skill profile from various skill-related columns
    def extract_skills(row):
        skills = []
        skill_columns = [
            'Factor_Research experience', 'Factor_English proficiency',
            'Factor_Other professional qualifications', 'Factor_Soft skills',
            'Factor_Computer literacy', 'Student Associations',
            'Organizing Workshops & Seminars', 'Charities', 'Sports',
            'Cultural Activities'
        ]
        
        skill_mapping = {
            'Factor_Research experience': 'research',
            'Factor_English proficiency': 'english',
            'Factor_Other professional qualifications': 'professional qualifications',
            'Factor_Soft skills': 'soft skills',
            'Factor_Computer literacy': 'computer literacy',
            'Student Associations': 'teamwork',
            'Organizing Workshops & Seminars': 'leadership',
            'Charities': 'volunteering',
            'Sports': 'sports',
            'Cultural Activities': 'cultural activities'
        }
        
        for col in skill_columns:
            if col in row and row[col] == 1:
                skills.append(skill_mapping[col])
        
        return skills
    
    # Create factor profile from factor-related columns
    def extract_factors(row):
        factors = []
        factor_columns = [
            'Factor_Degree', 'Factor_Class of degree', 'Factor_University Project',
            'Factor_Field of study', 'Factor_Personal contacts',
            'Factor_Previous work experience', 'Additional qualifications'
        ]
        
        factor_mapping = {
            'Factor_Degree': 'degree',
            'Factor_Class of degree': 'class of degree',
            'Factor_University Project': 'university projects',
            'Factor_Field of study': 'field of study',
            'Factor_Personal contacts': 'networking',
            'Factor_Previous work experience': 'work experience',
            'Additional qualifications': 'additional qualifications'
        }
        
        for col in factor_columns:
            if col in row and row[col] == 1:
                factors.append(factor_mapping[col])
        
        return factors

    # Apply the extraction functions
    df['skills'] = df.apply(extract_skills, axis=1)
    df['factors'] = df.apply(extract_factors, axis=1)

    # Ensure we have a category column
    if 'category' not in df.columns:
        if 'Job Category' in df.columns:
            df['category'] = df['Job Category']
        else:
            df['category'] = 'General'  # Default category
    
    return df

def get_top_k_recommendations(category_data, k=5):
    """Get top-k skill and subject recommendations for a category"""
    
    # Aggregate all skills and factors for this category
    all_skills = []
    all_factors = []
    
    for _, row in category_data.iterrows():
        all_skills.extend(row['skills'])
        all_factors.extend(row['factors'])
    
    # Count frequencies and get top-k
    skill_counts = Counter(all_skills)
    factor_counts = Counter(all_factors)

    top_skills = [skill for skill, _ in skill_counts.most_common(k)]
    top_factors = [factor for factor, _ in factor_counts.most_common(k)]

    return top_skills, top_factors

def calculate_precision_at_k(recommended, actual, k=5):
    """Calculate Precision@K"""
    if not recommended:
        return 0.0
    
    recommended_set = set(recommended[:k])
    actual_set = set(actual)
    
    intersection = recommended_set.intersection(actual_set)
    
    return len(intersection) / min(len(recommended_set), k)

def calculate_recall_at_k(recommended, actual, k=5):
    """Calculate Recall@K"""
    if not actual:
        return 0.0
    
    recommended_set = set(recommended[:k])
    actual_set = set(actual)
    
    intersection = recommended_set.intersection(actual_set)
    
    return len(intersection) / len(actual_set)

def evaluate_recommendation_system(df, test_ratio=0.3, random_seed=42):
    """
    Evaluate the recommendation system and return Precision@5 and Recall@5
    """
    np.random.seed(random_seed)
    
    # Split data into train and test
    test_size = int(len(df) * test_ratio)
    test_indices = np.random.choice(df.index, size=test_size, replace=False)
    
    train_df = df.drop(test_indices)
    test_df = df.loc[test_indices]
    
    print(f"✓ Split data: {len(train_df)} training, {len(test_df)} testing")
    
    skill_precisions = []
    skill_recalls = []
    factor_precisions = []
    factor_recalls = []
    
    print("🔄 Evaluating recommendations...")
    
    # For each test case, generate recommendations and calculate metrics
    for idx, test_row in test_df.iterrows():
        category = test_row['category']
        actual_skills = test_row['skills']
        actual_factors = test_row['factors']

        # Get training data for this category
        category_train_data = train_df[train_df['category'] == category]
        
        if len(category_train_data) == 0:
            continue  # Skip if no training data for this category
        
        # Get recommendations
        recommended_skills, recommended_subjects = get_top_k_recommendations(category_train_data, k=5)
        
        # Calculate metrics for skills
        if actual_skills:
            precision = calculate_precision_at_k(recommended_skills, actual_skills, k=5)
            recall = calculate_recall_at_k(recommended_skills, actual_skills, k=5)
            skill_precisions.append(precision)
            skill_recalls.append(recall)

        # Calculate metrics for factors
        if actual_factors:
            precision = calculate_precision_at_k(recommended_subjects, actual_factors, k=5)
            recall = calculate_recall_at_k(recommended_subjects, actual_factors, k=5)
            factor_precisions.append(precision)
            factor_recalls.append(recall)
    
    # Calculate average metrics
    avg_skill_precision = np.mean(skill_precisions) if skill_precisions else 0
    avg_skill_recall = np.mean(skill_recalls) if skill_recalls else 0
    avg_factor_precision = np.mean(factor_precisions) if factor_precisions else 0
    avg_factor_recall = np.mean(factor_recalls) if factor_recalls else 0

    return {
        'skill_precision_at_5': avg_skill_precision * 100,
        'skill_recall_at_5': avg_skill_recall * 100,
        'factor_precision_at_5': avg_factor_precision * 100,
        'factor_recall_at_5': avg_factor_recall * 100,
        'total_evaluations': len(skill_precisions) + len(factor_precisions),
        'skill_evaluations': len(skill_precisions),
        'factor_evaluations': len(factor_precisions)
    }

def main():
    """Main function to calculate evaluation metrics"""
    print("🚀 Alumni Career Recommendation System Evaluation")
    print("=" * 60)
    
    # Load data
    df = load_alumni_data()
    if df is None:
        return
    
    # Prepare evaluation data
    print("🔄 Preparing evaluation data...")
    df = prepare_evaluation_data(df)

    # Filter out rows with no skills or factors
    df = df[(df['skills'].str.len() > 0) | (df['factors'].str.len() > 0)]
    print(f"✓ {len(df)} records with skills/factors available for evaluation")

    if len(df) < 10:
        print("❌ Not enough data for reliable evaluation (need at least 10 records)")
        return
    
    # Run evaluation
    print("🔄 Running evaluation...")
    results = evaluate_recommendation_system(df)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    
    print(f"\n📈 METRICS:")
    print(f"├── Skill Precision@5:  {results['skill_precision_at_5']:.1f}%")
    print(f"├── Skill Recall@5:     {results['skill_recall_at_5']:.1f}%")
    print(f"├── Factor Precision@5: {results['factor_precision_at_5']:.1f}%")
    print(f"└── Factor Recall@5:    {results['factor_recall_at_5']:.1f}%")

    print(f"\n📋 EVALUATION DETAILS:")
    print(f"├── Total evaluations:   {results['total_evaluations']}")
    print(f"├── Skill evaluations:   {results['skill_evaluations']}")
    print(f"└── Factor evaluations: {results['factor_evaluations']}")

    # Calculate combined metrics (average of skills and factors)
    combined_precision = (results['skill_precision_at_5'] + results['factor_precision_at_5']) / 2
    combined_recall = (results['skill_recall_at_5'] + results['factor_recall_at_5']) / 2

    print("\n" + "=" * 60)
    print("📋 FOR RESEARCH PAPER TABLE:")
    print("=" * 60)
    print(f"Precision@5: {combined_precision:.1f}%")
    print(f"Recall@5:    {combined_recall:.1f}%")
    
    print("\n💡 INTERPRETATION:")
    print(f"• Precision@5 ({combined_precision:.1f}%): Of the top 5 recommendations, {combined_precision:.1f}% were relevant")
    print(f"• Recall@5 ({combined_recall:.1f}%): The system captured {combined_recall:.1f}% of all relevant items in top 5")
    
    return results

if __name__ == "__main__":
    results = main()