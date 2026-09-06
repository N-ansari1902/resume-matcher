# 🎯 AI Resume Matcher

An intelligent resume screening tool that **automatically parses resumes, analyses job descriptions, and calculates a match score** — all from a clean 3D glassmorphism web interface.

Built with Groq's ultra-fast LLaMA 3.3 inference, Pydantic structured outputs, and Streamlit.

---

## ✨ Features

- 📄 Upload PDF or DOCX resumes
- 💼 Paste any job description
- 🤖 AI-powered structured parsing (Pydantic models ensure clean output)
- 🎯 Visual match score with animated ring indicator
- ✅ Matching skills & ❌ missing skills breakdown
- 📋 AI-generated recruiter verdict
- 🌑 3D glassmorphism dark UI

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM inference | Groq API (LLaMA 3.3 70B) |
| Structured output | Pydantic v2 |
| Web interface | Streamlit |
| PDF parsing | pypdf |
| DOCX parsing | python-docx |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/resume-matcher.git
cd resume-matcher

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Launch
streamlit run app.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

---

## 🌐 Live Demo

[▶ Try it live →](https://YOUR_APP_NAME.streamlit.app)

---

## 📸 How it Works

```
Upload Resume (PDF/DOCX)
        +
  Paste Job Description
        ↓
  [LLM Call 1] Parse resume → structured Resume object
  [LLM Call 2] Parse JD    → structured JobD object
  [LLM Call 3] Compare both → match score + skill breakdown
        ↓
   Visual results with score ring, skill tags, verdict
```

---

*Built as part of an AI Engineering learning journey.*
