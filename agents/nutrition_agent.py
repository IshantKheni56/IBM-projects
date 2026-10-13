"""
Nutrition Agent — Core Agentic Logic
Orchestrates the multi-step nutrition planning workflow using IBM Granite LLM.
Implements the Agentic AI SDLC phases: Plan → Act → Observe → Reflect → Respond.
"""

import os
import re
from datetime import datetime
from .granite_client import call_granite
from .guardrails import (
    validate_user_profile,
    check_harmful_content,
    check_medical_referral,
    sanitize_input,
    get_medical_disclaimer,
    SUPPORTED_CONDITIONS
)

PLANS_DIR = os.path.join(os.path.dirname(__file__), "..", "plans")


# ─── Prompt Templates ────────────────────────────────────────────────────────

NUTRITION_PLAN_PROMPT = """You are NutriBot, a knowledgeable, empathetic, and ethical AI nutrition assistant powered by IBM Granite LLM. Your role is to provide safe, balanced, and personalised nutrition guidance following evidence-based dietary science.

AGENTIC TASK: Generate a comprehensive, personalised nutrition plan for the following individual.

USER PROFILE:
- Name: {name}
- Age: {age} years
- Gender: {gender}
- Diet Preference: {diet_preference}
- Medical Conditions: {medical_history}
- Food Allergies/Intolerances: {allergies}
- Health Goals: {goals}
- Location: {city}, {country}
- Activity Level: {activity_level}
- Current Weight (optional): {weight}
- Height (optional): {height}

INSTRUCTIONS:
1. Greet the user by name warmly and briefly.
2. Create a structured 7-day nutrition overview (highlight Day 1 in full detail with breakfast, mid-morning snack, lunch, afternoon snack, dinner, and late snack if needed).
3. Provide a daily calorie estimate and macronutrient breakdown (protein, carbs, fats, fibre).
4. Include a hydration guide (daily water intake recommendation).
5. List foods to include and foods to avoid or limit, relevant to their diet preference and medical conditions.
6. Provide culturally sensitive food suggestions appropriate for their location ({city}, {country}).
7. Include 3–5 practical lifestyle tips (sleep, stress, exercise alignment).
8. If the user has {medical_history}, include specific dietary adjustments tailored to that condition.
9. Maintain a respectful, encouraging, non-judgmental tone throughout.
10. Do NOT recommend supplements, medications, or treatments — focus only on whole foods and eating habits.
11. Use markdown formatting with clear headings, bullet points, and tables where appropriate.

ETHICAL GUARDRAILS:
- Do not promote extreme calorie restriction (< 1200 kcal/day for adults).
- Do not recommend any dangerous fasting regimes.
- Do not make disease-cure claims; only offer supportive dietary guidance.
- Acknowledge individual variability and recommend professional consultation.

Generate the complete nutrition plan now:"""


QUERY_ANSWER_PROMPT = """You are NutriBot, a friendly and knowledgeable AI nutrition assistant powered by IBM Granite LLM. You provide evidence-based, safe, and helpful answers to nutrition-related questions.

USER CONTEXT:
- Name: {name}
- Diet Preference: {diet_preference}
- Medical Conditions: {medical_history}
- Location: {city}, {country}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer the question clearly and concisely.
2. Base your answer on established nutritional science.
3. If the question is outside the scope of nutrition, politely redirect.
4. If the question relates to a specific medical condition, recommend consulting a healthcare professional for personalised advice.
5. Keep a warm, helpful, and encouraging tone.
6. Use bullet points or numbered lists for clarity when appropriate.
7. Limit your response to 300 words.

Answer:"""


# ─── Core Agent Functions ─────────────────────────────────────────────────────

def run_nutrition_agent(profile: dict) -> dict:
    """
    Main agentic pipeline:
    Phase 1 — Validate & Guardrail
    Phase 2 — Plan (build prompt)
    Phase 3 — Act (call IBM Granite LLM)
    Phase 4 — Observe (post-process output)
    Phase 5 — Respond (return structured response)
    """
    # ── Phase 1: Validate ──────────────────────────────────────────────────
    sanitized_profile = {k: sanitize_input(str(v)) for k, v in profile.items()}

    validation = validate_user_profile(sanitized_profile)
    if not validation["valid"]:
        return {
            "success": False,
            "errors": validation["errors"],
            "plan": None,
            "warnings": []
        }

    # ── Phase 2: Medical Referral Check ───────────────────────────────────
    warnings = []
    referral_check = check_medical_referral(sanitized_profile.get("medical_history", ""))
    if referral_check["requires_referral"]:
        warnings.append(referral_check["message"])

    # ── Phase 3: Build & Execute Prompt ───────────────────────────────────
    prompt = NUTRITION_PLAN_PROMPT.format(
        name=sanitized_profile.get("name", "User"),
        age=sanitized_profile.get("age", ""),
        gender=sanitized_profile.get("gender", "Not specified"),
        diet_preference=sanitized_profile.get("diet_preference", ""),
        medical_history=sanitized_profile.get("medical_history", "None"),
        allergies=sanitized_profile.get("allergies", "None"),
        goals=sanitized_profile.get("goals", "General wellness"),
        city=sanitized_profile.get("city", ""),
        country=sanitized_profile.get("country", ""),
        activity_level=sanitized_profile.get("activity_level", "Moderate"),
        weight=sanitized_profile.get("weight", "Not provided"),
        height=sanitized_profile.get("height", "Not provided"),
    )

    llm_response = call_granite(prompt, max_tokens=1400)

    # ── Phase 4: Observe & Post-Process ───────────────────────────────────
    plan_text = _post_process_plan(llm_response, sanitized_profile)

    # ── Phase 5: Save Plan ────────────────────────────────────────────────
    filename = _save_plan_to_markdown(plan_text, sanitized_profile)

    return {
        "success": True,
        "errors": [],
        "warnings": warnings,
        "plan": plan_text,
        "plan_file": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": sanitized_profile.get("name", "User")
    }


def run_query_agent(question: str, user_context: dict) -> dict:
    """
    Handles user Q&A using IBM Granite LLM with context from their profile.
    """
    # Guardrail check on the question
    harm_check = check_harmful_content(question)
    if not harm_check["safe"]:
        return {
            "success": False,
            "answer": harm_check["reason"],
            "is_safe": False
        }

    sanitized_question = sanitize_input(question)

    prompt = QUERY_ANSWER_PROMPT.format(
        name=user_context.get("name", "there"),
        diet_preference=user_context.get("diet_preference", "Not specified"),
        medical_history=user_context.get("medical_history", "None"),
        city=user_context.get("city", ""),
        country=user_context.get("country", ""),
        question=sanitized_question
    )

    answer = call_granite(prompt, max_tokens=500, temperature=0.5)

    return {
        "success": True,
        "answer": answer,
        "is_safe": True
    }


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _post_process_plan(raw_plan: str, profile: dict) -> str:
    """Append medical disclaimer and metadata to the plan."""
    disclaimer = get_medical_disclaimer()
    header = (
        f"# 🥗 Personalized Nutrition Plan\n"
        f"**Prepared for:** {profile.get('name', 'User')}  \n"
        f"**Generated on:** {datetime.now().strftime('%d %B %Y, %H:%M')}  \n"
        f"**Powered by:** IBM Granite LLM via watsonx.ai  \n\n"
        f"---\n\n"
    )
    return header + raw_plan + "\n\n" + disclaimer


def _save_plan_to_markdown(plan_text: str, profile: dict) -> str:
    """Save the nutrition plan to a .md file in the plans/ directory."""
    os.makedirs(PLANS_DIR, exist_ok=True)
    safe_name = re.sub(r'[^\w\-]', '_', profile.get("name", "user").lower())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nutrition_plan_{safe_name}_{timestamp}.md"
    filepath = os.path.join(PLANS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(plan_text)
    return filename
