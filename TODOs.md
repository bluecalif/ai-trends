# AI Trend Monitor - 작업 계획서 (TODOs)

> 이 문서는 PRD_ai-trend.md를 바탕으로 작성된 상세 구현 계획서입니다.  
> 단계별로 진행하며 각 항목을 완료할 때마다 체크박스를 업데이트합니다.

---

## 프로젝트 개요

**목적**: RSS 기반 AI 기술 트렌드 모니터링 서비스  
**기술 스택**: 
- Backend: Python (FastAPI), PostgreSQL
- Frontend: Next.js 14+ (TypeScript, Tailwind CSS)
- AI: OpenAI API (GPT-4/GPT-3.5)
- Infrastructure: Docker Compose

**핵심 원칙**:
- 원문 본문 미보관 (메타데이터, 요약, 엔티티만 저장)
- IPTC Media Topics + IAB Content Taxonomy + 커스텀 AI 태그 분류
- 인물별 사업/기술 방향 누적 타임라인
- 중복/사건 그룹화로 타임라인 구성

---

## 프로젝트 구조

```
ai-trend/
├── backend/              # Python FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 라우터
│   │   ├── core/        # 설정, 보안
│   │   ├── models/      # SQLAlchemy 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── services/    # 비즈니스 로직
│   │   │   ├── rss_collector.py
│   │   │   ├── summarizer.py
│   │   │   ├── classifier.py
│   │   │   ├── deduplicator.py
│   │   │   ├── entity_extractor.py
│   │   │   └── person_tracker.py
│   │   └── db/          # DB 세션, 마이그레이션
│   ├── alembic/         # DB 마이그레이션
│   └── .env.example
├── frontend/            # Next.js 프론트엔드
│   ├── app/            # App Router
│   │   ├── page.tsx    # 홈
│   │   ├── [field]/    # 분야별 페이지
│   │   ├── story/      # 사건 타임라인
│   │   ├── persons/    # 인물 페이지
│   │   ├── saved/      # 저장함
│   │   └── settings/   # 설정
│   ├── components/     # React 컴포넌트
│   ├── lib/            # 유틸리티, API 클라이언트
│   ├── package.json
│   └── .env.local.example
├── .cursor/            # Cursor IDE 설정
│   ├── rules/         # 커서룰 파일들
│   └── commands/      # 커맨드 정의
├── docs/               # 문서
│   └── PRD_ai-trend.md
├── pyproject.toml      # Poetry 의존성 관리
├── poetry.lock         # Poetry 잠금 파일
├── requirements.txt    # pip 대안 (Poetry 문제 시)
├── README.md           # 프로젝트 개요
├── AGENTS.md           # AI 에이전트 운영 가이드
├── docker-compose.yml  # PostgreSQL + 앱 컨테이너
└── TODOs.md           # 이 파일
```

---

## Phase 1: 백엔드 기반 구조

### 1.1 프로젝트 초기 설정
- [x] `pyproject.toml` 생성 (Poetry 의존성 관리)
- [x] `poetry.lock` 생성 (Poetry 2.2.1 이상 사용)
- [x] `requirements.txt` 생성 (pip 대안)
- [x] `README.md` 생성
- [x] `AGENTS.md` 업데이트 (Poetry 패키지 관리 섹션 추가)
- [x] `.cursor/rules/` 커서룰 파일 생성 (10개 파일)
- [x] `backend/` 디렉토리 생성
- [x] Poetry 가상환경 설정 (`poetry install`)
- [x] `backend/.env.example` 생성 (DATABASE_URL, OPENAI_API_KEY 등)
- [x] `docker-compose.yml` 생성 (PostgreSQL 서비스)
- [x] `backend/app/__init__.py` 생성
- [x] `backend/app/main.py` 생성 (FastAPI 앱 초기화, CORS 설정)
- [x] `backend/app/core/config.py` 생성 (환경변수 로드)

### 1.2 데이터베이스 스키마
- [x] Alembic 초기화 (`alembic init alembic`)
- [x] `backend/app/core/database.py` 생성 (SQLAlchemy 세션 관리)
- [x] `backend/app/models/__init__.py` 생성
- [x] `backend/app/models/base.py` 생성 (Base 모델)
- [x] `backend/app/models/source.py` 생성:
  ```python
  id, title, feed_url, site_url, category, lang, 
  created_at, updated_at, is_active
  ```
- [x] `backend/app/models/item.py` 생성:
  ```python
  id, source_id (FK), title, summary_short, link (unique), 
  published_at, author, thumbnail_url, 
  iptc_topics (JSON), iab_categories (JSON), custom_tags (JSON), 
  dup_group_id, created_at, updated_at
  ```
- [x] `backend/app/models/person.py` 생성:
  ```python
  id, name, bio, created_at, updated_at
  ```
- [x] `backend/app/models/person_timeline.py` 생성:
  ```python
  id, person_id (FK), item_id (FK), event_type, 
  description, created_at
  ```
- [x] `backend/app/models/watch_rule.py` 생성:
  ```python
  id, label, include_rules (JSON), exclude_rules (JSON), 
  priority, person_id (FK, nullable), created_at, updated_at
  ```
- [x] `backend/app/models/bookmark.py` 생성:
  ```python
  id, item_id (FK), title, tags (JSON), note, created_at
  ```
- [x] `backend/app/models/entity.py` 생성:
  ```python
  id, name, type (person/org/tech), created_at
  ```
- [x] `backend/app/models/item_entity.py` 생성 (다대다 관계 테이블):
  ```python
  item_id (FK), entity_id (FK)
  ```
- [x] Alembic 마이그레이션 생성 및 실행 (`alembic revision --autogenerate`, `alembic upgrade head`) - **완료: Supabase Shared Pooler (IPv4) 사용**
- [x] **단위 테스트**: 모델 생성 및 관계 테스트 (13개 테스트 통과)
- [x] **통합 테스트**: 마이그레이션 롤백/업그레이드 테스트 (4개 테스트 통과)
- [x] **E2E 테스트**: 실제 데이터 CRUD 작업 테스트 (모든 모델, 10개 테스트 통과)

### 1.3 RSS 수집 서비스
- [x] `backend/app/services/__init__.py` 생성
- [x] `backend/app/services/rss_collector.py` 생성:
  - [x] `feedparser`로 RSS/Atom 파싱 함수
  - [x] 메타데이터 정규화 함수 (title, link, published_at, author, description, thumbnail_url)
  - [x] 중복 체크 함수 (link 해시 기반)
  - [x] 소스별 폴링 함수 (스케줄러 통합)
  - [x] APScheduler 작업 등록 (일반 소스: 20분 간격, arXiv: 하루 2회)
- [x] PRD 소스 전량 등록(MVP 필수)
  - [x] 초기 소스 일괄 등록 스크립트 실행(TechCrunch, VentureBeat AI, MarkTechPost, WIRED, The Verge, IEEE Spectrum – AI, AITimes, arXiv cs.AI, OpenAI News, DeepMind Blog)
  - [x] 등록 직후 전체 수집 리포트 실행 및 결과 JSON 저장
  - [x] 문제 소스 별도 이슈 트래킹(헤더/인코딩/리다이렉트 정책 정리)
    - [x] IEEE Spectrum – AI: 대체 피드 적용(`https://spectrum.ieee.org/rss/fulltext`)
    - [x] OpenAI News: 대체 피드 적용(`https://openai.com/blog/rss.xml`)
    - [x] DeepMind: 현 단계 비활성화(피드 malformed 지속). Phase 3에서 The Keyword 전체 피드(`https://blog.google/feed/`) + 카테고리 필터(“Google DeepMind”) 방식으로 재활성화 예정
- [x] `backend/app/core/scheduler.py` 생성 (APScheduler 스케줄러 구현)
- [x] `backend/app/main.py` 스케줄러 통합 (lifespan 이벤트)
- [x] `backend/app/api/rss.py` 생성 (수동 수집 트리거 엔드포인트)
- [x] **단위 테스트**: RSS 파싱 함수 테스트 (mock feedparser) - 11개 테스트 통과
- [x] **단위 테스트**: 중복 체크 로직 테스트 - 통과
- [x] **통합 테스트**: 실제 RSS 피드 수집 테스트 (DB 호환성 포함) - 3개 테스트 통과
- [x] **E2E 테스트**: 초기 10개 RSS 소스 등록 및 수집 테스트 - 4개 테스트 통과
- [x] Supabase 연동 확인: 수집 후 `items` 행 증가 및 고유 인덱스 충돌 처리 검증 (스케줄러 포함)
- [x] 재검증(최근 기준 전체 소스 수집 품질 점검)
  - [x] 대상 소스 전체 재수집 실행(최근 7~14일 범위) 및 per-source 수집 결과 집계
  - [x] feedparser `bozo`/인코딩 오류(예: us-ascii vs utf-8) 원인 파악 및 핸들링 방안 마련
  - [x] 오류 소스별 대응: 요청 헤더/리다이렉트/파서 옵션/인코딩 강제 등 검토
  - [x] 재시도/백오프 로직 및 오류 로깅 강화(소스별 요약 리포트)
  - [x] 수집 결과 JSON 저장(`backend/tests/results/rss_collect_verify_YYYYMMDD_HHMMSS.json`)
  - [x] 문제 소스 리스트업 및 이슈 트래킹 항목 생성 — 현재 활성 소스 기준 에러 0 확인

### 1.4 요약 서비스 (MVP: RSS description만 사용)
- [x] `backend/app/services/summarizer.py` 생성:
  - [x] RSS description 사용 함수 (MVP: description 그대로 사용)
  - [x] **참고**: 원문 로드 및 AI 요약 기능은 Phase 3 고급 기능으로 이동
- [x] `backend/app/core/config.py`에 OpenAI API 키 설정 (이미 존재, Phase 3에서 사용)
- [x] **단위 테스트**: description 사용 로직 테스트 (`test_summarizer.py`)
- [x] **E2E 테스트**: 다양한 RSS 항목으로 요약 생성 → DB 저장 확인
- [x] **결정 사항**: MVP에서는 RSS description만 사용, 원문 기반 AI 요약은 Phase 3로 이동
- [x] Supabase 연동 확인: `items.summary_short` 업데이트 반영 및 대량 커밋 성능 확인

### 1.5 엔티티 추출 서비스
- [x] `backend/app/services/entity_extractor.py` 생성:
  - [x] OpenAI API (NER)로 인물/기관/기술 추출 함수
  - [x] 키워드 추출 함수 (제목+요약 기반)
  - [x] entities, item_entities 테이블 저장 함수
- [x] **단위 테스트**: 엔티티 추출 함수 테스트 (mock OpenAI API)
- [x] **통합 테스트**: 엔티티 DB 저장 및 관계 생성 테스트
- [x] **E2E 테스트**: 실제 아이템으로 엔티티 추출 → 저장 → 조회 확인
- [x] Supabase 연동 확인: `entities`, `item_entities` 쓰기 및 조인 조회 성능 확인

### 1.6 분류 서비스
- [x] `backend/app/services/classifier.py` 생성:
  - [x] IPTC Media Topics 매핑 함수 (상위 1-2개)
  - [x] IAB Content Taxonomy 매핑 함수 (상위 1개)
  - [x] 커스텀 AI 태그 추론 함수 (Agents, World Models, Non-Transformer 등)
  - [x] OpenAI(gpt-4.1-mini) 기반 분류 수행 + 휴리스틱 폴백
  - [x] 결과를 JSON 배열로 저장
- [x] `backend/app/data/iptc_mapping.json` 생성 (IPTC 상위 카테고리 매핑) — (MVP 내장 매핑으로 대체)
- [x] `backend/app/data/iab_mapping.json` 생성 (IAB 상위 카테고리 매핑) — (MVP 내장 매핑으로 대체)
- [x] `backend/app/data/custom_tags.json` 생성 (커스텀 태그 정의 및 규칙) — (MVP 내장 키워드로 대체)
- [x] **단위 테스트**: 커스텀 태그/매핑 로직 테스트
- [x] **통합 테스트**: 분류 결과를 Item JSON 필드에 저장 확인
- [x] **E2E 테스트**: 실제 아이템으로 분류 수행 → JSON 필드 저장 확인 → 결과 파일 저장
- [x] Supabase 연동 확인: `items.iptc_topics/iab_categories/custom_tags` 저장/조회 동작 확인 (JSONB contains/GIN은 Phase 1.9에서 최종 검증)

### 1.7 중복/사건 묶음 서비스
- [ ] `backend/app/services/deduplicator.py` 생성/확장:
  - [x] link 정확 중복 제거
  - [x] TF-IDF 유사도 + 보정점수(엔티티/태그/시간)
  - [x] 근사 중복 그룹화(유사도 임계값 기반)
  - [x] dup_group_id 할당
  - [ ] 후보 축소(1단계) 도입: 최근 윈도우 + 제목 3-gram 교집합 ≥1 + (있을 때) 엔티티/커스텀태그 교집합 필터
  - [ ] 초기 백필 모드(REF_DATE-21d ~ REF_DATE) + 증분 모드(REF_DATE 이후 신규) 분리
- [ ] 그룹 메타 테이블 추가: `dup_group_meta`
  - [ ] 스키마: `dup_group_id(PK)`, `first_seen_at`, `last_updated_at`, `member_count`
  - [ ] 인덱스: `first_seen_at`, `last_updated_at`
  - [ ] 동기화: 새 그룹 생성/합류 시 메타 갱신
- [ ] 스케줄러 작업
  - [ ] 초기 백필 작업(수동 트리거) — REF_DATE 포함 과거 21일 전수 그룹핑
  - [ ] 증분 파이프라인(10–30분) — 수집→요약→분류→엔티티→증분 그룹핑→메타 갱신
- [ ] API
  - [ ] `GET /api/groups?since=YYYY-MM-DD&kind=new|incremental&page=...`
  - [ ] `GET /api/groups/{dup_group_id}` 타임라인 상세(기존 group API 확장)
- [ ] **단위 테스트**: 후보축소/점수 결합/메타 동기화 테스트
- [ ] **통합 테스트**: 그룹 메타 생성/갱신/조회 테스트
- [ ] **E2E 테스트**: 초기 백필 결과/증분 결과 JSON 저장 및 검증
- [ ] Supabase 연동 확인: `dup_group_id` 배치 업데이트, 메타 조회 성능

### 1.8 인물 트래킹 서비스
- [ ] `backend/app/services/person_tracker.py` 생성:
  - [ ] watch_rules의 include/exclude 규칙 매칭 함수 (제목+요약 검색)
  - [ ] 매칭 시 person_timeline에 이벤트 추가 함수
  - [ ] 인물-기술-기관-사건 관계 그래프 생성 함수
- [ ] **단위 테스트**: 규칙 매칭 로직 테스트 (include/exclude)
- [ ] **단위 테스트**: 이벤트 타입 추론 함수 테스트
- [ ] **통합 테스트**: 타임라인 이벤트 추가 및 조회 테스트
- [ ] **E2E 테스트**: 초기 5명 인물 규칙으로 매칭 → 타임라인 생성 확인
- [ ] Supabase 연동 확인: `person_timeline` 쓰기/조회 및 관련 조인 성능

### 1.9 API 엔드포인트
- [ ] `backend/app/api/__init__.py` 생성
- [ ] `backend/app/api/sources.py` 생성:
  - [ ] `GET /api/sources` - 소스 목록
  - [ ] `POST /api/sources` - 소스 추가
  - [ ] `GET /api/sources/{id}` - 소스 상세
  - [ ] `PUT /api/sources/{id}` - 소스 수정
  - [ ] `DELETE /api/sources/{id}` - 소스 삭제
- [ ] `backend/app/api/items.py` 생성:
  - [ ] `GET /api/items` - 아이템 목록 (필터: 분야, 태그, 날짜, 페이지네이션)
  - [ ] `GET /api/items/{id}` - 아이템 상세
  - [ ] `GET /api/items/group/{dup_group_id}` - 사건 타임라인
- [ ] `backend/app/api/groups.py` 생성:
  - [ ] `GET /api/groups` - `since`, `kind=new|incremental` 기반 그룹 목록(대표+updates_count_since)
  - [ ] `GET /api/groups/{dup_group_id}` - 그룹 타임라인 상세
- [ ] `backend/app/api/persons.py` 생성:
  - [ ] `GET /api/persons` - 인물 목록
  - [ ] `GET /api/persons/{id}` - 인물 상세 (타임라인+그래프)
  - [ ] `POST /api/persons` - 인물 추가
- [ ] `backend/app/api/bookmarks.py` 생성:
  - [ ] `GET /api/bookmarks` - 북마크 목록
  - [ ] `POST /api/bookmarks` - 북마크 추가
  - [ ] `DELETE /api/bookmarks/{id}` - 북마크 삭제
- [ ] `backend/app/api/watch_rules.py` 생성:
  - [ ] `GET /api/watch-rules` - 워치 규칙 목록
  - [ ] `POST /api/watch-rules` - 워치 규칙 추가
  - [ ] `PUT /api/watch-rules/{id}` - 워치 규칙 수정
  - [ ] `DELETE /api/watch-rules/{id}` - 워치 규칙 삭제
- [ ] `backend/app/api/insights.py` 생성:
  - [ ] `GET /api/insights/weekly` - 주간 인사이트
- [ ] `backend/app/main.py`에 모든 라우터 등록
- [ ] Pydantic 스키마 작성 (`backend/app/schemas/`)
- [ ] API 문서 확인 (FastAPI 자동 생성: `/docs`)
- [ ] **단위 테스트**: 각 API 엔드포인트별 테스트 (TestClient)
- [ ] **통합 테스트**: 필터링, 페이지네이션, 정렬 기능 테스트
- [ ] **E2E 테스트**: 전체 API 플로우 테스트 (소스 추가 → 수집 → 조회)
- [ ] Supabase 연동 확인: 필터/페이지네이션/정렬이 Supabase에서 일관 동작

---

## Phase 2: 프론트엔드 UI

### 2.1 Next.js 프로젝트 설정
- [ ] `frontend/` 디렉토리 생성
- [ ] Next.js 14 프로젝트 초기화 (`npx create-next-app@latest`)
- [ ] TypeScript 설정 확인
- [ ] Tailwind CSS 설정 확인
- [ ] `frontend/package.json` 의존성 추가:
  - axios 또는 fetch wrapper
  - @tanstack/react-query (데이터 페칭)
  - react-flow 또는 d3.js (그래프 시각화)
  - date-fns (날짜 포맷팅)
- [ ] `frontend/.env.local.example` 생성 (API_BASE_URL)
- [ ] `frontend/lib/api.ts` 생성 (API 클라이언트)
- [ ] `frontend/lib/types.ts` 생성 (TypeScript 타입 정의)

### 2.2 홈/분야 탭
- [ ] `frontend/app/layout.tsx` 생성 (기본 레이아웃, 네비게이션)
- [ ] `frontend/app/page.tsx` 생성:
  - [ ] 상단 분야 탭 (Research/Industry/Infra/Policy/Funding)
  - [ ] 기본 필터링된 아이템 리스트
- [ ] `frontend/components/ItemCard.tsx` 생성:
  - [ ] 제목, 요약 표시
  - [ ] 태그 표시 (IPTC, IAB, 커스텀)
  - [ ] 출처, 시간 표시
  - [ ] "동일 사건 N건" 표시
  - [ ] 클릭 시 원문 링크 이동
  - [ ] "사건 보기" 버튼
- [ ] `frontend/app/[field]/page.tsx` 생성 (분야별 필터링된 페이지)
- [ ] `frontend/components/FieldTabs.tsx` 생성 (분야 탭 컴포넌트)
- [ ] `frontend/components/TagFilter.tsx` 생성 (태그 필터 컴포넌트)

### 2.3 사건 타임라인
- [ ] `frontend/app/story/[groupId]/page.tsx` 생성:
  - [ ] dup_group_id 기반 타임라인 UI
  - [ ] 최초 보도 → 후속/해설 흐름 시각화
  - [ ] 타임라인 카드 컴포넌트
- [ ] `frontend/components/TimelineCard.tsx` 생성

### 2.4 인물 페이지
- [ ] `frontend/app/persons/page.tsx` 생성:
  - [ ] 인물 리스트 (우선순위/최근 이벤트 정렬)
  - [ ] 검색 기능
- [ ] `frontend/app/persons/[id]/page.tsx` 생성:
  - [ ] 인물 상세 정보
  - [ ] 타임라인 표시
  - [ ] 관계 그래프 시각화 (인물-기술-기관-사건)
- [ ] `frontend/components/PersonCard.tsx` 생성
- [ ] `frontend/components/RelationshipGraph.tsx` 생성 (React Flow 또는 D3.js)

### 2.5 저장함
- [ ] `frontend/app/saved/page.tsx` 생성:
  - [ ] 북마크 목록
  - [ ] 태그 관리 (추가/삭제/필터)
  - [ ] 검색 기능
- [ ] `frontend/components/BookmarkCard.tsx` 생성
- [ ] `frontend/components/TagManager.tsx` 생성

### 2.6 설정
- [ ] `frontend/app/settings/page.tsx` 생성:
  - [ ] 소스 관리 섹션
    - [ ] 소스 목록
    - [ ] 소스 추가/수정/삭제
    - [ ] OPML Import/Export 기능
  - [ ] 워치 규칙 관리 섹션
    - [ ] 규칙 목록
    - [ ] 규칙 추가/수정/삭제 (JSON 편집기)
  - [ ] 알림 설정 섹션 (선택사항)
- [ ] `frontend/components/OPMLImporter.tsx` 생성
- [ ] `frontend/components/WatchRuleEditor.tsx` 생성

---

## Phase 3: 고급 기능

### 3.1 고급 요약 서비스 (원문 기반 AI 요약)
- [ ] `backend/app/services/summarizer.py` 확장:
  - [ ] 원문 일시 로드 함수 (httpx) - Phase 3에서 추가
  - [ ] OpenAI API로 1-2문장 요약 생성 함수 - Phase 3에서 추가
  - [ ] 본문 폐기 후 요약만 반환
  - [ ] RSS description 부족 시 원문 로드 → AI 요약 자동 수행
- [ ] **단위 테스트**: 원문 로드 함수 테스트 (mock httpx)
- [ ] **통합 테스트**: OpenAI API 호출 테스트 (실제 API 또는 mock)
- [ ] **E2E 테스트**: 원문 기반 요약 생성 → DB 저장 확인

### 3.2 OPML Import/Export
- [ ] `backend/app/services/opml_handler.py` 생성:
  - [ ] OPML 파싱 함수 (feedparser 또는 opml 라이브러리)
  - [ ] 소스 일괄 추가 함수
  - [ ] OPML 생성 함수
- [ ] `backend/app/api/opml.py` 생성:
  - [ ] `POST /api/opml/import` - OPML 파일 업로드 및 소스 추가
  - [ ] `GET /api/opml/export` - 현재 소스 목록을 OPML로 내보내기
- [ ] 프론트엔드 OPML Import/Export UI 연동

### 3.3 주간 인사이트
- [ ] `backend/app/services/insights.py` 생성:
  - [ ] 분야별 키워드 증감 분석 함수
  - [ ] 인물별 핵심 이슈 요약 함수
  - [ ] 주간 리포트 생성 함수
- [ ] `backend/app/api/insights.py` 확장:
  - [ ] `GET /api/insights/weekly` - 주간 인사이트 상세
  - [ ] `GET /api/insights/keywords` - 키워드 트렌드
  - [ ] `GET /api/insights/persons` - 인물별 요약
- [ ] `frontend/app/insights/page.tsx` 생성 (인사이트 시각화)

### 3.4 알림 (선택사항)
- [ ] `backend/app/services/notifier.py` 생성:
  - [ ] 이메일 알림 함수 (SMTP)
  - [ ] 웹푸시 알림 함수
- [ ] `backend/app/models/subscription.py` 생성 (구독 설정)
- [ ] Celery 작업 큐 설정 (비동기 알림 처리)
- [ ] `backend/app/api/subscriptions.py` 생성
- [ ] 프론트엔드 알림 설정 UI

### 3.5 고급 중복/사건 묶음 (임베딩/LSH 기반)
- [ ] 임베딩 기반 유사도(예: text-embedding-3-small) 도입 + 코사인 유사도
- [ ] LSH/ANN을 활용한 후보 축소 후 정밀 판별(성능 최적화)
- [ ] 사건 시드 모델: 초기 보도 식별 → 시간/엔티티/출처 가중으로 후속 기사 점수화
- [ ] 문장/문단 의미 유사도(파라프레이즈) 모델 평가 및 통합
- [ ] **E2E 테스트(실데이터)**: 임베딩/LSH 파이프라인으로 그룹 생성률/정확도 비교, 결과 JSON 저장

### 3.6 소스 재활성화(DeepMind)
- [ ] DeepMind 수집 재개(Phase 3)
  - [ ] The Keyword 전체 피드(`https://blog.google/feed/`) 구독
  - [ ] 카테고리 메타 기반 필터(“Google DeepMind”) + 백업 키워드(`deepmind`, `/technology/google-deepmind/`)
  - [ ] 초기 E2E: 수집 → 요약 → 분류 → 그룹핑 → `/api/groups` 노출 검증(결과 JSON 저장)

---

## 초기 데이터 설정

### 4.1 RSS 소스 초기화
- [ ] `backend/scripts/init_sources.py` 생성 (MVP 필수):
  - [ ] TechCrunch (전체)
  - [ ] VentureBeat – AI
  - [ ] MarkTechPost
  - [ ] WIRED (All)
  - [ ] The Verge (All)
  - [ ] IEEE Spectrum – AI
  - [ ] AITimes (전체)
  - [ ] arXiv – cs.AI
  - [ ] OpenAI News
  - [ ] DeepMind Blog
- [ ] 스크립트 실행하여 DB에 소스 등록(MVP 완료 요건)
  - [x] 실행 완료(등록/대체/비활성 반영) — DeepMind Blog 비활성화, OpenAI/IEEE 대체 피드 적용

### 4.2 워치 규칙 초기화
- [ ] `backend/scripts/init_watch_rules.py` 생성:
  - [ ] Yann LeCun: `("JEPA" OR "I-JEPA" OR "V-JEPA") AND (Meta OR LeCun)`
  - [ ] Andrej Karpathy: `("NanoChat" OR "Eureka Labs" OR "LLM101n")`
  - [ ] David Luan: `("agentic" OR "Amazon Nova" OR "AGI SF Lab")`
  - [ ] Llion Jones: `("Sakana AI" AND (model OR paper OR benchmark))`
  - [ ] AUI/Apollo-1: `("Apollo-1" OR "neuro-symbolic" OR "stateful reasoning")`
- [ ] 스크립트 실행하여 DB에 규칙 등록

### 4.3 IPTC/IAB 매핑 데이터 준비
- [ ] `backend/app/data/iptc_mapping.json` 작성 (상위 카테고리 매핑)
- [ ] `backend/app/data/iab_mapping.json` 작성 (상위 카테고리 매핑)
- [ ] `backend/app/data/custom_tags.json` 작성 (커스텀 태그 정의 및 규칙)

---

## 테스트 및 검증

### 5.1 백엔드 단위 테스트
- [ ] 모델 CRUD 테스트 (pytest)
- [ ] 서비스 레이어 단위 테스트 (mock 사용)
- [ ] 유틸리티 함수 테스트

### 5.2 백엔드 통합 테스트
- [ ] 데이터베이스 통합 테스트 (테스트 DB 사용)
- [ ] API 엔드포인트 통합 테스트 (TestClient)
- [ ] 서비스 간 연동 테스트

### 5.3 백엔드 E2E 테스트 (프론트엔드 개발 전 필수)
- [ ] 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장 (필수)
- [ ] **RSS 수집 E2E**: 소스 등록 → 수집 → DB 저장 확인
- [ ] **요약 E2E**: 아이템 수집 → 요약 생성 → 저장 확인
- [ ] **분류 E2E**: 아이템 → IPTC/IAB/커스텀 태그 분류 → 저장 확인
- [ ] **엔티티 추출 E2E**: 아이템 → 엔티티 추출 → 관계 저장 확인
- [ ] **중복 그룹화 E2E**: 초기 백필(21일) + 증분(REF_DATE 이후) → 그룹/타임라인/메타 조회 확인
- [ ] **인물 트래킹 E2E**: 워치 규칙 → 매칭 → 타임라인 생성 확인
- [ ] **API 전체 플로우 E2E**: 소스 추가 → 수집 → 처리 → API 조회 (모든 필터/정렬)
- [ ] **폴링 작업자 E2E**: 스케줄러 실행 → 자동 수집 → 처리 파이프라인 확인
- [ ] **성능 테스트**: 대량 데이터 처리 (1000+ 아이템)

### 5.4 프론트엔드 테스트 (백엔드 E2E 완료 후)
- [ ] 홈/분야 탭 UI 테스트
- [ ] 사건 타임라인 UI 테스트
- [ ] 인물 페이지 UI 테스트
- [ ] 저장함 기능 테스트
- [ ] 설정 페이지 기능 테스트

### 5.5 전체 통합 테스트
- [ ] 백엔드-프론트엔드 연동 테스트
- [ ] 전체 플로우 테스트 (RSS 수집 → 처리 → UI 표시)
- [ ] 에러 처리 및 복구 테스트

---

## 배포 준비

### 6.1 환경 설정
- [ ] 프로덕션 환경변수 설정
- [ ] 데이터베이스 백업 전략 수립
- [ ] 로깅 설정

### 6.2 문서화
- [ ] API 문서 정리
- [ ] 사용자 가이드 작성
- [ ] 개발자 가이드 작성

---

## 진행 상황 추적

**마지막 업데이트**: 2025-11-15

**프로젝트 진행률**: 백엔드 기반 구조 약 55% 완료 (Phase 1.1~1.6 / 1.9)

**완료된 항목**: Phase 1.1, Phase 1.2, Phase 1.3, Phase 1.4, Phase 1.5, Phase 1.6 완료

**현재 단계**: Phase 1.7 (중복/사건 묶음 서비스) - 진행 중

**결정 사항(그룹/증분 기준)**:
- REF_DATE: 매일 UTC 자정 고정
- 초기 백필 윈도우: REF_DATE 포함 과거 21일
- 신규(New): `first_seen_at >= since(REF_DATE 또는 사용자 마지막 방문)`
- 증분(Incremental): `first_seen_at < since` AND `last_updated_at >= since`

**다음 단계(즉시)**:
1) `dup_group_meta` 스키마/인덱스 추가 및 메타 동기화 로직 구현
2) Deduplicator 후보축소(1단계) 적용 및 초기 백필/증분 모드 분리
3) `/api/groups` 엔드포인트 추가 및 E2E 작성(백필/증분 결과 JSON 저장)
4) 소스 정리: 구(OpenAI `index.xml`, IEEE `.../fulltext/rss`) 중복 소스 비활성화
5) 수집 재실행 → 백필/증분 → `/api/groups` 재검증(결과 JSON 저장 유지)
6) 스케줄러 등록: 증분(10–30분), 일일 백필(UTC 00:00)

---

## 세션 요약 (2025-11-15)

- 수집 소스
  - IEEE Spectrum – AI: 대체 피드 적용(`https://spectrum.ieee.org/rss/fulltext`) 확인
  - OpenAI News: 대체 피드 적용(`https://openai.com/blog/rss.xml`) 확인
  - DeepMind: 현 단계 비활성화(피드 malformed 지속). Phase 3에서 The Keyword 전체 피드(`https://blog.google/feed/`) + 카테고리 필터(“Google DeepMind”) 방식 재활성화
- 그룹핑
  - 백필/증분 실행 결과: 최근 실행에서 백필 181, 증분 40 처리 확인
  - `/api/groups` 신 29, 증분 2 그룹 반환(JSON 저장)
- 테스트 결과 파일
  - `backend/tests/results/rss_collect_verify_YYYYMMDD_HHMMSS.json`
  - `backend/tests/results/groups_api_e2e_YYYYMMDD_HHMMSS.json`

### 미해결/과제
- [ ] 구 OpenAI/IEEE 중복 소스 비활성화(소스 테이블 정리) 및 재수집 확인
- [ ] The Keyword(DeepMind) 피드 malformed 지속 모니터링(Phase 3에서 재활성화)
- [ ] 스케줄러에 증분/백필 파이프라인 등록
- [ ] `/api/groups` 고도화: `updates_count_since` 계산 및 정렬 보강
- [ ] Supabase 체크포인트: `dup_group_meta` 읽기/쓰기 및 조회 성능 확인

**완료된 작업**:
- Phase 1.1: Poetry 프로젝트 설정, 프로젝트 문서화, 커서룰 파일 생성
- Phase 1.2: 데이터베이스 스키마 설정, Alembic 마이그레이션, 모든 모델 생성, 테스트 완료 (27개 테스트 통과)
- Phase 1.3: RSS 수집 서비스 구현 완료
  - RSS/Atom 피드 파싱 및 정규화
  - 중복 체크 로직
  - APScheduler 기반 자동 수집 스케줄러 (일반 소스: 20분 간격, arXiv: 하루 2회)
  - 테스트 완료: 단위 11개, 통합 3개, E2E 4개 (총 18개 테스트 통과)
- Phase 1.4: 요약 서비스 구현 완료 (MVP: RSS description만 사용)
  - RSS description 사용 로직 (MVP에서는 description 그대로 사용)
  - **참고**: 원문 로드 및 AI 요약 기능은 Phase 3 고급 기능으로 이동 결정
  - 테스트 완료: 단위 테스트, E2E 테스트 작성 완료 (실제 RSS 데이터 사용, 결과 JSON 파일 저장)

**현재 프로젝트 구조 상태**:
```
backend/app/
├── api/
│   ├── rss.py          ✅ (RSS 수집 API만 구현)
│   └── [5개 API 미구현: sources, items, persons, bookmarks, watch_rules, insights]
├── services/
│   ├── rss_collector.py  ✅
│   ├── summarizer.py     ✅
│   ├── entity_extractor.py ✅ (완료)
│   └── [3개 서비스 미구현: classifier, deduplicator, person_tracker]
├── models/            ✅ (8개 모델 모두 완료)
├── schemas/           
│   ├── rss.py         ✅
│   └── [다른 엔티티 스키마 미구현]
└── core/              ✅ (config, database, scheduler)
```

**테스트 현황**:
- ✅ 완료: 모델 테스트 27개, RSS 수집 테스트 18개, 요약 서비스 테스트 완료 (단위/통합/E2E)
- ❌ 미완료: 엔티티 추출, 분류, 중복 그룹화, 인물 트래킹, API 엔드포인트 테스트

**핵심 마일스톤**:
- ✅ 완료: 백엔드 기반 구조의 약 44% 완료 (Phase 1.1~1.4)
- ⏳ 현재: Phase 1.5 (엔티티 추출 서비스) 시작 전
- 📋 다음 우선순위: 엔티티 추출 → 분류 → 중복 그룹화 → 인물 트래킹 → API 엔드포인트
- 🚫 프론트엔드: Phase 1의 모든 E2E 테스트 통과 후 시작

**미구현 주요 기능**:
- Phase 1.5: 엔티티 추출 서비스 (entity_extractor.py)
- Phase 1.6: 분류 서비스 (classifier.py + 매핑 데이터 파일)
- Phase 1.7: 중복/사건 묶음 서비스 (deduplicator.py)
- Phase 1.8: 인물 트래킹 서비스 (person_tracker.py)
- Phase 1.9: API 엔드포인트 (5개 추가 API 라우터)

---

## 참고사항

- 각 단계 완료 후 체크박스를 업데이트합니다.
- 문제 발생 시 이슈를 기록하고 해결 방안을 문서화합니다.
- PRD의 우선순위에 따라 Phase 1-2를 먼저 완료한 후 Phase 3을 진행합니다.

### 테스트 순서 (중요)
- **백엔드 E2E 테스트 완료 후 프론트엔드 개발 시작**
- 각 서비스 구현 시 단위 테스트 → 통합 테스트 → E2E 테스트 순서로 진행
- Phase 1의 모든 E2E 테스트 통과 후 Phase 2 시작

