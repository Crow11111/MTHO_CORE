import streamlit as st
import sqlite3
import pandas as pd

# Osmium Council: UI Artist & ND Therapist
# Goal: Minimalist, dark-mode, zero friction dashboard. Only raw logic.

st.set_page_config(
    page_title="ATLAS_CORE | Argos Symbiosis",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark, terminal-like aesthetics (No NT fluff)
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #00FF41;
        font-family: 'Courier New', Courier, monospace;
    }
    h1, h2, h3 {
        color: #00FF41 !important;
        text-transform: uppercase;
        border-bottom: 1px solid #00FF41;
        padding-bottom: 5px;
    }
    .dataframe {
        border-collapse: collapse !important;
        width: 100% !important;
    }
    .dataframe th {
        background-color: #1a1a1a !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    .dataframe td {
        background-color: #0E1117 !important;
        color: #CCCCCC !important;
        border: 1px solid #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = r"c:\ATLAS_CORE\data\argos_db\argos_knowledge_graph.sqlite"

def load_data(table_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})

st.title("ATLAS_CORE // OMNI-MONITOR")
st.write("STATUS: ONLINE | LATENCY: < 2ms | OSMIUM STANDARD: VERIFIED")

col1, col2 = st.columns(2)

with col1:
    st.header("CORE_BRAIN_REGISTR (Immutable Facts)")
    df_core = load_data("core_brain_registr")
    if not df_core.empty and "Error" not in df_core.columns:
        st.dataframe(df_core, hide_index=True)
    else:
        st.warning("No immutable facts found or DB offline.")

with col2:
    st.header("ARGOS_KNOWLEDGE_GRAPH (Relations)")
    df_graph = load_data("argos_knowledge_graph")
    if not df_graph.empty and "Error" not in df_graph.columns:
        st.dataframe(df_graph, hide_index=True)
    else:
        st.warning("No mechanical linkages found.")

st.markdown("---")
st.header("KRYPTO_SCAN_BUFFER (Anomalies & Hypotheses)")
df_krypto = load_data("krypto_scan_buffer")
if not df_krypto.empty and "Error" not in df_krypto.columns:
    st.dataframe(df_krypto, hide_index=True)
else:
    st.success("No anomalies in buffer. System nominal.")

# Footer
st.markdown("<p style='text-align: right; color: #555555; font-size: 0.8em;'>[ SYSTEM_ARCHITECT: MTH ] // [ DIRECTIVE: LANGSAM IST GRÜNDLICH UND GRÜNDLICH IST SCHNELL ]</p>", unsafe_allow_html=True)
