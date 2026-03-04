"""
Unit-Tests für Smart Command Parser (ATLAS Voice Assistant).
"""
from __future__ import annotations

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from voice.smart_command_parser import (
    HAAction,
    parse_command,
    _build_entity_index,
    _fuzzy_resolve_entity,
    _normalize_entity_name,
)


# Fixture: Minimale Entity-Liste (wie HA get_states)
MOCK_ENTITIES = [
    {"entity_id": "light.regal", "attributes": {"friendly_name": "LED Regal"}},
    {"entity_id": "light.deckenlampe", "attributes": {"friendly_name": "Deckenlampe"}},
    {"entity_id": "light.led_regal", "attributes": {"friendly_name": "Regal"}},
    {"entity_id": "light.kueche", "attributes": {"friendly_name": "Küche"}},
    {"entity_id": "media_player.fernseher", "attributes": {"friendly_name": "Fernseher"}},
    {"entity_id": "climate.wohnzimmer", "attributes": {"friendly_name": "Wohnzimmer Thermostat"}},
]


class TestSmartCommandParser(unittest.TestCase):
    def test_normalize_entity_name(self):
        self.assertEqual(_normalize_entity_name("LED Regal"), "led_regal")
        self.assertEqual(_normalize_entity_name("Küche"), "kueche")
        self.assertEqual(_normalize_entity_name("  Deckenlampe  "), "deckenlampe")

    def test_build_entity_index(self):
        index = _build_entity_index(MOCK_ENTITIES)
        self.assertTrue("regal" in index or "led_regal" in index)
        self.assertEqual(index.get("deckenlampe"), "light.deckenlampe")
        self.assertEqual(index.get("kueche"), "light.kueche")
        self.assertEqual(index.get("fernseher"), "media_player.fernseher")

    def test_fuzzy_resolve_entity(self):
        index = _build_entity_index(MOCK_ENTITIES)
        self.assertIn(
            _fuzzy_resolve_entity("Regal", MOCK_ENTITIES, index),
            ("light.regal", "light.led_regal"),
        )
        self.assertEqual(
            _fuzzy_resolve_entity("Deckenlampe", MOCK_ENTITIES, index),
            "light.deckenlampe",
        )
        self.assertEqual(
            _fuzzy_resolve_entity("Fernseher", MOCK_ENTITIES, index),
            "media_player.fernseher",
        )
        self.assertEqual(
            _fuzzy_resolve_entity("Küche", MOCK_ENTITIES, index),
            "light.kueche",
        )

    def test_parse_regal_aus(self):
        """Regal aus -> light.turn_off light.regal/led_regal"""
        result = parse_command("Regal aus", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_off")
        self.assertIn("regal", result.entity_id.lower())
        self.assertEqual(result.domain, "light")

    def test_parse_deckenlampe_an(self):
        """Deckenlampe an -> light.turn_on"""
        result = parse_command("Deckenlampe an", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_on")
        self.assertEqual(result.entity_id, "light.deckenlampe")

    def test_parse_mach_das_regal_aus(self):
        """Mach das Regal aus -> turn_off"""
        result = parse_command("Mach das Regal aus", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_off")
        self.assertIn("regal", result.entity_id.lower())

    def test_parse_licht_regal_aus(self):
        """Licht Regal aus -> Synonym wird ignoriert"""
        result = parse_command("Licht Regal aus", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_off")
        self.assertIn("regal", result.entity_id.lower())

    def test_parse_brightness(self):
        """Regal 80% Helligkeit -> light.turn_on brightness_pct=80"""
        result = parse_command("Regal 80% Helligkeit", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_on")
        self.assertEqual(result.data.get("brightness_pct"), 80)
        self.assertIn("regal", result.entity_id.lower())

    def test_parse_color(self):
        """Regal rot -> light.turn_on rgb_color"""
        result = parse_command("Regal rot", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertEqual(result.service, "turn_on")
        self.assertEqual(result.data.get("rgb_color"), [255, 0, 0])

    def test_parse_empty(self):
        self.assertIsNone(parse_command(""))
        self.assertIsNone(parse_command("   "))

    def test_parse_unknown_no_llm(self):
        """Unbekannter Befehl ohne LLM (entities leer, skip_llm) -> None"""
        result = parse_command("Erkläre mir die Quantenmechanik", [], skip_llm_fallback=True)
        self.assertIsNone(result)

    def test_ha_action_structure(self):
        """HAAction hat korrekte Felder"""
        result = parse_command("Deckenlampe an", MOCK_ENTITIES)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, "domain"))
        self.assertTrue(hasattr(result, "service"))
        self.assertTrue(hasattr(result, "entity_id"))
        self.assertTrue(hasattr(result, "data"))
        self.assertTrue(hasattr(result, "confidence"))
        self.assertTrue(hasattr(result, "source"))
        self.assertEqual(result.source, "pattern")


if __name__ == "__main__":
    unittest.main(verbosity=2)
