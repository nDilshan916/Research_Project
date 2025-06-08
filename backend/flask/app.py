from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import model  # your own model (model.py)
import pandas as pd
from collections import Counter

app = Flask(__name__)
CORS(app)

# Use the much better Gemma 2B Instruct model!
MODEL_NAME = "google/gemma-2b-it"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
gemma_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32  # Use float32 for CPU; use float16 if you have a GPU with enough VRAM
)

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


@app.route("/api/ai-assistant", methods=["POST"])
def ai_assistant():
    data = request.json
    job_title = data.get("jobTitle")
    user_question = data.get("question", "")

    # Get job details
    job_details = model.get_job_details(job_title)
    if not job_details:
        return jsonify({"answer": "Sorry, I don't have enough data about this job title."}), 404

    skills = ', '.join(job_details.get("Skills", []))
    factors = ', '.join(job_details.get("Factors", []))
    how_to_get = ', '.join(job_details.get("HowToGet", []))

    # Build a focused, instructional prompt for Gemma Instruct
    prompt = (
        f"<start_of_turn>user\n"
        f"Job Title: {job_title}\n\n"
        f"Skills required: {skills}\n"
        f"Important factors: {factors}\n"
        f"How to get this job: {how_to_get}\n\n"
    )
    if user_question.strip():
        prompt += f"Question: {user_question.strip()}\n\n"

    prompt += (
        "Please provide a detailed, step-by-step guide for this question. "
        "Include practical steps, resume tips, and where to find jobs if relevant.\n"
        "<end_of_turn>\n<start_of_turn>model\n"
    )

    # Generate with Gemma 2B-Instruct
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        output_ids = gemma_model.generate(
            input_ids,
            max_new_tokens=300,
            temperature=0.8,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    answer = generated_text[len(prompt):].strip() if generated_text.startswith(prompt) else generated_text.strip()

    # Optional: Remove repeated lines and "Contact Information" hallucinations
    answer_lines = []
    seen = set()
    for line in answer.split('\n'):
        if line.strip() and line not in seen and not line.strip().lower().startswith("contact information"):
            answer_lines.append(line)
            seen.add(line)
    answer = "\n".join(answer_lines)

    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True)