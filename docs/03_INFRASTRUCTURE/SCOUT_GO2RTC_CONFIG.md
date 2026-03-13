<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# go2rtc Scout Configuration: MX Brio + Headset
#
# Eintragen in: HA → Add-ons → go2rtc → Konfiguration (YAML)
# oder direkt in die go2rtc.yaml auf dem Scout.
#
# Architektur: Scout hält Hardware, PC konsumiert on demand.
#
# ── Hardware am Scout (Raspi 5) ──
#
#   VIDEO:
#     /dev/video0 = Logitech BRIO (v4l2)
#
#   AUDIO (PulseAudio):
#     Source 4 = alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo   (Brio Mikro, 48kHz Stereo)
#     Source 3 = alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback  (Headset Mikro, 16kHz Mono)
#     Sink   1 = alsa_output.usb-Samsung_USBC_Headset_20190816-00.analog-stereo (Headset Speaker, 44.1kHz)
#
# ── Streams ──
#
#   mx_brio:        Video (Brio) + Audio (Brio-Mikro) → Raumüberwachung
#   headset_mic:    Audio-only (Samsung Headset) → Spracheingabe / Remote-Abhören
#
# ── Szenarien ──
#
#   Passive Raumüberwachung:  PC zieht mx_brio (Video + Audio on demand)
#   Remote Audio-Abruf:       PC zieht headset_mic oder mx_brio Audio
#   Aktive Spracheingabe:     HA Assist Pipeline (Wake Word → Whisper → Ollama → Piper → Headset Speaker)
#                             → Headset-Mikro wird von Assist UND go2rtc parallel genutzt (PulseAudio shared)

streams:
  # Brio: Video + Audio (Raumüberwachung)
  mx_brio:
    - "exec:ffmpeg -f v4l2 -input_format mjpeg -video_size 1920x1080 -i /dev/video0 -f pulse -i alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo -c:v libx264 -preset ultrafast -c:a aac -f rtsp {output}"

  # Headset: Audio-only (Sprache, höhere Qualität für STT)
  headset_mic:
    - "exec:ffmpeg -f pulse -i alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback -c:a aac -f rtsp {output}"

# Video-only Fallback (bewiesen funktionierend, falls exec-Probleme):
# mx_brio: ffmpeg:/dev/video0#video=h264
