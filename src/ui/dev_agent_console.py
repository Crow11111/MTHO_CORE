import streamlit as st

from src.ai.dev_agent_claude46 import call_dev_agent, DEV_AGENT_MODELS
from src.voice.elevenlabs_tts import speak_text
from src.config.voice_config import OSMIUM_VOICE_CONFIG, EMOTIONAL_STATE_PREFIXES


st.set_page_config(
    page_title="ATLAS_CORE | Dev-Agent Console",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #ECECEC;
        font-family: 'JetBrains Mono', monospace;
    }
    h1, h2, h3 {
        color: #00FF9C !important;
        text-transform: uppercase;
        border-bottom: 1px solid #00FF9C;
        padding-bottom: 4px;
    }
    textarea, .stTextInput input {
        background-color: #111827 !important;
        color: #E5E7EB !important;
        border-radius: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ATLAS_DEV_AGENT")

# --- Steuerleiste ---
cols = st.columns(4)
with cols[0]:
    model_choice = st.selectbox(
        "Modell",
        options=[m[0] for m in DEV_AGENT_MODELS],
        format_func=lambda id: next((m[1] for m in DEV_AGENT_MODELS if m[0] == id), id),
        index=0,
    )
with cols[1]:
    speak_enabled = st.checkbox("Sprache (ElevenLabs) aktiv", value=False)
with cols[2]:
    role_name = st.selectbox("Rolle", sorted(OSMIUM_VOICE_CONFIG.keys()), index=2)
with cols[3]:
    state_prefix = st.selectbox(
        "STATE",
        options=[""] + EMOTIONAL_STATE_PREFIXES,
        format_func=lambda x: x or "— none —",
        index=0,
    )

prompt = st.text_area(
    "Aufgabe / Prompt an Dev-Agent",
    height=160,
    placeholder="Beschreibe hier, was der Dev-Agent tun soll (z.B. Refactor, Analyse, Plan)...",
)

if st.button("▶ AUSFÜHREN", type="primary"):
    if not prompt.strip():
        st.warning("Bitte zuerst eine Aufgabe eingeben.")
    else:
        with st.spinner(f"Dev-Agent ({model_choice})..."):
            answer = call_dev_agent(prompt, model=model_choice)

        st.subheader("Antwort (Text)")
        st.write(answer)

        if speak_enabled:
            speak_text(answer, role_name=role_name, state_prefix=state_prefix)
            st.info("Audio-Ausgabe über ElevenLabs gestartet.")

