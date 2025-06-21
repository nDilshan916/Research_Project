from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import model  # your own model (model.py)
import pandas as pd
import logging
from transformers import AutoTokenizer, BlenderbotForConditionalGeneration

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask_app")

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

# --- AI Model Setup (load once on app start) ---
MODEL_NAME = "facebook/blenderbot-400M-distill"

device = torch.device("cpu")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    blenderbot_model = BlenderbotForConditionalGeneration.from_pretrained(MODEL_NAME).to(device)
    logger.info("Loaded Blenderbot model successfully.")
except Exception as e:
    logger.error(f"Failed to load Blenderbot model: {e}")
    tokenizer = None
    blenderbot_model = None

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/categories')
def list_categories():
    if model.df is not None:
        categories = sorted(model.df['category'].unique())
        return jsonify(categories)
    return jsonify([]), 500

@app.route('/category/<category>')
def get_category(category):
    return jsonify(model.recommend_by_category(category))

@app.route('/jobs/<category>')
def list_jobs(category):
    if model.df is not None:
        jobs = model.df.loc[model.df['category'] == category, 'Job title'].unique()
        return jsonify(sorted(jobs))
    return jsonify([]), 500

@app.route('/cluster', methods=['GET'])
def cluster_jobs():
    n_clusters = request.args.get('clusters', default=5, type=int)
    return jsonify(model.cluster_job_profiles(n_clusters))

@app.route('/job_title_clusters/<job_title>')
def get_job_title_clusters(job_title):
    if hasattr(model, "job_title_clusters"):
        return jsonify(model.job_title_clusters(job_title))
    return jsonify({"error": "job_title_clusters function not implemented"}), 501

@app.route('/job_details/<job_title>')
def get_job_details(job_title):
    logger.info(f"Request for job_title: {job_title}")
    try:
        details = model.get_job_details(job_title)
        if not details:
            logger.warning(f"No details found for {job_title}")
            return jsonify({"error": "No details found for job title"}), 404
        return jsonify(details)
    except Exception as e:
        logger.error(f"Error for job_title {job_title}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/job_dashboard_data/<job_title>')
def get_job_dashboard_data(job_title):
    try:
        subset = model.df.loc[model.df['Job title'].str.lower().str.contains(job_title.lower())]
        if subset.empty:
            return jsonify({"error": "No jobs found for this title"}), 404

        sector_counts = subset['Sector'].value_counts().to_dict() if 'Sector' in subset.columns else {}
        dept_counts = subset['Department'].value_counts().to_dict() if 'Department' in subset.columns else {}
        degree_counts = subset['Type of Degree'].value_counts().to_dict() if 'Type of Degree' in subset.columns else {}

        if "Date of current appointment " in subset.columns:
            years = pd.to_datetime(subset["Date of current appointment "], errors="coerce").dt.year
            year_counts = years.value_counts().sort_index().to_dict()
        else:
            year_counts = {}

        return jsonify({
            "sector_counts": sector_counts,
            "dept_counts": dept_counts,
            "degree_counts": degree_counts,
            "year_counts": year_counts,
            "total_count": len(subset)
        })
    except Exception as e:
        logger.error(f"Dashboard data error for {job_title}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-assistant", methods=["POST"])
def ai_assistant():
    if blenderbot_model is None or tokenizer is None:
        return jsonify({"answer": "AI model not loaded."}), 500

    data = request.json
    job_title = data.get("jobTitle")
    user_question = data.get("question", "")

    job_details = model.get_job_details(job_title)
    if not job_details:
        return jsonify({"answer": "Sorry, I don't have enough data about this job title."}), 404

    # Compose a conversational prompt for BlenderBot
    context = (
        f"I want to become a {job_title}. "
        f"Skills required: {', '.join(job_details.get('Skills', []))}. "
        f"Important factors: {', '.join(job_details.get('Factors', []))}. "
        f"How to get this job: {', '.join(job_details.get('HowToGet', []))}. "
    )
    if user_question.strip():
        prompt = f"{context} {user_question.strip()} Please give me a friendly, step-by-step guide with practical advice and tips."
    else:
        prompt = f"{context} Please give me a friendly, step-by-step guide with practical advice and tips."

    try:
        inputs = tokenizer([prompt], max_length=512, return_tensors="pt", truncation=True).to(device)
        output_ids = blenderbot_model.generate(
            inputs['input_ids'],
            max_length=256,
            num_beams=4,
            early_stopping=True
        )
        answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
        return jsonify({"answer": "AI generation failed: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)