import streamlit as st
from pypdf import PdfReader
from utils.ai_engine import generate_questions


def read_uploaded_file(uploaded_file):
    """Return text from a PDF or TXT file."""
    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()
    return uploaded_file.read().decode("utf-8", errors="ignore").strip()


def sales_input_page():
    st.title("🎙️ Sales Practice")

    st.markdown("## 🧑 Salesperson Name")
    name = st.text_input("Full name", placeholder="e.g. Nirupam")

    st.divider()

    st.markdown("## ⚙️ Choose Input Mode")
    mode = st.radio(
        "Select how you want to build questions:",
        ["📝 Manual Product Details", "📂 Upload Brochure (PDF / TXT)"],
        horizontal=True,
    )

    st.divider()

    product_info = ""

    if mode == "📝 Manual Product Details":
        st.markdown("## 🎯 Product Details")
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product / Service name", placeholder="e.g. CRM Software")
            industry = st.selectbox(
                "Customer industry",
                ["Retail", "Healthcare", "Education", "Finance", "Manufacturing", "IT / Software", "Other"],
            )
        with col2:
            customer = st.selectbox(
                "Customer type",
                ["Small business", "Mid-size company", "Large enterprise", "Individual consumer"],
            )
            experience = st.selectbox("Your experience level", ["Fresher", "1-3 years", "3+ years"])

        features = st.text_area(
            "Key features and benefits",
            placeholder="Example: Cloud based, lead tracking, email automation, 24/7 support",
        )

        col3, col4 = st.columns(2)
        with col3:
            scenario_type = st.selectbox(
                "Scenario type",
                ["Cold call", "Product demo", "Price negotiation", "Objection handling", "Closing the deal"],
            )
        with col4:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        product_info = (
            f"Product: {product}\nCustomer industry: {industry}\nCustomer type: {customer}\n"
            f"Salesperson experience: {experience}\nFeatures: {features}"
        )

    else:
        st.markdown("## 📂 Upload Your Brochure")
        uploaded = st.file_uploader("Upload product brochure (PDF or TXT)", type=["pdf", "txt"])

        if uploaded is not None:
            product_info = read_uploaded_file(uploaded)
            if product_info:
                st.success("Brochure uploaded successfully! AI will generate questions based on it.")
                with st.expander("📄 View Extracted Text"):
                    st.write(product_info[:3000])
            else:
                st.error("Could not read any text from this file. Try another one.")

        col3, col4 = st.columns(2)
        with col3:
            scenario_type = st.selectbox(
                "Scenario type (For brochure mode)",
                ["Cold call", "Product demo", "Price negotiation", "Objection handling", "Closing the deal"],
            )
        with col4:
            difficulty = st.selectbox("Difficulty (For brochure mode)", ["Easy", "Medium", "Hard"])

    st.divider()

    if st.button("✨ Generate My Sales Scenarios", use_container_width=True):
        if not name.strip():
            st.error("Please enter your name.")
        elif not product_info.strip():
            st.error("Please enter product details or upload a brochure first.")
        else:
            setup = {
                "name": name.strip(),
                "product_info": product_info,
                "scenario_type": scenario_type,
                "difficulty": difficulty,
            }
            with st.spinner("Gemini is preparing your customer questions..."):
                try:
                    questions = generate_questions(setup)
                except Exception as e:
                    st.error(f"Could not generate questions: {e}")
                else:
                    st.session_state.setup = setup
                    st.session_state.questions = questions
                    st.session_state.answers = {}
                    st.success("Questions generated! The answer screen comes in the next step.")
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"**Q{i}.** {q}")