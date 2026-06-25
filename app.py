import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from parser import extract_text_from_input
from scorer import analyze_resume, score_for_ranking

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }
    .metric-box {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5c;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-excellent { color: #00ff88; }
    .score-strong    { color: #00bfff; }
    .score-good      { color: #ffd700; }
    .score-low       { color: #ff6b6b; }
    .skill-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        margin: 2px;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        padding-bottom: 4px;
        border-bottom: 2px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📄 AI Resume Screening System")
st.caption("Powered by Groq (LLaMA 3.3) · ATS scoring · Skill analysis · Candidate ranking")
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.success("✅ API key configured in scorer.py")
    st.markdown("---")
    st.markdown("### 📊 ATS Score Guide")
    st.markdown("🟢 **90–100** — Excellent Match")
    st.markdown("🔵 **80–89** — Strong Match")
    st.markdown("🟡 **70–79** — Good Match")
    st.markdown("🔴 **Below 70** — Needs Improvement")
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("This tool uses **LLaMA 3.3 70B** via Groq to semantically analyze resumes against job descriptions.")
    st.markdown("**Free tier:** 14,400 req/day")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_single, tab_bulk = st.tabs(["🔍 Single Resume Analysis", "🏆 Bulk Candidate Ranking"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Resume
# ═════════════════════════════════════════════════════════════════════════════
with tab_single:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-header">📋 Resume</p>', unsafe_allow_html=True)
        pdf_upload = st.file_uploader("Upload PDF", type=["pdf"], key="single_pdf")
        resume_paste = st.text_area(
            "…or paste resume text",
            height=320,
            placeholder="John Doe | Data Analyst\nSkills: Python, SQL, Power BI, Tableau\nExperience: 3 years at Acme Corp...",
            key="single_resume",
        )

    with col2:
        st.markdown('<p class="section-header">💼 Job Description</p>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "Paste job description",
            height=370,
            placeholder="Looking for a Data Analyst with:\n- Python and SQL proficiency\n- Power BI or Tableau\n- Communication skills...",
            key="single_jd",
        )

    st.markdown("")
    analyze_btn = st.button("✨ Analyze Resume", type="primary", use_container_width=True)

    if analyze_btn:
        resume_text = extract_text_from_input(pdf_upload, resume_paste)
        if not resume_text:
            st.warning("⚠️ Please upload a PDF or paste resume text.")
        elif not jd_text.strip():
            st.warning("⚠️ Please paste the job description.")
        else:
            with st.spinner("🤖 Analyzing with LLaMA 3.3 via Groq…"):
                try:
                    result = analyze_resume(resume_text, jd_text)
                except Exception as e:
                    st.error(f"❌ API error: {e}")
                    st.stop()

            score   = result.get("ats_score", 0)
            verdict = result.get("verdict", "")

            # Score color
            if score >= 90:   score_class = "score-excellent"
            elif score >= 80: score_class = "score-strong"
            elif score >= 70: score_class = "score-good"
            else:             score_class = "score-low"

            st.markdown("---")
            st.markdown("### 📊 Analysis Results")

            # ── Metric cards ──────────────────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🎯 ATS Score",       f"{score}%",  delta=verdict)
            m2.metric("✅ Matched Skills",  len(result.get("matched_skills", [])))
            m3.metric("❌ Missing Skills",  len(result.get("missing_skills", [])))
            m4.metric("⭐ Bonus Skills",    len(result.get("bonus_skills",   [])))

            st.progress(score / 100)
            st.markdown(f"**Verdict:** {verdict}")
            st.markdown("---")

            # ── Skills ────────────────────────────────────────────────────
            st.markdown("### 🛠️ Skill Breakdown")
            sk1, sk2, sk3 = st.columns(3)

            with sk1:
                st.markdown("**✅ Matched Skills**")
                matched = result.get("matched_skills", [])
                if matched:
                    for s in matched:
                        st.success(s)
                else:
                    st.caption("None found")

            with sk2:
                st.markdown("**❌ Missing Skills**")
                missing = result.get("missing_skills", [])
                if missing:
                    for s in missing:
                        st.error(s)
                else:
                    st.caption("None — great match!")

            with sk3:
                st.markdown("**⭐ Bonus Skills**")
                bonus = result.get("bonus_skills", [])
                if bonus:
                    for s in bonus:
                        st.info(s)
                else:
                    st.caption("None listed")

            # ── AI Feedback ───────────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 🤖 AI Feedback")
            f1, f2, f3 = st.columns(3)

            with f1:
                st.markdown("**💪 Strengths**")
                st.info(result.get("strengths", "N/A"))

            with f2:
                st.markdown("**⚠️ Gaps**")
                st.warning(result.get("gaps", "N/A"))

            with f3:
                st.markdown("**💡 Suggestions**")
                st.success(result.get("suggestions", "N/A"))

            # ── Download JSON report ──────────────────────────────────────
            st.markdown("---")
            import json
            report = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=report,
                file_name="ats_report.json",
                mime="application/json",
            )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — Bulk Ranking
# ═════════════════════════════════════════════════════════════════════════════
with tab_bulk:
    st.markdown('<p class="section-header">💼 Job Description (shared for all candidates)</p>', unsafe_allow_html=True)
    bulk_jd = st.text_area(
        "Paste JD",
        height=150,
        placeholder="Looking for a Data Analyst with Python, SQL, Power BI...",
        key="bulk_jd",
    )

    st.markdown("---")
    st.markdown("### 👥 Candidates")
    num_candidates = st.number_input(
        "Number of candidates", min_value=2, max_value=10, value=3, step=1
    )

    candidates = []
    for i in range(int(num_candidates)):
        with st.expander(f"👤 Candidate {i + 1}", expanded=(i < 2)):
            c1, c2 = st.columns([1, 2])
            with c1:
                name = st.text_input("Name", key=f"name_{i}", placeholder=f"e.g. Candidate {i+1}")
                pdf  = st.file_uploader("Upload PDF", type=["pdf"], key=f"pdf_{i}")
            with c2:
                text = st.text_area(
                    "…or paste resume",
                    height=150,
                    key=f"resume_{i}",
                    placeholder="Paste resume text here…",
                )
            candidates.append({"name": name or f"Candidate {i+1}", "pdf": pdf, "text": text})

    st.markdown("")
    rank_btn = st.button("🏆 Rank All Candidates", type="primary", use_container_width=True)

    if rank_btn:
        if not bulk_jd.strip():
            st.warning("⚠️ Please paste the job description.")
        else:
            results  = []
            progress = st.progress(0, text="Scoring candidates…")

            for idx, cand in enumerate(candidates):
                resume_text = extract_text_from_input(cand["pdf"], cand["text"])
                if not resume_text:
                    continue
                try:
                    score_data = score_for_ranking(resume_text, bulk_jd)
                    results.append({
                        "Rank":      0,
                        "Candidate": cand["name"],
                        "ATS Score": score_data.get("ats_score", 0),
                        "Verdict":   score_data.get("verdict", ""),
                    })
                except Exception as e:
                    results.append({
                        "Rank": 0, "Candidate": cand["name"],
                        "ATS Score": 0, "Verdict": f"Error: {e}"
                    })
                progress.progress((idx + 1) / len(candidates), text=f"Scored {cand['name']}…")

            progress.empty()

            if results:
                df = (pd.DataFrame(results)
                        .sort_values("ATS Score", ascending=False)
                        .reset_index(drop=True))
                df["Rank"] = df.index + 1

                st.markdown("---")
                st.markdown("### 🏆 Candidate Ranking")

                # Medal emojis for top 3
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                df["Rank"] = df["Rank"].apply(lambda r: f"{medals.get(r, str(r))} {r}")

                st.dataframe(
                    df[["Rank", "Candidate", "ATS Score", "Verdict"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ATS Score": st.column_config.ProgressColumn(
                            "ATS Score", min_value=0, max_value=100, format="%d%%"
                        )
                    },
                )

                top = results[0]  # already sorted
                st.success(f"🥇 Top candidate: **{top['Candidate']}** with **{top['ATS Score']}%** ATS score — {top['Verdict']}")

                # Download ranking CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Ranking (CSV)",
                    data=csv,
                    file_name="candidate_ranking.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No candidates had resume text to score.")