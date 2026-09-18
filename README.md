# ResumeScreen AI — Intelligent ATS Screening & Candidate Evaluation Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0%2B-38B2AC?style=for-the-badge&logo=tailwind-css)

An enterprise-grade, high-aesthetic AI resume screening and recruitment analysis platform powered by **Google Gemini** (Gemini 2.5 Flash, 2.0 Flash, 1.5 Flash, 1.5 Pro) and **FastAPI**.

---

## ⚡ Highlights & Key Features

- 🎯 **Deep ATS Candidate Evaluation**: Objective scoring (0–100%) against target job descriptions with detailed gap analysis, key strengths, and missing qualifications.
- 🏆 **Executive Recruitment Verdict**: Automatically selects the top recommended candidate and analyzes strategic trade-offs across all applicants.
- 🗣️ **Tailored Technical Interview Questions**: Generates 3 targeted, gap-verifying technical interview questions with 1-click clipboard copying for hiring managers.
- 🛠️ **Actionable Resume Revisions**: Provides specific keyword additions, phrasing upgrades, and structural recommendations.
- 📊 **Interactive Candidate Scoreboard**: Real-time filtering (High Fit, Moderate Fit, Needs Review), search, and ranking medals (🥇 #1, 🥈 #2, 🥉 #3).
- 📑 **Comprehensive Document Support**: Parses both Adobe PDF (`.pdf`) and Microsoft Word (`.docx`) documents with OCR quality and scan-detection telemetry.
- 💾 **Local Evaluation Cache**: SHA-256 hashed persistent caching ensures instant sub-millisecond retrievals with zero duplicate API quota usage.
- 📥 **Executive Report Exports**: 1-click export to styled Microsoft Word (`.docx`) reports or print/save as clean PDF documents.
- 🎨 **State-of-the-Art UI**: Glassmorphism design system, ambient mesh glow, interactive sliders, quick job description presets, and dark/light themes.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- A Google Gemini API key ([Get a free key from Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Clone the Repository
```bash
git clone https://github.com/ayushbarve9/resume-screener.git
cd resume-screener
```

### 3. Configure API Key (Optional)
You can enter your API key directly into the web UI via the **"API Key"** header button, or configure it in a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Run the Dashboard
Run the automated one-click launcher (automatically manages `.venv` and dependencies):
```bash
python run.py
```

Open your browser and navigate to:
```
http://localhost:8000
```

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **AI / LLM Engine**: [Google GenAI SDK](https://github.com/google/generative-ai-python) with Structured JSON Output Schemas (`Pydantic v2`)
- **Document Extractors**: [PyPDF2](https://pypi.org/project/PyPDF2/) & [python-docx](https://python-docx.readthedocs.io/)
- **Frontend**: Vanilla HTML5/ES6, [Tailwind CSS CDN](https://tailwindcss.com/), [Lucide Icons](https://lucide.dev/), and Google Fonts (`Outfit`, `Plus Jakarta Sans`, `JetBrains Mono`)
- **Export Formatter**: [python-docx](https://python-docx.readthedocs.io/) for executive ATS evaluation summaries

---

## 📁 Project Structure

```
resume-screener/
├── main.py                  # FastAPI REST API endpoints and static file serving
├── config.py                # Model configurations, default thresholds, and prompt templates
├── evaluator.py             # Gemini API client, retry policies, and persistent cache
├── extractors.py            # PDF and DOCX text extraction with OCR heuristic detection
├── models.py                # Pydantic data schemas for structured outputs
├── report_generator.py      # Styled Word (.docx) executive report generator
├── run.py                   # Automated setup, venv management, and application launcher
├── requirements.txt         # Production Python package dependencies
├── index.html               # Single-page high-aesthetic responsive dashboard UI
└── README.md                # Project documentation and quick start guide
```

---

## 📜 License

MIT License. Free for personal, commercial, and educational use.