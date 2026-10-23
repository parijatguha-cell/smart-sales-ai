import streamlit as st
from fpdf import FPDF


def _clean(text):
    """The built-in PDF font only supports basic characters, so swap the rest."""
    text = str(text)
    swaps = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "-", "\u20b9": "Rs ",
        "\u2026": "...",
    }
    for old, new in swaps.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def build_pdf(setup, evaluation):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def line(text, style="", size=11, gap=6):
        pdf.set_font("Helvetica", style, size)
        pdf.multi_cell(0, gap, _clean(text), new_x="LMARGIN", new_y="NEXT")

    line("Smart Sales AI - Performance Report", "B", 18, 10)
    pdf.ln(2)
    line(f"Salesperson: {setup.get('name', '')}")
    line(f"Scenario: {setup.get('scenario_type', '')}   |   Difficulty: {setup.get('difficulty', '')}")
    line(f"Overall score: {evaluation['total']}/{evaluation['max']}", "B", 13, 8)
    line(f"Questions answered: {evaluation['answered']}/{len(evaluation['results'])}")
    pdf.ln(3)

    line("Overall feedback", "B", 13, 8)
    line(evaluation["overall"])
    pdf.ln(3)

    line("Question-wise review", "B", 13, 8)
    for r in evaluation["results"]:
        pdf.ln(2)
        line(f"Question {r['index'] + 1} - Score {r['score']}/20", "B", 11)
        line(f"Customer: {r['question']}")
        line(f"Your answer: {r['answer'] or '(not answered)'}")
        line(f"Feedback: {r['feedback']}")
        if r["missing"]:
            line("Missing points:")
            for m in r["missing"]:
                line(f"  - {m}")

    return bytes(pdf.output())


def results_page():
    st.title("📊 Your Sales Practice Results")

    evaluation = st.session_state.get("evaluation")
    setup = st.session_state.get("setup")
    if not evaluation or not setup:
        st.info("No results yet. Go to Sales Practice, answer the questions, and click Evaluate interview.")
        return

    total, maximum = evaluation["total"], evaluation["max"]
    st.progress(total / maximum if maximum else 0, text=f"Overall performance: {total}/{maximum}")

    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 Overall score", f"{total}/{maximum}")
    c2.metric("📝 Questions", len(evaluation["results"]))
    c3.metric("✅ Answered", f"{evaluation['answered']}/{len(evaluation['results'])}")

    st.subheader("🧠 Overall AI feedback")
    st.write(evaluation["overall"])

    st.subheader("Detailed question review")
    for r in evaluation["results"]:
        with st.expander(f"Question {r['index'] + 1} · Score {r['score']}/20"):
            st.markdown(f"**Customer:** {r['question']}")
            st.markdown(f"**Your answer:** {r['answer'] or '_Not answered_'}")
            st.markdown(f"**Feedback:** {r['feedback']}")
            if r["missing"]:
                st.markdown("**Missing points:**")
                for m in r["missing"]:
                    st.markdown(f"- {m}")

    st.download_button(
        "📄 Download professional PDF report",
        data=build_pdf(setup, evaluation),
        file_name="smart_sales_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start a new interview", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("ans_") or k.startswith("stt_"):
                    del st.session_state[k]
            for k in ["questions", "answers", "evaluation", "q_index", "setup"]:
                st.session_state.pop(k, None)
            st.session_state.page = "Sales Practice"
            st.rerun()
    with col2:
        if st.button("✏️ Review answers", use_container_width=True):
            st.session_state.q_index = 0
            st.session_state.page = "Answer Screen"
            st.rerun()