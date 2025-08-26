from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import torch
import model  # your own model (model.py)
import pandas as pd
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask_app")

# --- Flask App Setup (serve React build) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates"),
)
CORS(app)

# --- Qwen AI Model Setup ---
class QwenChatbot:
    def __init__(self, model_name="Qwen/Qwen3-0.6B"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.history = []

    def generate_response(self, user_input):
        messages = self.history + [{"role": "user", "content": user_input}]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self.tokenizer(text, return_tensors="pt")
        response_ids = self.model.generate(
            **inputs,
            max_new_tokens=512 
        )[0][len(inputs.input_ids[0]):].tolist()
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})
        return response

try:
    qwen_bot = QwenChatbot()
    logger.info("Loaded Qwen model successfully.")
except Exception as e:
    logger.error(f"Failed to load Qwen model: {e}")
    qwen_bot = None

# --- React frontend route ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Serve React build (index.html for SPA routes)"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return render_template("index.html")

# --- API Routes ---
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
        honor_grade = subset['Honor Grade of Degree'].value_counts().to_dict() if 'Honor Grade of Degree' in subset.columns else {}

        if "Date of current appointment " in subset.columns:
            years = pd.to_datetime(subset["Date of current appointment "], errors="coerce").dt.year
            year_counts = years.value_counts().sort_index().to_dict()
        else:
            year_counts = {}

        return jsonify({
            "sector_counts": sector_counts,
            "dept_counts": dept_counts,
            "degree_counts": degree_counts,
            "honor_grade": honor_grade,
            "year_counts": year_counts,
            "total_count": len(subset)
        })
    except Exception as e:
        logger.error(f"Dashboard data error for {job_title}: {e}")
        return jsonify({"error": str(e)}), 500

# @app.route('/api/summary-ai', methods=['POST'])
# def summary_ai():
#     """
#     Generates a summary for a given job title using the LLM.
#     Expects JSON: { "jobTitle": "...", "summaryType": "skills" | "factors" | "howToGet" }
#     Returns: { "summary": ... }
#     """
#     data = request.json
#     job_title = data.get("jobTitle")
#     summary_type = data.get("summaryType")

#     if not job_title or not summary_type:
#         return jsonify({"summary": "Missing jobTitle or summaryType"}), 400

#     job_details = model.get_job_details(job_title) or {}

#     # Get specific context for the summary type
#     skills = ', '.join(job_details.get('Skills', []))
#     factors = ', '.join(job_details.get('Factors', []))
#     how_to_get = ', '.join(job_details.get('HowToGet', []))

#     # Build prompt according to summary type
#     if summary_type == "skills":
#         prompt = (
#             f"List and briefly explain the key skills required to become a {job_title}. "
#             f"Skills from dataset: {skills}. "
#             f"Provide a professional, practical summary."
#         )
#     elif summary_type == "factors":
#         prompt = (
#             f"List and briefly explain the important factors for succeeding as a {job_title}. "
#             f"Factors from dataset: {factors}. "
#             f"Provide a professional, practical summary."
#         )
#     elif summary_type == "howToGet":
#         prompt = (
#             f"List and briefly explain the best ways to become a {job_title}. "
#             f"How to get this job from dataset: {how_to_get}. "
#             f"Provide a professional, practical summary."
#         )
#     else:
#         prompt = (
#             f"I want to become a {job_title}. "
#             f"Skills required: {skills}. "
#             f"Important factors: {factors}. "
#             f"How to get this job: {how_to_get}. "
#             f"Act as a professional {job_title}, provide practical advice and tips."
#         )

#     try:
#         answer = qwen_bot.generate_response(prompt)
#         return jsonify({"summary": answer})
#     except Exception as e:
#         logger.error(f"Summary AI error: {e}")
#         return jsonify({"summary": f"AI generation failed: {e}"}), 500

@app.route("/api/ai-assistant", methods=["POST"])
def ai_assistant():
    if qwen_bot is None:
        return jsonify({"answer": "AI model not loaded."}), 500

    data = request.json
    job_title = data.get("jobTitle")
    user_question = data.get("question", "").strip()

    job_details = model.get_job_details(job_title)
    if not job_details:
        return jsonify({"answer": "Sorry, I don't have enough data about this job title."}), 404

    # --- Case 1: No question asked → show ML-provided summary ---
    if not user_question:
        summary = (
            f"**{job_title} Profile Summary**\n\n"
            f"**Skills Required:** {', '.join(job_details.get('Skills', [])) or 'N/A'}\n"
            f"**Important Factors:** {', '.join(job_details.get('Factors', [])) or 'N/A'}\n"
            f"**How to Get This Job:** {', '.join(job_details.get('HowToGet', [])) or 'N/A'}"
        )
        return jsonify({"answer": summary})

    # --- Case 2: User asked a question → AI generates fresh advice ---
    prompt = (
        f"I want to become a {job_title}. "
        f"{user_question} "
        f"Please provide a professional, step-by-step guide with practical advice and tips."
    )

    try:
        answer = qwen_bot.generate_response(prompt)
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
        return jsonify({"answer": "AI generation failed: " + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
