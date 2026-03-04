"""
ATLAS Voice (ElevenLabs): TTS per API – verschiedene Stimmen/Rollen, automatisierbar.
Unabhängig von WhatsApp. Nutzt voice_config.OSMIUM_VOICE_CONFIG.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/atlas", tags=["atlas-voice"])


class TTSBody(BaseModel):
    text: str
    role: str = "atlas_dialog"
    state_prefix: str = ""
    play: bool = True  # Bei True: Audio lokal auf PC abspielen


class DispatchTTSBody(BaseModel):
    text: str
    target: str = "mini"  # mini | local | elevenlabs | elevenlabs_stream | both | piper
    role: str = "atlas_dialog"


@router.post("/tts")
def tts_speak(body: TTSBody):
    """Text zu Sprache (ElevenLabs), Rolle aus voice_config. Bei play=True: lokal abspielen."""
    try:
        from src.voice.elevenlabs_tts import speak_text
        import uuid
        import os
        _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        media_dir = os.path.join(_root, "media")
        os.makedirs(media_dir, exist_ok=True)
        out_path = os.path.join(media_dir, f"tts_{uuid.uuid4().hex[:12]}.mp3")
        path = speak_text(
            text=body.text,
            role_name=body.role,
            state_prefix=body.state_prefix or "",
            output_path=out_path,
            play=body.play,  # Lokal abspielen wenn True
        )
        if not path or not os.path.isfile(path):
            raise HTTPException(status_code=502, detail="TTS fehlgeschlagen (Key oder VoiceID)")
        if body.play:
            return {"status": "ok", "played": True, "path": path}
        return FileResponse(path, media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)[:200])


@router.post("/speak")
def speak_now(body: TTSBody):
    """Kurzform: Text empfangen, sofort lokal abspielen. Für Tampermonkey/Browser-Skripte."""
    body.play = True
    return tts_speak(body)


@router.post("/dispatch-tts")
async def dispatch_tts_endpoint(body: DispatchTTSBody):
    """TTS-Dispatcher: target='mini' (HA Minis), 'local' (ElevenLabs), 'both' (parallel)."""
    from src.voice.tts_dispatcher import dispatch_tts
    ok = await dispatch_tts(text=body.text, target=body.target, role_name=body.role)
    return {"status": "ok" if ok else "error", "ok": ok}


@router.get("/voice/roles")
def voice_roles():
    """Verfügbare Rollen (Stimmen) aus voice_config; voice_id je Rolle für Verifikation (Z11)."""
    from src.config.voice_config import OSMIUM_VOICE_CONFIG
    roles = [
        {"role": k, "voice_id": v.get("voice_id", "") or ""}
        for k, v in OSMIUM_VOICE_CONFIG.items()
    ]
    return {"roles": [r["role"] for r in roles], "roles_with_voice_id": roles}
