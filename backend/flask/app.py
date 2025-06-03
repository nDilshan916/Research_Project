from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import model
import pandas as pd
from collections import Counter

app = Flask(__name__)
CORS(app)

@app.route('/categories')
def list_categories():
    """Return all unique job categories"""
    if model.df is not None:
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

@app.route('/cluster', methods=['GET'])
def cluster_jobs():
    """Cluster job profiles for visualization"""
    n_clusters = request.args.get('clusters', default=5, type=int)
    return jsonify(model.cluster_job_profiles(n_clusters))

@app.route('/job_title_clusters/<job_title>')
def get_job_title_clusters(job_title):
    return jsonify(model.job_title_clusters(job_title))

@app.route('/job_details/<job_title>')
def get_job_details(job_title):
    print(f"[Flask] Received request for job_title: {job_title}")
    try:
        details = model.get_job_details(job_title)
        print(f"[Flask] Details returned for {job_title}: {details}")
        if details is None:
            # Not found or no data
            return jsonify({"error": "No details found for job title"}), 404
        return jsonify(details)
    except Exception as e:
        print(f"[Flask] ERROR for job_title {job_title}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/job_dashboard_data/<job_title>')
def get_job_dashboard_data(job_title):
    """
    Aggregated data for job dashboard visualizations:
    - Sector/department/degree distributions
    - Yearly trend
    """
    subset = model.df[model.df['Job title'].str.lower().str.contains(job_title.lower())].copy()
    if subset.empty:
        return jsonify({"error": "No jobs found for this title"}), 404

    # Sector/department/degree distributions
    sector_counts = subset['Sector'].value_counts().to_dict() if 'Sector' in subset.columns else {}
    dept_counts = subset['Department'].value_counts().to_dict() if 'Department' in subset.columns else {}
    degree_counts = subset['Type of Degree'].value_counts().to_dict() if 'Type of Degree' in subset.columns else {}

    # Yearly trend
    if "Date of current appointment " in subset.columns:
        subset["year"] = pd.to_datetime(subset["Date of current appointment "], errors="coerce").dt.year
        year_counts = subset["year"].value_counts().sort_index().to_dict()
    else:
        year_counts = {}

    return jsonify({
        "sector_counts": sector_counts,
        "dept_counts": dept_counts,
        "degree_counts": degree_counts,
        "year_counts": year_counts,
        "total_count": len(subset)
    })


if __name__ == '__main__':
    app.run(debug=True)