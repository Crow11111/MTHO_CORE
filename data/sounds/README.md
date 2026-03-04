# ATLAS Sound Assets

## NASA Mission Complete

**Datei:** `nasa_mission_complete.mp3`

Authentisches NASA Apollo Mission Control Audio (Public Domain) für "Mission Complete"-Bestätigung.

### Download

```bash
# Option 1: Apollo 11 Highlights (60 min, Ausschnitt manuell extrahieren)
# curl -L -o nasa_mission_complete.mp3 "https://honeysucklecreek.net/audio/A11_highlights/Apollo_11_Highlights_32kbps.mp3"

# Option 2: Python-Script (empfohlen)
python -m src.scripts.download_nasa_sound
```

### Quellen (Public Domain)

- [NASA Apollo 11 Mission Audio](https://www.nasa.gov/history/alsj/a11/a11MissionAudio.html)
- [Honeysuckle Creek – Apollo 11 Highlights](https://honeysucklecreek.net/msfn_missions/Apollo_11_mission/A11_highlights.html)
- [NASA Historical Sounds](https://www.nasa.gov/historical-sounds)

### Abspielen auf Mini

```python
from src.voice.play_sound import play_sound_on_mini
import asyncio
asyncio.run(play_sound_on_mini("data/sounds/nasa_mission_complete.mp3"))
```
