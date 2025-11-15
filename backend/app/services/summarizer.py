"""Article summarization service (MVP: RSS description only)."""
# Phase 3에서 사용할 import들 (현재는 주석 처리)
# import httpx
# from bs4 import BeautifulSoup
# from openai import OpenAI
# from typing import Optional

# Phase 3에서 사용할 설정 (현재는 불필요)
# from backend.app.core.config import get_settings as _get_settings
# settings = _get_settings()

# 테스트 호환성용 placeholder (기존 테스트가 get_settings를 patch 대상으로 사용)
def get_settings():
    """Placeholder for backward compatibility with older tests."""
    return None


class Summarizer:
    """Article summarizer using RSS description (MVP version).
    
    MVP(Phase 1-2)에서는 RSS description만 사용합니다.
    Phase 3에서 원문 로드 및 AI 요약 기능이 추가될 예정입니다.
    """
    
    MAX_SUMMARY_LENGTH = 500
    
    def __init__(self):
        """Initialize summarizer (MVP: no OpenAI client needed)."""
        # Phase 3에서 OpenAI client 초기화 추가 예정
        # if not settings.OPENAI_API_KEY:
        #     raise ValueError("OPENAI_API_KEY is not set in environment variables")
        # self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        pass
    
    def summarize(self, title: str, description: str, link: str) -> str:
        """Generate summary using RSS description only (MVP).
        
        Args:
            title: Article title (not used in MVP, reserved for Phase 3)
            description: RSS description
            link: Article URL (not used in MVP, reserved for Phase 3)
            
        Returns:
            Summary text (max 500 characters) - RSS description 그대로 반환
            
        Note:
            - MVP에서는 RSS description을 그대로 사용합니다.
            - Phase 3에서 description이 부족한 경우 원문 로드 → AI 요약 기능 추가 예정.
        """
        if description:
            return description.strip()[:self.MAX_SUMMARY_LENGTH]
        return ""
    
    # Phase 3 고급 기능: 원문 로드 함수 (주석 처리)
    # def _fetch_content(self, link: str) -> Optional[str]:
    #     """Fetch article content from URL (temporary, discarded after use).
    #     
    #     Phase 3에서 추가될 예정:
    #     - httpx로 원문 웹페이지 로드
    #     - BeautifulSoup으로 본문 추출 (<article>, <main> 등)
    #     - 최대 2000자만 추출 후 즉시 폐기
    #     
    #     Args:
    #         link: Article URL
    #         
    #     Returns:
    #         Extracted text content (max 2000 chars) or None if fetch fails
    #     """
    #     try:
    #         with httpx.Client(timeout=10.0) as client:
    #             response = client.get(link, follow_redirects=True)
    #             response.raise_for_status()
    #             
    #             soup = BeautifulSoup(response.text, 'lxml')
    #             content = (
    #                 soup.find('article') or 
    #                 soup.find('main') or 
    #                 soup.find('div', class_='content') or
    #                 soup.find('div', class_='article-body') or
    #                 soup.find('div', id='content')
    #             )
    #             
    #             if content:
    #                 text = content.get_text(separator=' ', strip=True)
    #                 return text[:2000]
    #             else:
    #                 body = soup.find('body')
    #                 if body:
    #                     text = body.get_text(separator=' ', strip=True)
    #                     return text[:2000]
    #                 return None
    #     except Exception as e:
    #         print(f"[Summarizer] Failed to fetch {link}: {e}")
    #         return None
    
    # Phase 3 고급 기능: OpenAI API 요약 생성 함수 (주석 처리)
    # def _generate_summary(self, title: str, content: str) -> str:
    #     """Generate summary using OpenAI API.
    #     
    #     Phase 3에서 추가될 예정:
    #     - gpt-4o-mini 모델 사용
    #     - 1-2문장 요약 생성
    #     - 본문은 일시 로드 후 즉시 폐기
    #     
    #     Args:
    #         title: Article title
    #         content: Article content (already truncated to max length)
    #         
    #     Returns:
    #         Generated summary text
    #     """
    #     prompt = f"""다음 기사를 1-2문장으로 요약하세요:
    #
    # 제목: {title}
    #
    # 내용: {content[:2000]}
    #
    # 요약:"""
    #     
    #     try:
    #         response = self.client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             messages=[
    #                 {"role": "system", "content": "You are a concise news summarizer."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             max_tokens=150,
    #             temperature=0.3
    #         )
    #         
    #         summary = response.choices[0].message.content.strip()
    #         return summary
    #     except Exception as e:
    #         print(f"[Summarizer] OpenAI API error: {e}")
    #         return ""

