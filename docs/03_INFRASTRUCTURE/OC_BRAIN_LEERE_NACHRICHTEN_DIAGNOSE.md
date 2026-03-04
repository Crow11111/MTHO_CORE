# OC Brain: "I didn't receive any text" – Diagnose

**Symptom (Screenshot 2026-03-03):** User schickt Nachricht im Gateway-Chat; OC Brain antwortet: "I didn't receive any text in your message. Please resend or add a caption." Eine User-Blase wirkt leer/korrupt, eine zweite enthält "das oder?".

**Ursache (Vermutung):** Leere oder nicht korrekt übermittelte Nutzer-Eingabe beim Gateway (Frontend → Backend). Mögliche Auslöser: zu schnelles Absenden, Encoding, oder UI-Bug beim Senden.

**Minimal-invasive Maßnahmen (ohne OC Brain zu gefährden):**

1. **Update ausführen:** Im Dashboard steht "Update available: v2026.3.2 (running v2026.2.27)". Update durchführen – kann den Parsing-/Payload-Bug beheben.
2. **Leere Eingabe vermeiden:** Vor dem Absenden prüfen, dass Text im Feld steht; nicht mit leerem Input senden.
3. **Bei erneutem Auftreten:** Browser-Konsole (F12) prüfen, ob beim Senden Fehler erscheinen oder der Request-Body leer ist. Falls ja: OpenClaw-Issue oder -Release-Notes prüfen.

**Kein Zugriff auf Gateway-Frontend-Code im Repo** – Fix liegt beim OpenClaw-Product. Wir ändern hier nichts am laufenden OC-Brain-Backend.
