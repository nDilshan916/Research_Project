from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from model import RecommendationSystem

app = Flask(__name__)
CORS(app)

# Path to your data file
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cleaned_data.xlsx')
recommender = RecommendationSystem(DATA_PATH)
recommender.load_data()
# recommender.build_similarity_matrix()

# get all unique job titles from backend

@app.route('/api/job_titles', methods=['GET'])
def job_category():
    category = recommender.df['category'].dropna().unique().tolist()
    return jsonify(category)

@app.route('/api/search', methods=['POST'])
def search():
    job_category = request.json.get('category', '')
    print("Received category:", job_category)
    print("Available categories:", recommender.get_all_categories())
    recommendations = recommender.recommend(job_category)
    print("Recommendations:", recommendations)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)