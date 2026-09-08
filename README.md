# 🎯 LLM-Based Profile Evaluator & Matcher

Learning to build with LLMs — and I shipped something live.

An automated AI resume screening application: paste a job description, upload a stack of candidate resumes, and get every profile parsed, evaluated, and ranked by match percentage — with detailed breakdowns of matched skills, missing criteria, and an automated recruiter verdict.

Built with Groq's high-speed inference engine (`openai/gpt-oss-120b`), strict Pydantic v2 structured schemas, document parsers (`pypdf`, `python-docx`), and a custom-styled Streamlit frontend.

---

## 💡 What I Actually Learned Building It

* **Structured outputs are easy. CONSISTENT structured outputs are the real work.**
  Initial tests showed scores fluctuating between runs on the same resume. Setting `temperature=0` helped stabilize the tokens, but prompt framing was the true bottleneck. Asking an LLM to arbitrarily "score a candidate from 0 to 100" creates inconsistent outputs[cite: 1]. The architecture works better when the model verifies factual criteria (individual skills, experience thresholds), while numerical aggregations and rankings are handled deterministically in code.

* **Batch processing requires deliberate rate management.**
  Moving from evaluating a single file to parsing multiple resumes simultaneously caused rapid API rate limits. Implementing sequential processing with pacing intervals (`time.sleep`) ensured high stability across multi-document batches without dropping client connections.

* **Frontend DOM isolation demands creative engineering.**
  Streamlit's default components present isolated shadow wrappers that often resist standard CSS overrides. Achieving the dark translucent UI required targeted CSS injection, string flattening to prevent unintended markdown block formatting, and a lightweight MutationObserver script to keep the layout clean.

---

## ✨ Features

* **Multi-Resume Batch Upload:** Supports concurrent upload of `.pdf` and `.docx` resumes.
* **Automated Candidate Leaderboard:** Automatically ranks and sorts evaluated candidates by match percentage in a unified table.
* **Granular Profile Breakdown:** Displays contact details, reported vs. required experience, matching skills, and missing technical competencies.
* **Strict Type Safety:** Pydantic models validate raw LLM JSON outputs into strict schema objects.
* **Visual Match Indicators:** Animated score rings and tags styled for quick recruitment screening.
* **Translucent Dark UI:** Custom responsive interface layered over an animated canvas.

---

## 🛠️ Tech Stack

| Layer | Tool / Library |
| :--- | :--- |
| **LLM Inference** | Groq API (`openai/gpt-oss-120b`) |
| **Structured Output** | Pydantic v2 |
| **Frontend UI** | Streamlit + Custom CSS / JS |
| **Document Ingestion** | `pypdf`, `python-docx` |
| **Environment / Runtime**| Python 3.10+, `python-dotenv` |

---

## 📸 Architecture Pipeline

```text
       Upload Multiple Resumes (PDF / DOCX)
                         +
               Paste Job Description
                         ↓
    [LLM Call 1] Analyze JD → Structured JobD Object
                         ↓
           For Each Candidate Resume:
   ┌─────────────────────────────────────────────────┐
   │ 1. Extract raw text via pypdf / python-docx     │
   │ 2. [LLM Call 2] Parse Resume → Resume Object    │
   │ 3. Buffer delay (Rate-limit preservation)       │
   │ 4. [LLM Call 3] Cross-evaluate JobD vs Resume   │
   │ 5. Yield MatchResult (Score, Skills, Verdict)   │
   └─────────────────────────────────────────────────┘
                         ↓
  Sort Descending by Score → Generate Dynamic Leaderboard
                         ↓
          Render Detailed Breakdown per Candidate
