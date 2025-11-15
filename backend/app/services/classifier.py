"""Classifier service for IPTC, IAB, and custom AI tags.

Updated: LLM-first strategy with heuristic fallback.
- Primary: Use gpt-5-mini to classify (title + summary) into custom_tags, IPTC, IAB.
- Fallback: If LLM fails or returns empty, use keyword heuristics and minimal mappings.
"""

from typing import List, Dict, Optional

from backend.app.core.config import get_settings


CUSTOM_KEYWORDS = {
    "agents": ["agent", "agentic", "tool use", "tool-use"],
    "world_models": ["jepa", "world model", "world-model"],
    "non_transformer": ["mamba", "ssm", "state space", "non-transformer"],
    "neuro_symbolic": ["neuro-symbolic", "apollo", "symbolic reasoning"],
    "foundational_models": ["llm", "multimodal", "foundation model"],
    "inference_infra": ["gpu", "asic", "inference", "accelerator"],
}


class ClassifierService:
    """LLM-first classifier with heuristic fallback; IPTC/IAB placeholders."""

    def __init__(self):
        self._settings = get_settings()
        self._client = None
        try:
            if self._settings.OPENAI_API_KEY:
                from openai import OpenAI

                self._client = OpenAI(api_key=self._settings.OPENAI_API_KEY)
        except Exception:
            self._client = None

    def classify(self, title: str, summary: str) -> Dict:
        """Return dict with iptc_topics, iab_categories, custom_tags."""
        text = f"{title} {summary}".strip()
        try:
            print(f"[Classifier] title_len={len(title)}, summary_len={len(summary)}")
        except Exception:
            pass

        # Try LLM first when client is available
        if self._client and text:
            llm = self._classify_with_llm(title, summary)
            if llm and (
                llm.get("custom_tags") or llm.get("iptc_topics") or llm.get("iab_categories")
            ):
                return llm

        # Fallback to heuristics
        lower_text = text.lower()
        custom_tags = self._infer_custom_tags(lower_text)
        iptc_topics = self._map_iptc_from_custom(custom_tags)
        iab_categories = self._map_iab_from_custom(custom_tags)
        return {
            "iptc_topics": iptc_topics,
            "iab_categories": iab_categories,
            "custom_tags": custom_tags,
        }

    def _classify_with_llm(self, title: str, summary: str) -> Optional[Dict]:
        """Classify using LLM; try gpt-5-mini first, then gpt-4o-mini. Return JSON or None."""
        prompt = (
            "다음 텍스트를 분류하세요. JSON만 반환:\n"
            "{\n"
            '  "custom_tags": ["agents","world_models","non_transformer","neuro_symbolic","foundational_models","inference_infra"],\n'
            '  "iptc_topics": ["technology > artificial intelligence", ...],\n'
            '  "iab_categories": ["Technology > Computing", ...]\n'
            "}\n\n"
            f"제목: {title}\n요약: {summary}\n"
        )
        # Prefer gpt-4.1-mini; then try gpt-4o-mini; finally gpt-5-mini
        models_to_try = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-5-mini"]
        import json as _json

        last_error = None
        for model_name in models_to_try:
            try:
                resp = self._client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a classification assistant. Respond ONLY with valid minified JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    # Some model variants reject response_format; rely on instruction-only JSON
                    max_tokens=180,
                    temperature=0.0,
                )
                raw = resp.choices[0].message.content.strip()
                # Attempt strict JSON parse; if fails, try to extract first JSON object
                try:
                    data = _json.loads(raw)
                except Exception:
                    start = raw.find("{")
                    end = raw.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        data = _json.loads(raw[start : end + 1])
                    else:
                        raise
                return {
                    "custom_tags": list(data.get("custom_tags", []) or []),
                    "iptc_topics": list(data.get("iptc_topics", []) or []),
                    "iab_categories": list(data.get("iab_categories", []) or []),
                }
            except Exception as e:
                last_error = e
                continue
        return None

    def _infer_custom_tags(self, text: str) -> List[str]:
        tags: List[str] = []
        for tag, keywords in CUSTOM_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        return tags

    def _map_iptc_from_custom(self, custom_tags: List[str]) -> List[str]:
        """Minimal placeholder mapping. Expand with data files later."""
        mapping = {
            "agents": ["technology > artificial intelligence"],
            "world_models": ["science & technology > research / AI"],
            "foundational_models": ["technology > computing & information technology"],
            "inference_infra": ["technology > computing & information technology"],
        }
        topics: List[str] = []
        for t in custom_tags:
            topics.extend(mapping.get(t, []))
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for topic in topics:
            if topic not in seen:
                deduped.append(topic)
                seen.add(topic)
        return deduped[:2]

    def _map_iab_from_custom(self, custom_tags: List[str]) -> List[str]:
        """Minimal placeholder mapping for IAB."""
        mapping = {
            "agents": "Technology > Artificial Intelligence",
            "world_models": "Science > Technology",
            "foundational_models": "Technology > Computing",
            "inference_infra": "Technology > Computing",
        }
        for t in custom_tags:
            if t in mapping:
                return [mapping[t]]
        return ["Technology"]
