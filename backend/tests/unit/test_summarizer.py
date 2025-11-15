"""Unit tests for summarizer service (MVP version)."""
import pytest
from backend.app.services.summarizer import Summarizer


class TestSummarizerMVP:
    """Test MVP summarizer (RSS description only)."""
    
    def test_use_description_when_provided(self):
        """Test that description is used when provided."""
        summarizer = Summarizer()
        title = "Test Article"
        description = "This is a description that should be used directly."
        link = "https://example.com/article"
        
        result = summarizer.summarize(title, description, link)
        
        assert result == description
    
    def test_empty_string_when_no_description(self):
        """Test that empty string is returned when no description."""
        summarizer = Summarizer()
        title = "Test Article"
        description = ""
        link = "https://example.com/article"
        
        result = summarizer.summarize(title, description, link)
        
        assert result == ""
    
    def test_description_truncated_to_max_length(self):
        """Test that description is truncated to max length (500 chars)."""
        summarizer = Summarizer()
        title = "Test Article"
        description = "a" * 600  # Longer than max
        link = "https://example.com/article"
        
        result = summarizer.summarize(title, description, link)
        
        assert len(result) == 500
        assert result == "a" * 500
    
    def test_description_with_whitespace_stripped(self):
        """Test that description whitespace is stripped."""
        summarizer = Summarizer()
        title = "Test Article"
        description = "  This is a description with whitespace.  "
        link = "https://example.com/article"
        
        result = summarizer.summarize(title, description, link)
        
        assert result == "This is a description with whitespace."
        assert result == result.strip()
    
    def test_short_description_used_as_is(self):
        """Test that short descriptions are used as-is (no minimum length in MVP)."""
        summarizer = Summarizer()
        title = "Test Article"
        description = "Short"  # Less than 50 characters, but still used in MVP
        link = "https://example.com/article"
        
        result = summarizer.summarize(title, description, link)
        
        assert result == "Short"


# Phase 3 고급 기능 테스트 (주석 처리)
# 아래 테스트들은 Phase 3에서 원문 로드 및 AI 요약 기능 추가 시 활성화될 예정입니다.

# class TestSummarizerFetchContent:
#     """Test content fetching logic (Phase 3 feature)."""
#     # Phase 3에서 구현 예정: httpx로 원문 로드, BeautifulSoup으로 본문 추출
#     pass

# class TestSummarizerGenerateSummary:
#     """Test OpenAI summary generation (Phase 3 feature)."""
#     # Phase 3에서 구현 예정: OpenAI API를 사용한 1-2문장 요약 생성
#     pass

# class TestSummarizerInitialization:
#     """Test summarizer initialization with OpenAI client (Phase 3 feature)."""
#     # Phase 3에서 구현 예정: OpenAI client 초기화 및 API 키 검증
#     pass

