<div align="center">

# 🥗 NutriBot — Nutrition Agentic AI

### Powered by IBM Granite LLM · watsonx.ai

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask)](https://flask.palletsprojects.com)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-0f62fe?logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![IBM Granite](https://img.shields.io/badge/IBM%20Granite-13B%20LLM-6929c4)](https://www.ibm.com/granite)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**An ethical, agentic AI web application that generates personalised nutrition plans using IBM Granite LLM, following IBM AI Ethics principles and full Agentic AI SDLC.**

[✨ Features](#-features) · [🚀 Quick Start](#-quick-start) · [🏗️ Architecture](#️-architecture) · [🤖 IBM Granite Setup](#-ibm-granite-llm-setup) · [📁 Project Structure](#-project-structure) · [🛡️ Ethical AI](#️-ethical-ai--guardrails)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **IBM Granite LLM** | `ibm/granite-13b-instruct-v2` via watsonx.ai REST API |
| 👤 **User Profile Collection** | Name, age, gender, diet preference, medical history, location, allergies, activity level |
| 🎯 **Personalised Plans** | 7-day meal plans with calories, macros, hydration, and lifestyle tips |
| 🛡️ **Ethical Guardrails** | Blocks harmful content, extreme diets, dangerous patterns |
| 🩺 **Medical Referral** | Auto-flags complex conditions for professional consultation |
| 💬 **Agentic Q&A Chat** | Context-aware IBM Granite-powered nutrition chatbot |
| 📥 **Export to .md** | Download plans as Markdown files with medical disclaimer |
| 🌐 **Responsive Web UI** | Multi-step form with progress indicator — works on all devices |
| 🔒 **Demo Mode** | Runs without API credentials (rich pre-built responses) |
| ⚕️ **Medical Disclaimer** | Auto-appended to every generated plan |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** — [Download here](https://www.python.org/downloads/) *(tick "Add to PATH")*
- **Git** — [Download here](https://git-scm.com/downloads)
- **IBM watsonx.ai account** — [Sign up free](https://cloud.ibm.com/registration) *(optional — app works in Demo Mode without it)*

---

### Option A: One-Click Windows Launch (Recommended)

```
1. Clone this repository
2. Navigate to the nutrition-agent folder
3. Double-click  run.bat
```

The launcher automatically:
- ✅ Checks your Python installation
- ✅ Creates an isolated virtual environment (`venv/`)
- ✅ Installs all dependencies from `requirements.txt`
- ✅ Starts the Flask server on port 5000
- ✅ Opens your browser at **http://localhost:5000**

---

### Option B: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/IshantKheni56/IBM-projects.git
cd IBM-projects/nutrition-agent

# 2. Create & activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials (optional — skip for Demo Mode)
copy .env.example .env
# Edit .env and add your WATSONX_API_KEY and WATSONX_PROJECT_ID

# 5. Run the application
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (SPA)                        │
│   Multi-step Form (3 steps) + Markdown Plan + Chat UI       │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP / JSON
┌──────────────────────────▼──────────────────────────────────┐
│              Flask REST API  (app.py)                        │
│  POST /api/generate-plan  │  POST /api/query                 │
│  GET  /api/download-plan  │  GET  /api/health                │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │       Nutrition Agent            │
          │    (agents/nutrition_agent.py)   │
          │                                  │
          │  Phase 1 — VALIDATE              │
          │  Phase 2 — GUARDRAIL CHECK       │
          │  Phase 3 — BUILD PROMPT          │
          │  Phase 4 — CALL IBM GRANITE LLM  │
          │  Phase 5 — POST-PROCESS          │
          │  Phase 6 — SAVE .md + RESPOND    │
          └────────┬──────────────┬──────────┘
                   │              │
     ┌─────────────▼──┐  ┌────────▼──────────────┐
     │   Guardrails    │  │  IBM Granite Client    │
     │  (guardrails.py)│  │  (granite_client.py)   │
     │                 │  │                        │
     │ • Harm patterns │  │ • IAM token exchange   │
     │ • Med referral  │  │ • Granite REST API     │
     │ • Input valid.  │  │ • Demo mode fallback   │
     └─────────────────┘  └───────────┬────────────┘
                                      │
                          ┌───────────▼───────────┐
                          │   IBM watsonx.ai        │
                          │  granite-13b-instruct   │
                          └───────────────────────┘
```

### Agentic AI Pipeline

```
User Input → [Validate] → [Guardrail] → [Plan Prompt] → [Act: Granite LLM]
          → [Observe: Post-process] → [Reflect: Add disclaimer] → [Respond: UI + .md]
```

---

## 🤖 IBM Granite LLM Setup

### Step 1 — Create IBM Cloud Account
👉 https://cloud.ibm.com/registration

### Step 2 — Create Watson Machine Learning Service
- Go to IBM Cloud Catalog → search "Watson Machine Learning"
- Create a Lite (free) instance

### Step 3 — Create a watsonx.ai Project
👉 https://dataplatform.cloud.ibm.com/
- Click "New project" → fill in details → associate your WML service

### Step 4 — Get Your API Key
👉 https://cloud.ibm.com/iam/apikeys
- Click "Create an IBM Cloud API key" → copy the key

### Step 5 — Get Your Project ID
- In watsonx.ai → your project → **Manage** tab → **General** → copy **Project ID**

### Step 6 — Configure `.env`

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> **Note:** Without credentials the app runs in **Demo Mode** — it returns rich, pre-built sample nutrition plans so the application can be fully demonstrated and tested without an IBM account.

---

## 📁 Project Structure

```
nutrition-agent/
│
├── app.py                    # Flask web application & REST API endpoints
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── run.bat                   # Windows one-click launcher
├── install.bat               # Dependency installer only
├── README.md                 # This file
│
├── agents/
│   ├── __init__.py
│   ├── nutrition_agent.py    # Core agentic pipeline & IBM Granite prompt engineering
│   ├── granite_client.py     # IBM Granite LLM REST API client
│   └── guardrails.py         # Ethical AI: harm detection, validation, medical referral
│
├── templates/
│   └── index.html            # Single-page web application (3-step form + chat)
│
├── static/
│   ├── css/
│   │   └── style.css         # IBM Design System inspired responsive stylesheet
│   └── js/
│       └── app.js            # Client-side form, plan rendering, chat logic
│
└── plans/                    # Auto-generated nutrition plans (*.md files)
    └── nutrition_plan_*.md
```

---

## 🛡️ Ethical AI & Guardrails

NutriBot implements **IBM's AI Ethics Principles**:

### Harm Prevention
Automatically detects and blocks input containing:
- Dangerous fasting / starvation language
- Extreme calorie restriction (< 500 kcal prompts)
- Supplement/medication abuse patterns
- Self-harm content

### Medical Professional Referral
Complex conditions trigger an automatic referral warning:
> Cancer · Chemotherapy · Kidney/Liver Failure · Eating Disorders (Anorexia, Bulimia) · Dialysis · Transplant · PKU

### HAM Principles (Helpful · Accurate · Mindful)
| Principle | Implementation |
|-----------|---------------|
| **Helpful** | Actionable meal plans, portion sizes, recipe ideas, lifestyle tips |
| **Accurate** | Evidence-based dietary science, no unsubstantiated claims |
| **Mindful** | Non-judgmental tone, culturally sensitive (location-aware food suggestions), inclusive |

### Transparency
- Always identifies as an AI (NutriBot / IBM Granite LLM)
- Demo Mode is clearly labelled
- Source model displayed in every plan header

---

## ⚕️ Medical Disclaimer

> **IMPORTANT:** This nutrition plan is generated by an AI system (IBM Granite LLM) for **informational and educational purposes only**. It does **NOT** constitute medical advice, diagnosis, or treatment.
>
> Always consult a **registered dietitian (RD)**, **nutritionist**, or **licensed physician** before making significant dietary changes. If you have a medical condition, your healthcare provider should review and approve any nutrition plan.

*This disclaimer is automatically appended to every generated `.md` plan file.*

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Serve the web application |
| `POST` | `/api/generate-plan` | Generate personalised nutrition plan |
| `POST` | `/api/query` | Answer nutrition question (chat agent) |
| `GET`  | `/api/download-plan/<filename>` | Download plan as `.md` file |
| `GET`  | `/api/health` | Health check |

### POST `/api/generate-plan` — Request Body
```json
{
  "name": "Priya Sharma",
  "age": "32",
  "gender": "Female",
  "city": "Mumbai",
  "country": "India",
  "diet_preference": "Vegetarian",
  "medical_history": "Diabetes, High Blood Pressure",
  "allergies": "None",
  "weight": "68 kg",
  "height": "162 cm",
  "activity_level": "Moderate",
  "goals": "Manage Diabetes, Improve Energy"
}
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows

# Run validation tests
python -c "
from agents.guardrails import validate_user_profile, check_harmful_content, check_medical_referral
print('Running guardrail tests...')
assert validate_user_profile({'name':'Test','age':'30','diet_preference':'Vegetarian','city':'Delhi','country':'India'})['valid']
assert not check_harmful_content('how to starve myself')['safe']
assert check_medical_referral('I have cancer')['requires_referral']
print('All tests PASSED')
"
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `flask` | 3.0.3 | Web framework & REST API |
| `flask-cors` | 4.0.1 | Cross-origin resource sharing |
| `requests` | 2.31.0 | IBM watsonx.ai REST API calls |
| `python-dotenv` | 1.0.1 | Environment variables from `.env` |
| `markdown` | 3.6 | Markdown processing |

---

## 📋 Agentic AI SDLC Phases

| Phase | Description | Status |
|-------|-------------|--------|
| **1. Requirements** | User personas, ethical constraints, model selection | ✅ Complete |
| **2. Design** | Multi-step UI, agent pipeline, guardrails architecture | ✅ Complete |
| **3. Development** | Flask backend, Granite client, agent, guardrails, frontend | ✅ Complete |
| **4. Testing** | Input validation, harm detection, medical referral, API | ✅ 13/13 Tests |
| **5. Deployment** | Local via `.bat`, venv isolation, `.env` config | ✅ Complete |
| **6. Ethics & Monitoring** | Disclaimer, guardrails, professional referral | ✅ Complete |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**NutriBot** · IBM Granite LLM · watsonx.ai · Built following IBM AI Ethics Principles

*Always consult a qualified healthcare professional before making dietary changes.*

</div>
