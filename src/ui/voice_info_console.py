"""
ATLAS Voice – Info-Assistent.
Text einfügen → Sprache abspielen. Standard: atlas_info, neutrale Stimmlage.
Rollen und Stimmlage (State) wählbar; verdrahtet gegen voice_config, ElevenLabs TTS.
"""
import streamlit as st
from src.voice.elevenlabs_tts import speak_text
from src.config.voice_config import OSMIUM_VOICE_CONFIG, EMOTIONAL_STATE_PREFIXES

st.set_page_config(page_title="ATLAS Voice Info", layout="centered")
st.title("ATLAS Voice – Info-Assistent")

roles = sorted(OSMIUM_VOICE_CONFIG.keys())
default_role_index = roles.index("atlas_info") if "atlas_info" in roles else 0

state_options = ["(neutral)"] + list(EMOTIONAL_STATE_PREFIXES)

col1, col2 = st.columns(2)
with col1:
    role_name = st.selectbox("Rolle", options=roles, index=default_role_index)
with col2:
    state_choice = st.selectbox("Stimmlage / State", options=state_options, index=0)
state_prefix = "" if state_choice == "(neutral)" else state_choice

st.caption("Text einfügen, optional Rolle und Stimmlage anpassen, dann abspielen.")

text = st.text_area(
    "Text zum Vorlesen",
    height=220,
    placeholder="Text hier einfügen …",
    label_visibility="collapsed",
)

if st.button("▶ Als Sprache abspielen", type="primary"):
    if not (text and text.strip()):
        st.warning("Bitte zuerst Text einfügen.")
    else:
        with st.spinner("Sprache wird erzeugt …"):
            path = speak_text(
                text.strip(),
                role_name=role_name,
                state_prefix=state_prefix,
                play=True,
            )
        if path:
            st.success(f"Abgespielt. Datei: `{path}`")
        else:
            st.error("TTS fehlgeschlagen. Prüfe ELEVENLABS_API_KEY und Voice-ID für die gewählte Rolle.")
