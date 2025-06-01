from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import model

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


# If you want to serve generated images, uncomment these lines:
# @app.route('/visualizations/<filename>')
# def get_visualization(filename):
#     """Serve visualization images"""
#     return send_from_directory(model.VISUALIZATIONS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)