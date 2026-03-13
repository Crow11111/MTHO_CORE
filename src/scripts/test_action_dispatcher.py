# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test für Action Dispatcher.
"""
from src.services.action_dispatcher import ActionDispatcher

def test_dispatcher():
    dispatcher = ActionDispatcher()
    # Wir nutzen eine harmlose Aktion: Notification
    text = "Ich werde eine Test-Notification senden. [HA: notify.mobile_app_iphone_von_mth( , {\"message\": \"CORE Autonomous Test\", \"title\": \"CORE 1.0\"})]"
    print(f"Sende Text an Dispatcher: {text}")
    res = dispatcher.dispatch(text)
    print(f"Ergebnis: {res}")

if __name__ == "__main__":
    test_dispatcher()
