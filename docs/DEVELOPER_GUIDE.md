# AI Trend Monitor - 개발자 가이드

이 문서는 AI Trend Monitor 프로젝트의 개발 환경 설정, 코드 구조, 개발 가이드라인을 설명합니다.

## 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [개발 환경 설정](#개발-환경-설정)
3. [코드 스타일 및 컨벤션](#코드-스타일-및-컨벤션)
4. [테스트 실행 방법](#테스트-실행-방법)
5. [API 개발 가이드](#api-개발-가이드)
6. [데이터베이스 스키마](#데이터베이스-스키마)
7. [배포 프로세스](#배포-프로세스)

---

## 프로젝트 구조

### 전체 구조

```
ai-trend/
├── backend/              # Python FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 라우터
│   │   ├── core/        # 설정, 데이터베이스, 스케줄러
│   │   ├── models/      # SQLAlchemy 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── services/    # 비즈니스 로직
│   │   └── main.py      # FastAPI 앱 진입점
│   ├── alembic/         # DB 마이그레이션
│   ├── scripts/         # 유틸리티 스크립트
│   ├── tests/           # 테스트 파일
│   │   ├── unit/        # 단위 테스트
│   │   ├── integration/ # 통합 테스트
│   │   └── e2e/         # E2E 테스트
│   └── alembic.ini      # Alembic 설정
├── frontend/            # Next.js 프론트엔드
│   ├── app/            # App Router
│   ├── components/     # React 컴포넌트
│   ├── lib/            # 유틸리티, API 클라이언트
│   └── package.json
├── docs/               # 문서
├── .cursor/           # Cursor IDE 설정
│   └── rules/         # 커서룰 파일들
├── pyproject.toml     # Poetry 의존성 관리
└── README.md
```

### 백엔드 구조

#### `backend/app/api/`

API 라우터 모듈. 각 파일은 특정 도메인의 엔드포인트를 담당합니다.

- `rss.py`: RSS 수집 API
- `items.py`: 아이템 조회 API
- `sources.py`: 소스 관리 API
- `persons.py`: 인물 관리 API
- `bookmarks.py`: 북마크 관리 API
- `watch_rules.py`: 워치 규칙 관리 API
- `insights.py`: 인사이트 API
- `constants.py`: 상수 제공 API
- `groups.py`: 사건 그룹 API

#### `backend/app/core/`

핵심 설정 및 유틸리티 모듈.

- `config.py`: 환경변수 설정 (Pydantic Settings)
- `constants.py`: 애플리케이션 상수 (RSS 소스, 필드, 태그)
- `database.py`: SQLAlchemy 세션 관리
- `scheduler.py`: APScheduler 설정 및 작업 정의

#### `backend/app/models/`

SQLAlchemy ORM 모델.

- `base.py`: Base 모델 (id, created_at, updated_at)
- `source.py`: RSS 소스 모델
- `item.py`: 뉴스 아이템 모델
- `person.py`: 인물 모델
- `person_timeline.py`: 인물 타임라인 이벤트 모델
- `watch_rule.py`: 워치 규칙 모델
- `bookmark.py`: 북마크 모델
- `entity.py`: 엔티티 모델 (인물/기관/기술)
- `item_entity.py`: 아이템-엔티티 다대다 관계 테이블
- `dup_group_meta.py`: 중복 그룹 메타데이터 모델

#### `backend/app/schemas/`

Pydantic 스키마 (API 요청/응답 검증).

- 각 모델에 대응하는 스키마 파일
- 요청 스키마 (Create, Update)
- 응답 스키마 (Response, ListResponse)

#### `backend/app/services/`

비즈니스 로직 서비스.

- `rss_collector.py`: RSS 피드 수집 및 정규화
- `summarizer.py`: 요약 생성 (MVP: RSS description 사용)
- `classifier.py`: 분류 (IPTC/IAB/커스텀 태그)
- `entity_extractor.py`: 엔티티 추출 (인물/기관/기술)
- `deduplicator.py`: 중복 그룹화 (TF-IDF 유사도)
- `person_tracker.py`: 인물 트래킹 (워치 규칙 매칭)
- `group_backfill.py`: 그룹화 백필 로직

### 프론트엔드 구조

#### `frontend/app/`

Next.js 14 App Router 페이지.

- `page.tsx`: 홈 페이지
- `[field]/page.tsx`: 분야별 페이지 (research, industry, infra, policy, funding)
- `story/[groupId]/page.tsx`: 사건 타임라인 페이지
- `persons/page.tsx`: 인물 목록 페이지
- `persons/[id]/page.tsx`: 인물 상세 페이지
- `saved/page.tsx`: 북마크 페이지
- `settings/page.tsx`: 설정 페이지

#### `frontend/components/`

재사용 가능한 React 컴포넌트.

- `Navigation.tsx`: 네비게이션 바
- `FieldTabs.tsx`: 분야 탭
- `ItemCard.tsx`: 아이템 카드
- `TagFilter.tsx`: 태그 필터
- `Pagination.tsx`: 페이지네이션
- `TimelineCard.tsx`: 타임라인 카드
- `PersonCard.tsx`: 인물 카드
- `BookmarkCard.tsx`: 북마크 카드
- `BookmarkModal.tsx`: 북마크 생성 모달

#### `frontend/lib/`

유틸리티 및 API 클라이언트.

- `api.ts`: Axios 기반 API 클라이언트
- `types.ts`: TypeScript 타입 정의 (백엔드 스키마와 동기화)
- `constants.ts`: 상수 정의 (FIELDS, CUSTOM_TAGS)
- `validators.ts`: 런타임 검증 함수

---

## 개발 환경 설정

### 필수 요구사항

- Python 3.11 이상
- Poetry 1.8.5 이상
- Node.js 18 이상
- Supabase 계정 (또는 로컬 PostgreSQL)

### 초기 설정

자세한 내용은 `docs/SETUP.md`를 참고하세요.

**요약**:
1. 저장소 클론
2. Poetry 설치 및 의존성 설치: `poetry install`
3. 환경변수 설정: `backend/.env` 파일 생성
4. 데이터베이스 마이그레이션: `poetry run alembic upgrade head`
5. 초기 소스 등록: `poetry run python -m backend.scripts.init_sources`

### 개발 서버 실행

**백엔드**:
```bash
poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**프론트엔드**:
```bash
cd frontend
npm run dev
```

---

## 코드 스타일 및 컨벤션

### Python 코드 스타일

#### 포맷팅

- **Black**: 코드 포맷팅 (line-length: 100)
- **isort**: import 정렬 (black 프로필 사용)
- **ruff**: 린팅 (E, W, F, I, B, C4, UP 규칙)

**실행**:
```bash
# 포맷팅
poetry run black backend/
poetry run isort backend/

# 린팅
poetry run ruff check backend/
poetry run ruff check --fix backend/
```

#### 네이밍 컨벤션

- **클래스**: PascalCase (예: `RSSCollector`)
- **함수/변수**: snake_case (예: `collect_source`)
- **상수**: UPPER_SNAKE_CASE (예: `PRD_RSS_SOURCES`)
- **프라이빗**: `_` 접두사 (예: `_parse_date`)

#### 타입 힌팅

모든 함수에 타입 힌팅을 추가합니다:

```python
from typing import List, Optional, Dict

def collect_source(source: Source) -> int:
    """소스별 수집 실행."""
    ...
```

#### 문서화

- **Docstring**: Google 스타일 사용
- **인라인 주석**: 복잡한 로직에만 사용

### TypeScript 코드 스타일

#### 포맷팅

- **Prettier**: 코드 포맷팅 (Next.js 기본 설정)
- **ESLint**: 린팅 (Next.js 기본 설정)

#### 네이밍 컨벤션

- **컴포넌트**: PascalCase (예: `ItemCard`)
- **함수/변수**: camelCase (예: `getItems`)
- **상수**: UPPER_SNAKE_CASE (예: `FIELDS`)
- **타입/인터페이스**: PascalCase (예: `ItemResponse`)

#### 타입 정의

모든 API 응답에 타입을 정의합니다:

```typescript
export interface ItemResponse {
  id: number
  title: string
  summary_short: string
  // ...
}
```

---

## 테스트 실행 방법

### 테스트 구조

- **단위 테스트** (`tests/unit/`): 함수/메서드 단위 (mock 사용)
- **통합 테스트** (`tests/integration/`): 서비스 간 연동, DB 연동
- **E2E 테스트** (`tests/e2e/`): 전체 플로우 (실제 DB 데이터 사용)

### 테스트 실행

**모든 테스트**:
```bash
poetry run pytest backend/tests/ -v
```

**특정 테스트 파일**:
```bash
poetry run pytest backend/tests/unit/test_rss_collector.py -v
```

**E2E 테스트만**:
```bash
poetry run pytest backend/tests/e2e/ -v -m e2e_real_data
```

**커버리지**:
```bash
poetry run pytest backend/tests/ --cov=backend/app --cov-report=html
```

### 테스트 마커

- `@pytest.mark.slow`: 느린 테스트
- `@pytest.mark.unit`: 단위 테스트
- `@pytest.mark.integration`: 통합 테스트
- `@pytest.mark.e2e`: E2E 테스트
- `@pytest.mark.e2e_real_data`: 실제 DB 데이터 사용 E2E 테스트

**특정 마커만 실행**:
```bash
poetry run pytest backend/tests/ -m "not slow" -v
```

### E2E 테스트 주의사항

**중요**: E2E 테스트는 Supabase 실제 DB 데이터를 사용합니다.

**필수 준수 사항**:
1. 소스 확인/생성: 테스트 시작 시 `PRD_RSS_SOURCES`에서 소스 확인
2. 기존 아이템 우선 조회: DB에서 기존 아이템 먼저 조회
3. 수집은 보조: 기존 아이템이 없을 때만 RSS 수집 시도
4. 최종 검증: 아이템이 0개면 테스트 실패

자세한 내용은 `TODOs.md`의 "테스트 전략" 섹션을 참고하세요.

---

## API 개발 가이드

### 새 API 엔드포인트 추가

#### 1. 스키마 정의

`backend/app/schemas/`에 Pydantic 스키마 정의:

```python
# backend/app/schemas/example.py
from pydantic import BaseModel
from datetime import datetime

class ExampleResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 2. 라우터 생성

`backend/app/api/`에 라우터 파일 생성:

```python
# backend/app/api/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.example import ExampleResponse

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("", response_model=List[ExampleResponse])
async def get_examples(db: Session = Depends(get_db)):
    """예시 목록 조회."""
    # 구현
    pass
```

#### 3. 라우터 등록

`backend/app/main.py`에 라우터 등록:

```python
from backend.app.api import example

app.include_router(example.router)
```

#### 4. API 문서 확인

서버 실행 후 `http://localhost:8000/docs`에서 확인.

### API 계약 동기화

**중요**: 백엔드가 상수와 스키마의 단일 진실 공급원입니다.

**체크리스트**:
- [ ] Pydantic 스키마에 정확한 필드명/타입 정의
- [ ] 프론트엔드 타입 정의가 백엔드와 일치하는지 확인
- [ ] Query 파라미터 이름이 양쪽에서 동일한지 확인 (snake_case)
- [ ] Enum 값이 문자열로 정확히 일치하는지 확인

자세한 내용은 `.cursor/rules/api-contract-sync.mdc`를 참고하세요.

---

## 데이터베이스 스키마

### 주요 테이블

#### `sources`
RSS 소스 정보.

- `id`: Primary Key
- `title`: 소스 이름
- `feed_url`: RSS 피드 URL (Unique)
- `site_url`: 웹사이트 URL
- `is_active`: 활성화 여부

#### `items`
수집된 뉴스 아이템.

- `id`: Primary Key
- `source_id`: Foreign Key → sources.id
- `title`: 기사 제목
- `summary_short`: 요약 (RSS description)
- `link`: 원문 링크 (Unique)
- `published_at`: 발행 시간
- `iptc_topics`: IPTC 분류 (JSON 배열)
- `iab_categories`: IAB 분류 (JSON 배열)
- `custom_tags`: 커스텀 태그 (JSON 배열)
- `dup_group_id`: 중복 그룹 ID

#### `persons`
추적 대상 인물.

- `id`: Primary Key
- `name`: 인물 이름 (Unique)

#### `person_timeline`
인물별 타임라인 이벤트.

- `id`: Primary Key
- `person_id`: Foreign Key → persons.id
- `item_id`: Foreign Key → items.id
- `event_type`: 이벤트 타입 (paper, product, investment 등)

#### `watch_rules`
워치 규칙 (인물/키워드 매칭).

- `id`: Primary Key
- `label`: 규칙 이름
- `required_keywords`: 필수 키워드 (JSON 배열)
- `optional_keywords`: 선택적 키워드 (JSON 배열)
- `person_id`: Foreign Key → persons.id (선택사항)

#### `bookmarks`
사용자 북마크.

- `id`: Primary Key
- `item_id`: Foreign Key → items.id (선택사항)
- `title`: 북마크 제목
- `link`: 링크
- `tags`: 태그 (JSON 배열)

#### `entities`
추출된 엔티티 (인물/기관/기술).

- `id`: Primary Key
- `name`: 엔티티 이름 (Unique)
- `type`: 엔티티 타입 (person, org, tech)

#### `item_entities`
아이템-엔티티 다대다 관계.

- `item_id`: Foreign Key → items.id
- `entity_id`: Foreign Key → entities.id

### 마이그레이션

**새 마이그레이션 생성**:
```bash
poetry run alembic revision --autogenerate -m "description"
```

**마이그레이션 적용**:
```bash
poetry run alembic upgrade head
```

**마이그레이션 롤백**:
```bash
poetry run alembic downgrade -1
```

---

## 배포 프로세스

### 배포 전 체크리스트

- [ ] 모든 테스트 통과
- [ ] 환경변수 설정 확인
- [ ] 데이터베이스 마이그레이션 적용
- [ ] 초기 데이터 설정 (RSS 소스 등록)
- [ ] 로깅 설정 확인
- [ ] Health check 엔드포인트 확인

### 배포 단계

1. **데이터베이스 마이그레이션**: 프로덕션 DB에 스키마 적용
2. **초기 데이터 설정**: RSS 소스 등록
3. **백엔드 API 배포**: FastAPI 서버 배포
4. **스케줄러 워커 배포**: Worker 프로세스 배포
5. **프론트엔드 배포**: Next.js 앱 배포

자세한 내용은 `docs/DEPLOYMENT.md`를 참고하세요.

---

## 참고 자료

- **초기 설정 가이드**: `docs/SETUP.md`
- **배포 가이드**: `docs/DEPLOYMENT.md`
- **사용자 가이드**: `docs/USER_GUIDE.md`
- **프로젝트 계획**: `TODOs.md`
- **PRD**: `docs/PRD_ai-trend.md`
- **커서룰**: `.cursor/rules/` 디렉토리

---

## 문제 해결

### 일반적인 문제

**모듈을 찾을 수 없음**:
- 프로젝트 루트에서 명령 실행 확인
- `-m` 옵션 사용: `poetry run python -m backend.scripts.script_name`

**데이터베이스 연결 오류**:
- `DATABASE_URL` 확인
- Supabase 프로젝트 상태 확인
- SSL 모드 확인 (`sslmode=require`)

**환경변수 로드 오류**:
- `backend/.env` 파일 위치 확인
- 파일 인코딩 확인 (UTF-8)
- `python-dotenv` 패키지 설치 확인

자세한 내용은 `docs/SETUP.md`의 "문제 해결" 섹션을 참고하세요.

