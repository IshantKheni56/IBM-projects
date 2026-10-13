"""
Flask Application — Nutrition Agentic AI
Main entry point for the web server.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from agents.nutrition_agent import run_nutrition_agent, run_query_agent

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition-agent-secret-2024")
CORS(app)

PLANS_DIR = os.path.join(os.path.dirname(__file__), "plans")
os.makedirs(PLANS_DIR, exist_ok=True)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main single-page application."""
    return render_template("index.html")


@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    """
    Endpoint: Generate a personalized nutrition plan.
    Accepts JSON profile data, runs the agentic pipeline, returns the plan.
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "errors": ["No data received."]}), 400

        result = run_nutrition_agent(data)

        if not result["success"]:
            return jsonify(result), 422

        return jsonify({
            "success": True,
            "plan": result["plan"],
            "plan_file": result.get("plan_file", ""),
            "warnings": result.get("warnings", []),
            "user_name": result.get("user_name", ""),
            "timestamp": result.get("timestamp", "")
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


@app.route("/api/query", methods=["POST"])
def query_agent():
    """
    Endpoint: Answer a nutrition-related question using IBM Granite LLM.
    """
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        user_context = data.get("context", {})

        if not question:
            return jsonify({"success": False, "answer": "Please enter a question."}), 400

        if len(question) > 600:
            return jsonify({"success": False, "answer": "Question is too long. Please keep it under 600 characters."}), 400

        result = run_query_agent(question, user_context)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "answer": f"Server error: {str(e)}"
        }), 500


@app.route("/api/download-plan/<filename>")
def download_plan(filename):
    """
    Endpoint: Download a previously generated nutrition plan as a .md file.
    """
    # Security: allow only alphanumeric, underscore, hyphen, dot in filename
    import re
    if not re.match(r'^[\w\-\.]+\.md$', filename):
        return jsonify({"error": "Invalid filename."}), 400

    filepath = os.path.join(PLANS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Plan file not found."}), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype="text/markdown"
    )


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Nutrition Agentic AI",
        "model": "IBM Granite LLM",
        "version": "1.0.0"
    })


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    print("\n" + "="*60)
    print("  NutriBot - Nutrition Agentic AI (IBM Granite LLM)")
    print("="*60)
    print(f"  Server: http://localhost:{port}")
    print(f"  Model : IBM Granite (ibm/granite-13b-instruct-v2)")
    print(f"  Plans : {PLANS_DIR}")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
