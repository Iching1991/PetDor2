# ==========================================================
# 🎨 CSS GLOBAL PETDor
# ==========================================================

import streamlit as st


def load_css():
    """
    Injeta o CSS global da aplicação.
    Deve ser chamado no streamlit_app.py
    """

    st.markdown(
        """
        <style>

        /* ======================================================
        🔷 LAYOUT GLOBAL
        ====================================================== */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* Remove espaço topo Streamlit */
        header[data-testid="stHeader"] {
            display: none;
        }

        /* ======================================================
        🔷 SIDEBAR
        ====================================================== */

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #0f766e 0%,
                #115e59 100%
            );
            color: white;
            width: 260px !important;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Logo centralizada */
        .sidebar-logo {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }

        /* ======================================================
        🔷 BOTÕES
        ====================================================== */

        .stButton button {
            width: 100%;
            border-radius: 12px;
            height: 45px;
            font-weight: 600;
            border: none;
            background: linear-gradient(
                90deg,
                #14b8a6,
                #0d9488
            );
            color: white;
            transition: 0.3s;
        }

        .stButton button:hover {
            background: linear-gradient(
                90deg,
                #0d9488,
                #0f766e
            );
            transform: scale(1.02);
        }

        /* ======================================================
        🔷 INPUTS
        ====================================================== */

        input, textarea {
            border-radius: 10px !important;
        }

        /* ======================================================
        🔷 CARDS
        ====================================================== */

        .petdor-card {
            padding: 20px;
            border-radius: 16px;
            background: white;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }

        /* ======================================================
        🔷 ALERTAS
        ====================================================== */

        .stAlert {
            border-radius: 12px;
        }

        /* ======================================================
        🔷 PASSWORD STRENGTH BAR
        ====================================================== */

        .password-bar {
            height: 8px;
            border-radius: 6px;
            margin-top: 6px;
            margin-bottom: 12px;
        }

        .weak {
            background-color: #ef4444;
            width: 25%;
        }

        .medium {
            background-color: #f59e0b;
            width: 50%;
        }

        .good {
            background-color: #3b82f6;
            width: 75%;
        }

        .strong {
            background-color: #10b981;
            width: 100%;
        }

        /* ======================================================
        🔷 SCROLLBAR CUSTOM
        ====================================================== */

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #0d9488;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #0f766e;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
