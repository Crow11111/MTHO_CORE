import os
import requests
from dotenv import load_dotenv
from loguru import logger

from src.config.voice_config import build_elevenlabs_payload, OSMIUM_VOICE_CONFIG


load_dotenv("c:/CORE/.env")


def speak_text(
    text: str,
    role_name: str = "atlas_dialog",
    state_prefix: str = "",
    output_path: str | None = None,
    play: bool = True,
    override_voice_id: str | None = None,
) -> str | None:
    """
    Wandelt Text über ElevenLabs in Sprache um und speichert/optional spielt die Datei.

    :param text: Text, der gesprochen werden soll.
    :param role_name: Osmium-Rolle (z.B. 'therapeut', 'analyst', 'atlas_dialog').
    :param state_prefix: Optionales STATE-Markup (z.B. '[STATE: Internal-Crisis]').
    :param output_path: Zielpfad für die MP3-Datei. Wenn None, wird ein Default im media-Ordner verwendet.
    :param play: Wenn True, wird die Datei unter Windows direkt abgespielt.
    :param override_voice_id: Optional explizite VoiceID, falls nicht aus dem Rollen-Mapping genommen werden soll.
    :return: Pfad zur erzeugten Datei oder None bei Fehler.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    env_default_voice = os.getenv("ELEVENLABS_VOICE_ELA_CONVERSATION")

    if not api_key:
        logger.error("ELEVENLABS_API_KEY fehlt in .env.")
        return None

    # VoiceID aus Rollen-Config oder Override / Fallback auf ENV
    config = OSMIUM_VOICE_CONFIG.get(role_name, OSMIUM_VOICE_CONFIG["atlas_dialog"])
    voice_id = override_voice_id or config.get("voice_id") or env_default_voice

    if not voice_id:
        logger.error("Keine gültige VoiceID gefunden (weder in Rollen-Config noch in .env).")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }

    payload = build_elevenlabs_payload(text=text, role_name=role_name, state_prefix=state_prefix)

    logger.info(f"Sende Text an ElevenLabs (Rolle='{role_name}', State='{state_prefix}')...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        logger.error(f"Fehler bei ElevenLabs Request: {e}")
        return None

    if response.status_code != 200:
        logger.error(f"Fehler bei ElevenLabs: {response.status_code} - {response.text}")
        return None

    if output_path is None:
        media_dir = os.path.join("c:/CORE", "media")
        os.makedirs(media_dir, exist_ok=True)
        output_path = os.path.join(media_dir, "dev_agent_reply.mp3")

    try:
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.success(f"Audio gespeichert unter {output_path}.")
    except Exception as e:
        logger.error(f"Fehler beim Schreiben der Audio-Datei: {e}")
        return None

    if play:
        try:
            os.startfile(output_path)
            logger.info("Audio wird abgespielt...")
        except Exception as e:
            logger.error(f"Fehler beim Abspielen der Audio-Datei: {e}")

    return output_path
