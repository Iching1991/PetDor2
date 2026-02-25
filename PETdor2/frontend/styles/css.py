import streamlit as st


def load_css():
    st.markdown(
        """
        <style>

        /* ====== Fundo geral ====== */
        .stApp {
            background-color: #f5f7fb;
        }

        /* ====== Sidebar ====== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
            border-right: 1px solid #1e293b;
        }

        /* Texto sidebar */
        section[data-testid="stSidebar"] * {
            color: #e5e7eb !important;
            font-weight: 500;
        }

        /* Botões sidebar */
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            border: none;
            padding: 10px;
            background: transparent;
            color: #e5e7eb;
            text-align: left;
        }

        .stButton > button:hover {
            background-color: #1e293b;
            color: #22c55e;
        }

        /* Headers */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 700;
        }

        /* Cards */
        .block-container {
            padding-top: 2rem;
        }

        /* Inputs */
        .stTextInput input,
        .stSelectbox div {
            border-radius: 10px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
