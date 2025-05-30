from flask import Flask, jsonify, request
from flask_cors import CORS
import model

app = Flask(__name__)
CORS(app)

@app.route('/categories')
def list_categories():
    """Return all unique job categories"""
    if model.df is not None:
        # Extract unique categories from the dataframe
        categories = sorted(model.df['category'].unique().tolist())
        return jsonify(categories)
    return jsonify([]), 500

@app.route('/category/<category>')
def get_category(category):
    """Get recommendations for a specific job category"""
    return jsonify(model.recommend_by_category(category))

@app.route('/jobs/<category>')
def list_jobs(category):
    """List all jobs for a specific category"""
    if model.df is not None:
        jobs = model.df[model.df['category'] == category]['Job title'].unique().tolist()
        return jsonify(sorted(jobs))
    return jsonify([]), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Predict missing skills and subjects for a job"""
    data = request.get_json()
    job_title = data.get('job_title', '')
    skills = data.get('skills', [])
    subjects = data.get('subjects', [])
    
    return jsonify(model.predict_missing(job_title, skills, subjects))

@app.route('/cluster', methods=['GET'])
def cluster_jobs():
    """Cluster job profiles for visualization"""
    n_clusters = request.args.get('clusters', default=5, type=int)
    return jsonify(model.cluster_job_profiles(n_clusters))

# @app.route('/visualizations/<filename>')
# def get_visualization(filename):
#     """Serve visualization images"""
#     return send_from_directory(model.VISUALIZATIONS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)