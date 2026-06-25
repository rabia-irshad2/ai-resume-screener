#  AI Resume Screener

An AI-powered tool that scores how well a resume matches a job description — instantly, using LLaMA 3.3 70B via the Groq API. Built as an early MVP to test a product idea: **can AI replace the first-pass manual resume screening that recruiters and hiring managers do every day?**

 **Live demo:** [ai-resume-screener-mgzhqpn7dboita2eksc8kw.streamlit.app](https://ai-resume-screener-mgzhqpn7dboita2eksc8kw.streamlit.app/)
 **Demo video:** [Add link if you post one]

---

##  The Problem

Recruiters and hiring managers spend hours manually comparing resumes against job descriptions — checking for keyword matches, missing skills, and overall fit. It's repetitive, inconsistent across reviewers, and doesn't scale when you have 50+ applicants for one role.

This project tests whether an LLM can do that first-pass screening reliably, instantly, and for free.

##  What It Does

###  Single Resume Analysis
Upload a resume (PDF or pasted text) + a job description, and get back:
- **ATS Score** (0–100%)
- **Matched Skills** — present in both resume and JD
- **Missing Skills** — required by the JD but absent from the resume
- **Bonus Skills** — relevant skills the candidate has beyond what was asked
- **AI-generated feedback** — strengths, gaps, and actionable suggestions
- **Verdict** — Excellent Match → Needs Improvement
- Downloadable full report (JSON)

###  Bulk Candidate Ranking
Paste one job description, add 2–10 candidates, and get an automatically sorted leaderboard with ATS scores and verdicts — exportable as CSV.

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| AI Model | LLaMA 3.3 70B (via [Groq API](https://groq.com)) |
| PDF Parsing | Custom Python parser |
| Hosting | Streamlit Community Cloud |
| Secrets Management | Streamlit Secrets (cloud) / `.env` (local) |

##  How It Works

```
Resume + Job Description (PDF or text)
        ↓
parser.py → extracts plain text
        ↓
scorer.py → builds a structured prompt → sends to Groq's LLaMA 3.3 70B
        ↓
Groq returns a JSON-structured analysis
        ↓
app.py (Streamlit) → renders scores, skill tags, and feedback
```

The AI is prompted to act as an ATS analyst and return a strict JSON schema (score, matched/missing/bonus skills, strengths, gaps, suggestions, verdict), which the app then parses and visualizes.

##  Running It Locally

```bash
git clone https://github.com/rabia-irshad2/ai-resume-screener.git
cd ai-resume-screener/streamlit-version
pip install -r requirements.txt
```

Create a `.env` file in the project folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

Then run:
```bash
streamlit run app.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) — the free tier includes 14,400 requests/day.

##  Project Status

This is an early-stage MVP built to validate the core idea — automated, AI-driven resume-to-JD matching. Possible next steps:
- Batch resume upload (folder/zip support)
- Support for `.docx` resumes
- Custom scoring weights per role/industry
- Multi-language resume support
- User accounts and saved screening history

## Feedback Welcome

This is a work-in-progress product idea — if you're a recruiter, hiring manager, or job seeker with thoughts on what would make this genuinely useful, I'd love to hear them.

---

*Built with Python, Streamlit, and the Groq API.*
