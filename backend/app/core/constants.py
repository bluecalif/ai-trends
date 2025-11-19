"""Application constants.

This module contains constants used across the application, including
RSS source definitions from the PRD.
"""
from typing import List, Dict

# PRD-defined RSS sources (MVP mandatory)
# These are the initial 10 RSS sources defined in the project requirements
PRD_RSS_SOURCES: List[Dict[str, str]] = [
    {"title": "TechCrunch", "feed_url": "https://techcrunch.com/feed/", "site_url": "https://techcrunch.com"},
    {"title": "VentureBeat – AI", "feed_url": "https://venturebeat.com/category/ai/feed/", "site_url": "https://venturebeat.com"},
    {"title": "MarkTechPost", "feed_url": "https://www.marktechpost.com/feed/", "site_url": "https://www.marktechpost.com"},
    {"title": "WIRED (All)", "feed_url": "https://www.wired.com/feed/rss", "site_url": "https://www.wired.com"},
    {"title": "The Verge (All)", "feed_url": "https://www.theverge.com/rss/index.xml", "site_url": "https://www.theverge.com"},
    {"title": "IEEE Spectrum – AI", "feed_url": "https://spectrum.ieee.org/rss/fulltext", "site_url": "https://spectrum.ieee.org"},
    {"title": "AITimes", "feed_url": "https://www.aitimes.com/rss/allArticle.xml", "site_url": "https://www.aitimes.com"},
    {"title": "arXiv – cs.AI", "feed_url": "http://export.arxiv.org/rss/cs.AI", "site_url": "https://arxiv.org/list/cs.AI/recent"},
    {"title": "OpenAI News", "feed_url": "https://openai.com/blog/rss.xml", "site_url": "https://openai.com"},
    {"title": "The Keyword (Google DeepMind filtered)", "feed_url": "https://blog.google/feed/", "site_url": "https://blog.google/technology/google-deepmind/"},
]

# Field categories for news items (분야)
FIELDS = [
    "research",
    "industry",
    "infra",
    "policy",
    "funding"
]

# Custom AI tags for classification
CUSTOM_TAGS = [
    "agents",
    "world_models",
    "non_transformer",
    "neuro_symbolic",
    "foundational_models",
    "inference_infra"
]


