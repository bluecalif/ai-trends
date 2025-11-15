"""Integration tests for summarizer service (MVP)."""
import pytest
from backend.app.services.summarizer import Summarizer


class TestSummarizerIntegration:
    """Integration tests for MVP summarizer (description-only)."""

    def test_summarize_with_sufficient_description(self, test_db):
        """Uses RSS description as-is when provided (truncated to 500 chars)."""
        summarizer = Summarizer()
        title = "Test Article Title"
        description = "This is a long enough description that contains more than 50 characters and should be used directly without any API calls or content fetching."
        link = "https://example.com/article"

        result = summarizer.summarize(title, description, link)

        assert result == description[:500]
        assert len(result) > 50

    def test_summarize_uses_description_even_if_short(self, test_db):
        """Short descriptions are still used in MVP (no content fetch)."""
        summarizer = Summarizer()
        title = "AI Technology Advances"
        description = "Short"
        link = "https://example.com/article"

        result = summarizer.summarize(title, description, link)

        assert result == "Short"

    def test_summarize_returns_empty_when_no_description(self, test_db):
        """Returns empty string when description is empty or missing."""
        summarizer = Summarizer()
        title = "Test Article"
        description = ""
        link = "https://example.com/article"

        result = summarizer.summarize(title, description, link)

        assert result == ""

