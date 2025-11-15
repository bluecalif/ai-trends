"""Unit tests for ClassifierService (heuristics)."""
from backend.app.services.classifier import ClassifierService


def test_custom_tags_detection():
    svc = ClassifierService()
    title = "Agentic systems for tool use"
    summary = "New LLM agents demonstrate tool-use abilities."
    out = svc.classify(title, summary)
    assert "agents" in out["custom_tags"]


def test_world_models_mapping():
    svc = ClassifierService()
    title = "JEPA world model explained"
    summary = "Meta's work on JEPA advances world-model learning."
    out = svc.classify(title, summary)
    assert "world_models" in out["custom_tags"]
    assert any("research" in t for t in out["iptc_topics"])
    assert out["iab_categories"][0].startswith("Science") or out["iab_categories"][0].startswith("Technology")


def test_defaults_when_no_keywords():
    svc = ClassifierService()
    out = svc.classify("Unrelated news", "Nothing about AI here.")
    assert out["custom_tags"] == []
    assert out["iab_categories"] == ["Technology"]
