from model import RecommendationSystem

def main():
    # Initialize the recommendation system
    data_path = "data/cleaned_data.xlsx"
    recommender = RecommendationSystem(data_path)

    # Load data and build the similarity matrix
    recommender.load_data()
    recommender.build_similarity_matrix()

    # Get recommendations
    job_title = input("Enter a job title: ")
    recommendations = recommender.recommend(job_title)
    print("\nRecommended Jobs:")
    print(recommendations)

if __name__ == "__main__":
    main()