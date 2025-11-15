"""Unit tests for EntityExtractor (mock OpenAI)."""
from unittest.mock import Mock
import json

import pytest

from backend.app.services.entity_extractor import EntityExtractor


class DummyChoices:
    def __init__(self, content: str):
        msg = Mock()
        msg.content = content
        choice = Mock()
        choice.message = msg
        self.choices = [choice]


def make_response(payload: dict) -> DummyChoices:
    return DummyChoices(json.dumps(payload))


def test_extract_entities_success():
    extractor = EntityExtractor()

    # Mock OpenAI client response
    payload = {
        "entities": [
            {"name": "Yann LeCun", "type": "person"},
            {"name": "Meta", "type": "org"},
            {"name": "JEPA", "type": "tech"},
        ]
    }
    extractor.client.chat.completions.create = Mock(return_value=make_response(payload))

    result = extractor.extract_entities("JEPA explained", "Meta's Yann LeCun discusses JEPA.")
    assert result == payload["entities"]


def test_extract_entities_returns_empty_on_malformed_json():
    extractor = EntityExtractor()

    # Return non-JSON content
    extractor.client.chat.completions.create = Mock(
        return_value=DummyChoices("not a json")
    )

    result = extractor.extract_entities("Title", "Summary")
    assert result == []


def test_extract_entities_filters_invalid_entries():
    extractor = EntityExtractor()

    payload = {
        "entities": [
            {"name": "Valid Person", "type": "person"},
            {"name": "  ", "type": "person"},        # invalid name
            {"name": "UnknownType", "type": "x"},    # invalid type
        ]
    }
    extractor.client.chat.completions.create = Mock(return_value=make_response(payload))

    result = extractor.extract_entities("T", "S")
    assert result == [{"name": "Valid Person", "type": "person"}]


