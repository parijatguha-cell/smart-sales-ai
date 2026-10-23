import streamlit as st
from utils.sales_input import sales_input_page
from utils.answer_screen import answer_page
from utils.results_page import results_page

st.set_page_config(page_title="Smart Sales AI", page_icon="💼", layout="wide")

USERS = {
    "admin": "admin123",
    "sales": "sales123",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Home"


def login_page():
    st.markdown("<h1 style='text-align:center;'>💼 Smart Sales AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔒 Login to Access Smart Sales AI</h3>", unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="e.g. admin")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("🚀 Login", use_container_width=True):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Wrong username or password.")


def sidebar():
    st.sidebar.markdown("### 💼 Smart Sales AI")
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    if st.sidebar.button("🎙️ Sales Practice", use_container_width=True):
        st.session_state.page = "Sales Practice"
        st.rerun()
    if st.sidebar.button("📊 Performance Results", use_container_width=True):
        st.session_state.page = "Performance Results"
        st.rerun()


def home_page():
    st.markdown(
        """
        <div style='background:linear-gradient(135deg,#000000,#1a0aa8);
                    padding:40px;border-radius:20px;color:white;'>
            <p style='color:#a78bfa;letter-spacing:2px;font-size:12px;'>✦ GENERATIVE AI POWERED SALES TRAINING</p>
            <h1 style='color:white;margin:0;'>Pitch with confidence.<br>Sell smarter.</h1>
            <p style='color:#c7d2fe;'>Enter your product details to generate real customer scenarios and objections.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Your Sales Toolkit")
    st.caption("An AI sales practice flow from product details to feedback.")

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📄 Product Analysis")
            st.write("Enter product details or upload a brochure to generate customer scenarios.")
    with c2:
        with st.container(border=True):
            st.markdown("#### 🎙️ Pitch Answers")
            st.write("Speak naturally or type your answer to each customer question.")
    with c3:
        with st.container(border=True):
            st.markdown("#### 🧠 AI Evaluation")
            st.write("Get question-wise scores, missing points, and a PDF report.")


if not st.session_state.logged_in:
    login_page()
else:
    sidebar()
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Sales Practice":
        sales_input_page()
        if st.session_state.get("questions"):
            if st.button("▶️ Start Answering", use_container_width=True):
                st.session_state.q_index = 0
                st.session_state.page = "Answer Screen"
                st.rerun()
    elif st.session_state.page == "Answer Screen":
        answer_page()
    elif st.session_state.page == "Performance Results":
        results_page()