import streamlit as st
from streamlit_mic_recorder import speech_to_text
from utils.ai_engine import evaluate_answers


def answer_page():
    questions = st.session_state.get("questions")
    if not questions:
        st.warning("No questions yet. Go to Sales Practice and generate questions first.")
        return

    total = len(questions)
    i = st.session_state.get("q_index", 0)
    answers = st.session_state.setdefault("answers", {})
    key = f"ans_{i}"

    if key not in st.session_state:
        st.session_state[key] = answers.get(i, "")

    st.progress((i + 1) / total, text=f"Question {i + 1} of {total}")

    with st.container(border=True):
        st.caption(f"CUSTOMER QUESTION {i + 1:02d}")
        st.markdown(f"### {questions[i]}")

    st.write("🎙️ Speak your answer (Chrome works best), or type it below.")
    spoken = speech_to_text(
        language="en",
        start_prompt="🎙️ Start recording",
        stop_prompt="⏹️ Stop recording",
        use_container_width=True,
        just_once=True,
        key=f"stt_{i}",
    )
    if spoken:
        st.session_state[key] = (st.session_state[key] + " " + spoken).strip()

    text = st.text_area(
        "Your answer (you can edit the transcript)",
        key=key,
        height=160,
        placeholder="Record your answer above or type here...",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save answer", use_container_width=True):
            answers[i] = text
            st.success("Answer saved.")

    with col2:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(i == 0)):
            answers[i] = text
            st.session_state.q_index = i - 1
            st.rerun()

    with col3:
        if i < total - 1:
            if st.button("Next question ➡️", use_container_width=True):
                answers[i] = text
                st.session_state.q_index = i + 1
                st.rerun()
        else:
            if st.button("📊 Evaluate interview", use_container_width=True):
                answers[i] = text
                with st.spinner("Gemini is scoring your answers..."):
                    try:
                        st.session_state.evaluation = evaluate_answers(
                            st.session_state.setup, questions, answers
                        )
                    except Exception as e:
                        st.error(f"Could not evaluate: {e}")
                    else:
                        st.session_state.page = "Performance Results"
                        st.rerun()