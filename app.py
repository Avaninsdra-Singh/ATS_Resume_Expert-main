# app.py

import json
from pathlib import Path

import streamlit as st
from src.ai.gemini_handler import get_ai_evaluation, get_ai_configuration, parse_ai_response
from src.logic.quality_check import evaluate_quality
from src.logic.score_engine import evaluate_resume
from src.parser.resume_parser import extract_resume_sections
from src.utils.explainability import show_explanation
from src.utils.file_handler import read_pdf_file
from src.utils.pdf_report import generate_pdf_report


# Page config
st.set_page_config(page_title="ATS Resume Expert", layout="wide")
project_root = Path(__file__).resolve().parent
style_path = project_root / "assets" / "styles.css"
if style_path.exists():
    st.markdown("<style>" + style_path.read_text() + "</style>", unsafe_allow_html=True)


# Initialize session state for page routing
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"


# Sidebar or session-driven navigation
pages = ["🏠 Home", "📄 Evaluate Resume", "📊 Resume Ranking"]
if st.session_state.current_page == "🏠 Home":
    selected_page = st.sidebar.radio("Go to", pages)
else:
    selected_page = st.session_state.current_page
    selected_page = st.sidebar.radio("Go to", pages, index=pages.index(selected_page))

st.session_state.current_page = selected_page  # keep synced


# ------------------ HOME PAGE ------------------
if selected_page == "🏠 Home":
    st.title("📄 ATS Resume Expert")
    st.markdown(
        """
        Welcome to **ATS Resume Expert**, the ultimate tool to match resumes with job descriptions using advanced logic and AI.
        \n➡️ Navigate to other sections using the sidebar.
        """
    )

    ai_config = get_ai_configuration()
    if ai_config["openai_api_key_set"] or ai_config["gemini_api_key_set"]:
        provider = "OpenAI" if ai_config["openai_api_key_set"] else "Gemini"
        st.success(f"AI provider configured: {provider}")
    else:
        st.warning("No AI API key configured. Set OPENAI_API_KEY or GEMINI_API_KEY in your .env file.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Evaluating", use_container_width=True):
            st.session_state.current_page = "📄 Evaluate Resume"
            st.rerun()


# ------------------ SINGLE RESUME EVALUATION ------------------
elif selected_page == "📄 Evaluate Resume":
    st.title("📄 ATS Resume Evaluation")
    st.markdown("Upload a resume and a job description to get an ATS-style evaluation (Hybrid: Logic + AI).")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jd_input = st.text_area("Paste Job Description Here", height=200)

    if uploaded_file and jd_input and st.button("Evaluate Resume"):
        with st.spinner("📄 Reading resume..."):
            resume_text = read_pdf_file(uploaded_file)
            resume_sections = extract_resume_sections(resume_text)

        with st.spinner("🧠 Running logic-based analysis..."):
            logic_score, matched_skills, required_skills = evaluate_resume(resume_sections, jd_input)
            quality_score = evaluate_quality(resume_sections)
            final_logic_score = min(100, logic_score + (quality_score * 0.3))
            logic_explain = show_explanation(final_logic_score, matched_skills, required_skills)

        with st.spinner("🤖 Asking AI for comparison..."):
            ai_result = get_ai_evaluation(resume_text, jd_input)

        st.subheader("✅ Logic-Based ATS Evaluation")
        st.markdown(f"**Score:** {final_logic_score:.2f} / 100")
        st.success("✔️ Good Match" if final_logic_score >= 60 else "❌ Needs Improvement")

        with st.expander("🔍 View Matched & Missing Skills"):
            st.write("**Matched Skills:**", logic_explain["Matched Skills"])
            st.write("**Missing Skills:**", logic_explain["Missing Skills"])

        st.subheader("💡 AI-Powered Insight")

        try:
            parsed_ai = parse_ai_response(ai_result)
            score = parsed_ai.get("score", "N/A")
            score_value = None
            if isinstance(score, (int, float)):
                score_value = float(score)
            elif isinstance(score, str):
                try:
                    score_value = float(score)
                except (TypeError, ValueError):
                    score_value = None

            score_text = "N/A"
            score_display = score if score_value is None else int(score_value)
            if score_value is not None:
                score_color = "#0D47A1" if score_value >= 60 else "#B71C1C"
                score_text = "✔️ Good Match" if score_value >= 60 else "❌ Needs Improvement"
                st.markdown(
                    f"""
                    <div style='background-color:{score_color}; padding:16px; border-radius:10px; text-align:center; color:white; font-size:20px; font-weight:bold;'>
                    🧠 AI Match Score: {score_display}/100 — {score_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("AI returned a result but the score could not be interpreted.")

            if parsed_ai.get("error"):
                st.warning(parsed_ai["error"])

            strengths = parsed_ai.get("strengths", [])
            if strengths:
                st.markdown("### ✅ Key Strengths")
                for s in strengths:
                    st.markdown(
                        f"""
                        <div style='background-color:#f0fff4; color:#1b5e20; padding:12px; margin:6px 0; border-left:5px solid #2e7d32; border-radius:6px;'>
                            <strong>✔️</strong> {s}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            gaps = parsed_ai.get("gaps", [])
            if gaps:
                st.markdown("### ⚠️ Areas for Improvement")
                for g in gaps:
                    st.markdown(
                        f"""
                        <div style='background-color:#fff8e1; color:#bf360c; padding:12px; margin:6px 0; border-left:5px solid #f57c00; border-radius:6px;'>
                            <strong>⚠️</strong> {g}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with st.expander("📄 Show Raw AI Response (optional)"):
                st.code(json.dumps(parsed_ai, indent=2))

            if uploaded_file and parsed_ai:
                pdf_bytes = generate_pdf_report(
                    resume_name=uploaded_file.name,
                    logic_score=final_logic_score,
                    logic_explain=logic_explain,
                    ai_score=score_value if score_value is not None else 0,
                    strengths=parsed_ai.get("strengths", []),
                    gaps=parsed_ai.get("gaps", []),
                )

                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_ATS_Report.pdf",
                    mime="application/pdf",
                )

        except Exception as exc:
            st.error(f"❌ Could not parse AI output: {exc}")
            st.info(ai_result)


# ------------------ RESUME RANKING (AI ONLY) ------------------
elif selected_page == "📊 Resume Ranking":
    st.title("📊 Resume Ranking (AI-Based Only)")
    st.markdown("Upload multiple resumes and a job description. The system will rank resumes based on how well they match the JD using AI.")

    bulk_files = st.file_uploader("Upload Multiple Resumes (PDFs)", type=["pdf"], accept_multiple_files=True)
    bulk_jd = st.text_area("Paste Job Description for Ranking", height=200)

    if bulk_files and bulk_jd and st.button("Rank Resumes"):
        with st.spinner("🔍 Evaluating all resumes using AI..."):
            ai_rankings = []

            for resume_file in bulk_files:
                resume_text = read_pdf_file(resume_file)
                ai_result_raw = get_ai_evaluation(resume_text, bulk_jd)
                ai_payload = parse_ai_response(ai_result_raw)

                if ai_payload.get("error"):
                    st.warning(f"⚠️ {resume_file.name}: {ai_payload['error']}")
                    continue

                score = ai_payload.get("score", 0)
                if isinstance(score, str):
                    try:
                        score = float(score)
                    except (TypeError, ValueError):
                        score = 0

                ai_rankings.append(
                    {
                        "name": resume_file.name,
                        "score": score,
                        "strengths": ai_payload.get("strengths", []),
                        "gaps": ai_payload.get("gaps", []),
                    }
                )

            if ai_rankings:
                ai_rankings.sort(key=lambda x: x["score"], reverse=True)

                st.subheader("🏆 Ranked Resumes:")
                for idx, resume in enumerate(ai_rankings, start=1):
                    st.markdown(f"### {idx}. {resume['name']} — **Score: {resume['score']}**")
                    with st.expander("🔍 View Details"):
                        st.write("**Strengths:**", resume["strengths"])
                        st.write("**Gaps:**", resume["gaps"])
            else:
                st.warning("⚠️ No valid AI responses to display.")
