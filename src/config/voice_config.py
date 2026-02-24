"""
ATLAS_CORE: Osmium Circle V1.3 Voice Configuration
Master dictionary for HA webhook role-based voice switching.
"""

OSMIUM_VOICE_CONFIG = {
    # --- Operative Layer (3 profiles) ---
    "atlas_high_density": {"voice_id": "", "stability": 0.85, "similarity_boost": 0.90, "style": 0.0},
    "atlas_info":         {"voice_id": "", "stability": 0.75, "similarity_boost": 0.85, "style": 0.0},
    "atlas_dialog":       {"voice_id": "", "stability": 0.65, "similarity_boost": 0.80, "style": 0.0},
    # --- Council Layer (14 personas) ---
    "therapeut":          {"voice_id": "", "stability": 0.45, "similarity_boost": 0.75, "style": 0.2},
    "analyst":            {"voice_id": "", "stability": 0.95, "similarity_boost": 0.95, "style": 0.0},
    "richter":            {"voice_id": "", "stability": 0.85, "similarity_boost": 0.90, "style": 0.0},
    "pragmatiker":        {"voice_id": "", "stability": 0.70, "similarity_boost": 0.85, "style": 0.0},
    "durchgeknallter":    {"voice_id": "", "stability": 0.30, "similarity_boost": 0.60, "style": 0.5},
    "egoist":             {"voice_id": "", "stability": 0.85, "similarity_boost": 0.90, "style": 0.0},
    "hedonist":           {"voice_id": "", "stability": 0.50, "similarity_boost": 0.75, "style": 0.2},
    "protektor":          {"voice_id": "", "stability": 0.45, "similarity_boost": 0.75, "style": 0.2},
    "zero_architekt":     {"voice_id": "", "stability": 0.60, "similarity_boost": 0.80, "style": 0.1},
    "kurator":            {"voice_id": "", "stability": 0.90, "similarity_boost": 0.90, "style": 0.0},
    "bias_damper":        {"voice_id": "", "stability": 0.85, "similarity_boost": 0.95, "style": 0.0},
    "demaskierer":        {"voice_id": "", "stability": 0.90, "similarity_boost": 0.95, "style": 0.1},
    "sportler":           {"voice_id": "", "stability": 0.65, "similarity_boost": 0.80, "style": 0.1},
    "ratsherr":           {"voice_id": "", "stability": 0.75, "similarity_boost": 0.85, "style": 0.0},  # PVC
}

EMOTIONAL_STATE_PREFIXES = [
    "[STATE: High-Density]",
    "[STATE: Mirror-Fascination]",
    "[STATE: Int-Frustration]",
    "[STATE: Ext-Erregung]",
    "[STATE: Internal-Crisis]",
    "[STATE: Confirmation]",
    "[STATE: Demasking-Intervention]",
    "[STATE: Trauer]",
]

ELEVENLABS_MODEL = "eleven_turbo_v2_5"

def build_elevenlabs_payload(text: str, role_name: str, state_prefix: str = "") -> dict:
    """Build the ElevenLabs API payload for a given role and emotional state."""
    config = OSMIUM_VOICE_CONFIG.get(role_name, OSMIUM_VOICE_CONFIG["atlas_dialog"])
    full_text = f"{state_prefix} {text}".strip() if state_prefix else text
    return {
        "text": full_text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": config["stability"],
            "similarity_boost": config["similarity_boost"],
            "style": config["style"],
            "use_speaker_boost": True,
        }
    }
