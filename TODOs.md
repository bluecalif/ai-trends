# AI Trend Monitor - 작업 계획서 (TODOs)

> 이 문서는 PRD_ai-trend.md를 바탕으로 작성된 상세 구현 계획서입니다.  
> Phase 1은 완료되었으며 핵심만 요약합니다. 상세 내용은 `TODOs_v0.md`를 참고하세요.

---

## 프로젝트 개요

**목적**: RSS 기반 AI 기술 트렌드 모니터링 서비스  
**기술 스택**: 
- Backend: Python (FastAPI), PostgreSQL (Supabase)
- Frontend: Next.js 14+ (TypeScript, Tailwind CSS)
- AI: OpenAI API (GPT-4/GPT-3.5)
- Infrastructure: Docker Compose

**핵심 원칙**:
- 원문 본문 미보관 (메타데이터, 요약, 엔티티만 저장)
- IPTC Media Topics + IAB Content Taxonomy + 커스텀 AI 태그 분류
- 인물별 사업/기술 방향 누적 타임라인
- 중복/사건 그룹화로 타임라인 구성

---

## Phase 1: 백엔드 기반 구조 ✅ (완료)

### 완료 요약

**상태**: Phase 1.1 ~ Phase 1.9 전체 완료 ✅  
**완료일**: 2025-11-19  
**프로젝트 진행률**: 백엔드 기반 구조 100% 완료

### 주요 완료 항목

#### 1.1 프로젝트 초기 설정 ✅
- Poetry 프로젝트 설정, 커서룰 파일 생성 (10개)
- FastAPI 앱 초기화, 환경변수 설정
- `backend/app/core/constants.py` 생성 (PRD_RSS_SOURCES 상수 정의)

#### 1.2 데이터베이스 스키마 ✅
- 8개 모델 생성 (Source, Item, Person, PersonTimeline, WatchRule, Bookmark, Entity, ItemEntity)
- Alembic 마이그레이션 (Supabase 연동)
- 단위/통합/E2E 테스트 통과 (27개 테스트)

#### 1.3 RSS 수집 서비스 ✅
- RSS/Atom 피드 파싱 및 정규화
- APScheduler 기반 자동 수집 (일반 소스: 20분 간격, arXiv: 하루 2회)
- 10개 RSS 소스 등록 및 수집 (TechCrunch, VentureBeat, MarkTechPost, WIRED, The Verge, IEEE Spectrum, AITimes, arXiv, OpenAI, DeepMind)
- E2E 테스트 통과 (실제 DB 데이터 사용)

#### 1.4 요약 서비스 ✅
- RSS description 사용 (MVP)
- 원문 기반 AI 요약은 Phase 3로 이동
- E2E 테스트 통과

#### 1.5 엔티티 추출 서비스 ✅
- OpenAI API로 인물/기관/기술 추출
- entities, item_entities 테이블 저장
- E2E 테스트 통과

#### 1.6 분류 서비스 ✅
- IPTC Media Topics + IAB Content Taxonomy + 커스텀 AI 태그 분류
- OpenAI(gpt-4o-mini) 기반 분류 + 휴리스틱 폴백
- E2E 테스트 통과

#### 1.7 중복/사건 묶음 서비스 ✅
- TF-IDF 유사도 기반 그룹화
- dup_group_id 할당 및 dup_group_meta 테이블
- 초기 백필/증분 모드 분리
- `/api/groups` API 엔드포인트
- E2E 테스트 통과

#### 1.8 인물 트래킹 서비스 ✅
- watch_rules 기반 키워드 매칭 (required_keywords/optional_keywords 지원)
- person_timeline 이벤트 생성
- 초기 5명 인물 규칙 생성 (Yann LeCun, Andrej Karpathy, David Luan, Llion Jones, AUI/Apollo-1)
- E2E 테스트 통과 (DB 0 문제 해결 포함)

#### 1.9 API 엔드포인트 ✅
- 29개 엔드포인트 구현 (20개 경로)
  - `/api/sources` - 소스 관리
  - `/api/items` - 아이템 조회 (필터, 페이지네이션, 정렬)
  - `/api/groups` - 사건 그룹 타임라인
  - `/api/persons` - 인물 관리 및 타임라인
  - `/api/bookmarks` - 북마크 관리
  - `/api/watch-rules` - 워치 규칙 관리
  - `/api/insights` - 인사이트 및 트렌드
- Pydantic 스키마 작성 (모든 엔티티)
- PostgreSQL JSONB 배열 검색 최적화 (`@>` 연산자)
- API 문서 확인 (FastAPI `/docs`, OpenAPI 3.1.0)
- Supabase 연동 검증 (페이지네이션, 필터링, 정렬)
- E2E 테스트 통과

### 주요 결과

- **데이터베이스**: Supabase PostgreSQL 연동 완료
- **RSS 소스**: 10개 소스 등록 및 활성화
- **수집 아이템**: 1000+ 아이템 수집 및 저장
- **API 엔드포인트**: 29개 엔드포인트 구현 및 검증 완료
- **테스트**: 모든 단위/통합/E2E 테스트 통과 (실제 DB 데이터 사용)

### 참고 파일

- **상세 계획**: `TODOs_v0.md` (Phase 1 전체 상세 내용)
- **API 문서**: `http://localhost:8000/docs` (FastAPI 자동 생성)
- **테스트 결과**: `backend/tests/results/` (E2E 테스트 결과 JSON 파일)
- **커서룰**: `.cursor/rules/` (10개 규칙 파일)

### 핵심 결정 사항

- **REF_DATE**: 매일 UTC 자정 고정
- **백필 윈도우**: REF_DATE 포함 과거 21일
- **그룹화 기준**: 신규(New) / 증분(Incremental) 분리
- **E2E 테스트**: Supabase 실제 DB 데이터 사용 (필수)
- **RSS 피드 제한**: 대부분 최근 20-30개 항목만 제공 (정기 수집으로 누적)

---

## Phase 2: 프론트엔드 UI

### 2.1 Next.js 프로젝트 설정
- [x] `frontend/` 디렉토리 생성
- [x] Next.js 14 프로젝트 초기화 (`npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`)
- [x] TypeScript 설정 확인
- [x] Tailwind CSS 설정 확인
- [x] `frontend/package.json` 의존성 추가:
  - `@tanstack/react-query`: 데이터 페칭 및 캐싱
  - `axios`: HTTP 클라이언트
  - `date-fns`: 날짜 포맷팅
  - `react-flow` 또는 `@reactflow/core`: 관계 그래프 시각화 (선택사항)
- [x] `frontend/.env.local.example` 생성 (`NEXT_PUBLIC_API_URL=http://localhost:8000`)
- [x] 기본 디렉토리 구조 생성:
  - `frontend/lib/api.ts`: API 클라이언트 (axios 기반)
  - `frontend/lib/types.ts`: TypeScript 타입 정의 (백엔드 스키마와 동기화)
  - `frontend/lib/constants.ts`: 상수 정의 (FIELDS, CUSTOM_TAGS 등)
  - `frontend/lib/validators.ts`: 런타임 검증 함수
  - `frontend/components/`: 재사용 가능한 컴포넌트
  - `frontend/app/`: Next.js App Router 페이지
- [x] **백엔드 Constants API 구현** (API Contract 동기화):
  - [x] `backend/app/api/constants.py` 생성
  - [x] `GET /api/constants/fields`: FIELDS 목록 반환
  - [x] `GET /api/constants/custom-tags`: CUSTOM_TAGS 목록 반환
  - [x] `backend/app/main.py`에 라우터 등록
- [x] API 클라이언트 구현 (`frontend/lib/api.ts`):
  - [x] axios 인스턴스 생성 (baseURL: `process.env.NEXT_PUBLIC_API_URL`)
  - [x] API 메서드 구현:
    - `getItems()`: 아이템 목록 조회 (필터, 페이지네이션, 정렬)
    - `getItem()`: 아이템 상세 조회
    - `getItemGroup()`: 사건 그룹 타임라인 조회
    - `getGroups()`: 그룹 목록 조회
    - `getPersons()`: 인물 목록 조회
    - `getPerson()`: 인물 상세 조회 (타임라인 포함)
    - `getBookmarks()`: 북마크 목록 조회
    - `createBookmark()`: 북마크 생성
    - `getSources()`: 소스 목록 조회
    - `getConstants()`: 상수 조회 (FIELDS, CUSTOM_TAGS)
    - 기타 API 메서드
  - [x] **중요**: 쿼리 파라미터는 snake_case 사용 (`date_from`, `date_to`, `page_size`, `order_by`, `order_desc` 등)
- [x] 타입 정의 (`frontend/lib/types.ts`):
  - [x] 백엔드 스키마와 일치하는 TypeScript 인터페이스 정의
  - [x] `ItemResponse`, `ItemListResponse`, `PersonResponse`, `BookmarkResponse` 등
  - [x] **체크리스트**: 필드명 일치 (snake_case), 타입 일치, Optional 필드 일치, 배열 타입 일치
- [x] 상수 정의 (`frontend/lib/constants.ts`):
  - [x] **옵션 B**: 정적 상수 정의 (백엔드와 수동 동기화) - 초기 구현
  - [x] `FIELDS`: 분야 목록 (백엔드와 동기화)
  - [x] `CUSTOM_TAGS`: 커스텀 태그 목록 (백엔드와 동기화)
  - [x] `FIELD_LABELS`: 분야 한글 레이블 매핑
  - [x] 타입 정의: `type Field = typeof FIELDS[number]`, `type CustomTag = typeof CUSTOM_TAGS[number]`
- [x] 런타임 검증 함수 (`frontend/lib/validators.ts`):
  - [x] `validateField()`: 분야 값 검증
  - [x] `validateCustomTag()`: 커스텀 태그 값 검증
  - [x] URL 파라미터 검증에 사용
- [x] **UX 확인**:
  - [x] 개발 서버 실행 (`npm run dev`) 및 기본 페이지 접근 확인
  - [x] API 클라이언트 연결 테스트 (백엔드 API 호출 확인)
  - [x] 에러 처리 및 로딩 상태 표시 확인
  - [x] 반응형 디자인 확인 (모바일/데스크톱)

### 2.2 홈/분야 탭 ✅
- [x] 기본 레이아웃 (`frontend/app/layout.tsx`):
  - [x] 네비게이션 바 (로고, 메뉴)
  - [x] 기본 스타일링 (Tailwind CSS)
  - [x] React Query Provider 설정
- [x] 홈 페이지 (`frontend/app/page.tsx`):
  - [x] "All" 옵션 추가 (모든 분야 아이템 표시)
  - [x] 분야 탭 컴포넌트 포함
  - [x] 아이템 리스트 표시
- [x] 분야별 페이지 (`frontend/app/[field]/page.tsx`):
  - [x] 동적 라우팅: `/research`, `/industry`, `/infra`, `/policy`, `/funding`
  - [x] React Query로 해당 분야 아이템 조회
  - [x] 페이지네이션 구현
  - [x] **중요**: URL 파라미터 검증 (`validateField()` 사용)
- [x] `FieldTabs` 컴포넌트 (`frontend/components/FieldTabs.tsx`):
  - [x] "All" 옵션 추가
  - [x] 5개 분야 탭 (Research, Industry, Infra, Policy, Funding)
  - [x] 현재 선택된 분야 하이라이트
  - [x] 클릭 시 해당 분야 페이지로 이동
- [x] `ItemCard` 컴포넌트 (`frontend/components/ItemCard.tsx`):
  - [x] 제목, 요약 표시
  - [x] 태그 표시 (커스텀 태그)
  - [x] 출처, 시간 표시 (date-fns 사용)
  - [x] `dup_group_id`가 있으면 "동일 사건 N건" 표시
  - [x] 클릭 시 원문 링크 이동 (새 탭)
- [x] `TagFilter` 컴포넌트 (`frontend/components/TagFilter.tsx`):
  - [x] 커스텀 태그 필터 (다중 선택 가능)
  - [x] 필터 상태 관리 (React Query 쿼리 파라미터와 연동)
  - [x] **중요**: 상수 파일의 CUSTOM_TAGS 사용 (하드코딩 금지)
- [x] 페이지네이션 컴포넌트 (`frontend/components/Pagination.tsx`):
  - [x] 페이지 번호 표시
  - [x] 이전/다음 버튼
  - [x] 총 아이템 수 표시
- [x] **백엔드 field 필터 기능 추가**:
  - [x] Item 모델에 `field` 컬럼 추가 (마이그레이션)
  - [x] 분류 서비스에 `field` 추론 로직 추가
  - [x] 백엔드 API에서 `field` 필터 활성화
  - [x] 기존 아이템에 `field` 및 `custom_tags` 업데이트 스크립트 실행
- [x] **UX 확인**:
  - [x] 홈 페이지 로딩 및 아이템 표시 확인
  - [x] "All" 탭 동작 확인
  - [x] 분야 탭 전환 동작 확인 (Research/Industry/Infra/Policy/Funding)
  - [x] 아이템 카드 클릭 시 원문 링크 이동 확인
  - [x] 태그 필터 동작 확인 (다중 선택, 필터링 결과)
  - [x] 페이지네이션 동작 확인 (이전/다음, 페이지 번호 클릭)
  - [x] 로딩 상태 표시 확인 (데이터 로딩 중)
  - [x] 에러 상태 표시 확인 (API 에러 발생 시)
  - [x] 반응형 디자인 확인 (모바일/태블릿/데스크톱)
  - [x] 태그 표시 확인

### 2.3 사건 타임라인 ✅
- [x] 사건 타임라인 페이지 (`frontend/app/story/[groupId]/page.tsx`):
  - [x] 동적 라우팅: `/story/{dup_group_id}`
  - [x] React Query로 그룹 아이템 조회 (`GET /api/items/group/{dup_group_id}`)
  - [x] 시간순 정렬된 타임라인 표시
- [x] `TimelineCard` 컴포넌트 (`frontend/components/TimelineCard.tsx`):
  - [x] 타임라인 아이템 카드
  - [x] 시간 표시 (date-fns)
  - [x] 제목, 요약, 링크 표시
  - [x] 최초 보도/후속 기사 구분 표시 ("Initial Report" 배지)
- [x] 타임라인 레이아웃:
  - [x] 수직 타임라인 UI (시간순)
  - [x] 각 아이템을 카드로 표시
  - [x] 반응형 디자인 (모바일/데스크톱)
- [x] ItemCard에 "View story" 링크 추가:
  - [x] `dup_group_id`가 있을 때만 표시
  - [x] `/story/{dup_group_id}`로 이동
- [x] **참고**: 중복 그룹화 실행 및 백필은 Phase 3.5에서 진행 (백엔드 작업)
- [ ] **UX 확인** (dup_group_id가 있는 아이템 필요):
  - [ ] 사건 타임라인 페이지 접근 확인 (`/story/{dup_group_id}`)
  - [ ] 타임라인 아이템 시간순 정렬 확인
  - [ ] 타임라인 카드 클릭 시 원문 링크 이동 확인
  - [ ] 최초 보도/후속 기사 구분 표시 확인
  - [ ] 로딩 상태 표시 확인
  - [ ] 에러 상태 표시 확인 (그룹이 없거나 아이템이 없는 경우)
  - [ ] 반응형 디자인 확인 (모바일/태블릿/데스크톱)
  - [ ] 접근성 확인 (키보드 네비게이션)

### 2.4 인물 페이지
- [ ] 인물 목록 페이지 (`frontend/app/persons/page.tsx`):
  - [ ] 인물 리스트 표시
  - [ ] 검색 기능 (이름 기반)
  - [ ] 정렬 (이름순, 최근 이벤트순)
- [ ] 인물 상세 페이지 (`frontend/app/persons/[id]/page.tsx`):
  - [ ] 인물 정보 표시 (이름, bio)
  - [ ] 타임라인 표시 (PersonTimeline 이벤트)
  - [ ] 관계 그래프 시각화 (선택사항)
- [ ] `PersonCard` 컴포넌트 (`frontend/components/PersonCard.tsx`):
  - [ ] 인물 카드 (목록용)
  - [ ] 이름, bio 미리보기
  - [ ] 최근 이벤트 수 표시
- [ ] `RelationshipGraph` 컴포넌트 (`frontend/components/RelationshipGraph.tsx`):
  - [ ] 인물-기술-기관-사건 관계 그래프
  - [ ] react-flow 또는 d3.js 사용 (선택사항)
  - [ ] 노드 클릭 시 상세 정보 표시
- [ ] **UX 확인**:
  - [ ] 인물 목록 페이지 접근 및 표시 확인 (`/persons`)
  - [ ] 인물 검색 기능 동작 확인
  - [ ] 인물 정렬 기능 확인 (이름순, 최근 이벤트순)
  - [ ] 인물 상세 페이지 접근 확인 (`/persons/{id}`)
  - [ ] 인물 타임라인 표시 확인
  - [ ] 관계 그래프 표시 및 인터랙션 확인 (노드 클릭, 확대/축소)
  - [ ] 로딩 상태 표시 확인
  - [ ] 에러 상태 표시 확인 (인물이 없거나 데이터가 없는 경우)
  - [ ] 반응형 디자인 확인 (모바일/태블릿/데스크톱)
  - [ ] 접근성 확인 (키보드 네비게이션, 그래프 대체 텍스트)

### 2.5 저장함 (북마크)
- [ ] 저장함 페이지 (`frontend/app/saved/page.tsx`):
  - [ ] 북마크 목록 표시
  - [ ] 태그 필터링
  - [ ] 검색 기능 (제목 기반)
- [ ] `BookmarkCard` 컴포넌트 (`frontend/components/BookmarkCard.tsx`):
  - [ ] 북마크 카드
  - [ ] 제목, 메모, 태그 표시
  - [ ] 원문 링크 이동
  - [ ] 삭제 버튼
- [ ] `TagManager` 컴포넌트 (`frontend/components/TagManager.tsx`):
  - [ ] 태그 추가/삭제 UI
  - [ ] 태그 목록 표시
  - [ ] 태그 필터링
- [ ] 북마크 추가 기능:
  - [ ] 아이템 카드에 "저장" 버튼 추가
  - [ ] 북마크 생성 모달/폼
- [ ] **UX 확인**:
  - [ ] 저장함 페이지 접근 및 북마크 목록 표시 확인 (`/saved`)
  - [ ] 북마크 추가 기능 확인 (아이템 카드의 "저장" 버튼)
  - [ ] 북마크 생성 모달/폼 동작 확인
  - [ ] 북마크 태그 필터링 동작 확인
  - [ ] 북마크 검색 기능 확인 (제목 기반)
  - [ ] 북마크 태그 추가/삭제 기능 확인
  - [ ] 북마크 삭제 기능 확인
  - [ ] 북마크 원문 링크 이동 확인
  - [ ] 로딩 상태 표시 확인
  - [ ] 에러 상태 표시 확인 (북마크가 없거나 API 에러 발생 시)
  - [ ] 반응형 디자인 확인 (모바일/태블릿/데스크톱)
  - [ ] 접근성 확인 (키보드 네비게이션, 폼 접근성)

### 2.6 설정 페이지
- [ ] 설정 페이지 (`frontend/app/settings/page.tsx`):
  - [ ] 소스 관리 섹션
  - [ ] 워치 규칙 관리 섹션
  - [ ] 탭 또는 섹션으로 구분
- [ ] 소스 관리 UI:
  - [ ] 소스 목록 표시 (`GET /api/sources`)
  - [ ] 소스 추가 폼 (`POST /api/sources`)
  - [ ] 소스 수정/삭제 (`PATCH /DELETE /api/sources/{id}`)
  - [ ] 활성화/비활성화 토글
  - [ ] OPML Import/Export 버튼 (Phase 3에서 구현)
- [ ] 워치 규칙 관리 UI:
  - [ ] 규칙 목록 표시 (`GET /api/watch-rules`)
  - [ ] 규칙 추가 폼 (`POST /api/watch-rules`)
  - [ ] 규칙 수정/삭제 (`PATCH /DELETE /api/watch-rules/{id}`)
  - [ ] JSON 편집기 (required_keywords, optional_keywords 편집)
- [ ] `OPMLImporter` 컴포넌트 (`frontend/components/OPMLImporter.tsx`):
  - [ ] OPML 파일 업로드 UI (Phase 3에서 구현)
  - [ ] 파일 선택 및 업로드
- [ ] `WatchRuleEditor` 컴포넌트 (`frontend/components/WatchRuleEditor.tsx`):
  - [ ] 워치 규칙 편집 폼
  - [ ] required_keywords, optional_keywords 입력
  - [ ] JSON 편집 모드
- [ ] **UX 확인**:
  - [ ] 설정 페이지 접근 및 섹션 구분 확인 (`/settings`)
  - [ ] 소스 관리 UI 동작 확인:
    - [ ] 소스 목록 표시
    - [ ] 소스 추가 폼 동작
    - [ ] 소스 수정/삭제 동작
    - [ ] 활성화/비활성화 토글 동작
  - [ ] 워치 규칙 관리 UI 동작 확인:
    - [ ] 규칙 목록 표시
    - [ ] 규칙 추가 폼 동작
    - [ ] 규칙 수정/삭제 동작
    - [ ] JSON 편집기 동작 확인
  - [ ] 폼 유효성 검증 확인 (필수 필드, 형식 검증)
  - [ ] 성공/실패 피드백 확인 (저장 성공, 에러 메시지)
  - [ ] 로딩 상태 표시 확인
  - [ ] 에러 상태 표시 확인
  - [ ] 반응형 디자인 확인 (모바일/태블릿/데스크톱)
  - [ ] 접근성 확인 (키보드 네비게이션, 폼 접근성, 에러 메시지 접근성)

---

## Phase 3: 고급 기능

### 3.1 고급 요약 서비스 (원문 기반 AI 요약)
- [ ] `backend/app/services/summarizer.py` 확장:
  - [ ] 원문 일시 로드 함수 (httpx)
  - [ ] OpenAI API로 1-2문장 요약 생성 함수
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
- [ ] **중복 그룹화 실행 및 백필** (Phase 1.7 기본 그룹화 완료, 실행 필요):
  - [ ] 백필 스크립트 실행 (`backend/scripts/run_backfill.py`)
  - [ ] 기존 아이템에 `dup_group_id` 할당
  - [ ] 증분 모드로 신규 아이템 그룹화
  - [ ] 그룹화 결과 검증 (`/api/groups` API 테스트)
- [ ] **고급 최적화** (임베딩/LSH 기반):
  - [ ] 임베딩 기반 유사도(예: text-embedding-3-small) 도입 + 코사인 유사도
  - [ ] LSH/ANN을 활용한 후보 축소 후 정밀 판별(성능 최적화)
  - [ ] 사건 시드 모델: 초기 보도 식별 → 시간/엔티티/출처 가중으로 후속 기사 점수화
  - [ ] 문장/문단 의미 유사도(파라프레이즈) 모델 평가 및 통합
- [ ] **E2E 테스트(실데이터)**: 임베딩/LSH 파이프라인으로 그룹 생성률/정확도 비교, 결과 JSON 저장

### 3.6 소스 재활성화(DeepMind)
- [ ] DeepMind 수집 재개(Phase 3)
  - [ ] The Keyword 전체 피드(`https://blog.google/feed/`) 구독
  - [ ] 카테고리 메타 기반 필터("Google DeepMind") + 백업 키워드(`deepmind`, `/technology/google-deepmind/`)
  - [ ] 초기 E2E: 수집 → 요약 → 분류 → 그룹핑 → `/api/groups` 노출 검증(결과 JSON 저장)

---

## Phase 4: 통합 테스트 및 E2E 검증

**참고**: 단위 테스트와 통합 테스트는 각 Phase(1, 2, 3)의 서브섹션에 포함되어 있습니다.
이 Phase 4는 전체 시스템 통합 테스트와 E2E 검증에 집중합니다.

### 4.1 백엔드-프론트엔드 연동 테스트

- [ ] 백엔드-프론트엔드 API 연동 테스트
- [ ] 전체 플로우 테스트 (RSS 수집 → 처리 → UI 표시)
- [ ] 에러 처리 및 복구 테스트
- [ ] CORS 및 인증 테스트

### 4.2 전체 시스템 E2E 테스트
**중요: E2E 테스트는 Supabase 실제 DB 데이터 사용 (필수)**
- 모든 E2E 테스트는 테스트 DB가 아닌 **Supabase 실제 DB**에서 데이터를 가져와야 함
- `backend/app/core/database.py`의 `SessionLocal()`을 사용하여 실제 DB 연결
- 테스트는 실제 수집된 뉴스 아이템으로 검증해야 함
- DB에 데이터가 없는 경우: 수집 먼저 실행 또는 기존 데이터 활용
- 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장 (필수)

- [x] 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장 (필수)
- [x] **RSS 수집 E2E**: 소스 등록 → 수집 → **Supabase 실제 DB** 저장 확인 (Phase 1.3에서 완료)
- [x] **요약 E2E**: **실제 DB의 아이템** → 요약 생성 → 저장 확인 (Phase 1.4에서 완료)
- [x] **분류 E2E**: **실제 DB의 아이템** → IPTC/IAB/커스텀 태그 분류 → 저장 확인 (Phase 1.6에서 완료)
- [x] **엔티티 추출 E2E**: **실제 DB의 아이템** → 엔티티 추출 → 관계 저장 확인 (Phase 1.5에서 완료)
- [x] **중복 그룹화 E2E**: **실제 DB의 아이템**으로 초기 백필(21일) + 증분(REF_DATE 이후) → 그룹/타임라인/메타 조회 확인 (Phase 1.7에서 완료)
- [x] **인물 트래킹 E2E**: **실제 DB의 아이템**으로 워치 규칙 → 매칭 → 타임라인 생성 확인 (Phase 1.8에서 완료)
- [ ] **API 전체 플로우 E2E**: 소스 추가 → 수집 → 처리 → API 조회 (모든 필터/정렬) - **실제 DB 데이터 사용**
- [ ] **폴링 작업자 E2E**: 스케줄러 실행 → 자동 수집 → 처리 파이프라인 확인 - **실제 DB 데이터 사용**
- [ ] **성능 테스트**: 대량 데이터 처리 (1000+ 아이템) - **실제 DB 데이터 사용**

---

## Phase 5: 프로덕션 준비

### 5.1 초기 데이터 설정 스크립트 정리
- [x] `backend/app/core/constants.py` 생성 완료 확인
- [x] `backend/scripts/init_sources.py` 리팩토링 완료 확인
- [x] 테스트 파일 리팩토링 완료 확인
- [ ] 초기 데이터 설정 가이드 문서화

### 5.2 환경 설정 및 문서화
- [ ] 프로덕션 환경변수 설정 가이드 작성
- [ ] 데이터베이스 마이그레이션 가이드 작성
- [ ] API 문서 정리 (FastAPI 자동 생성 `/docs`)
- [ ] 사용자 가이드 작성
- [ ] 개발자 가이드 작성

### 5.3 성능 최적화 및 모니터링 설정
- [ ] 로깅 설정:
  - 개발: 콘솔 출력
  - 프로덕션: 구조화된 로그 (JSON 형식)
- [ ] 에러 추적: Sentry 또는 유사 서비스 연동 (선택사항)
- [ ] Health check 모니터링:
  - `/health` 엔드포인트
  - 스케줄러 상태 확인
- [ ] 메트릭 수집 (선택사항):
  - 수집된 아이템 수
  - API 응답 시간
  - 에러율

---

## Phase 6: 배포

### 6.1 배포 아키텍처 (Vercel 중심)

**배포 전략**:
- **프론트엔드**: Vercel에 배포 (Next.js 최적화)
- **백엔드 API**: Vercel Serverless Functions 또는 별도 서버 (Railway/Render/Fly.io)
- **스케줄러**: 별도 워커 프로세스 필요 (Vercel Cron Jobs 또는 외부 서비스)

**Vercel 제약사항**:
- Serverless Functions는 요청 기반 실행 (장기 실행 작업 불가)
- APScheduler는 stateless 환경에서 제대로 작동하지 않음
- 스케줄러는 별도 프로세스로 분리 필요

**권장 아키텍처**:
```
┌─────────────────┐
│  Vercel (Next.js) │  ← 프론트엔드
└────────┬────────┘
         │ API 호출
┌────────▼────────┐
│ Backend API      │  ← Vercel Functions 또는 별도 서버
│ (FastAPI)        │
└────────┬────────┘
         │
┌────────▼────────┐
│ Supabase (DB)   │
└─────────────────┘
         │
┌────────▼────────┐
│ Worker Process  │  ← 별도 서버 (스케줄러)
│ (APScheduler)   │
└─────────────────┘
```

### 6.2 프론트엔드 배포 (Vercel)

- [ ] `frontend/vercel.json` 생성 (Next.js 설정)
- [ ] `frontend/.env.production` 또는 Vercel 환경변수 설정:
  - `NEXT_PUBLIC_API_URL`: 백엔드 API URL
  - 기타 프론트엔드 환경변수
- [ ] Vercel 프로젝트 생성 및 연결
- [ ] 빌드 설정 확인 (`next build` 성공 확인)
- [ ] 도메인 설정 (선택사항)

### 6.3 백엔드 배포 옵션

#### 옵션 A: Vercel Serverless Functions (제한적)
- [ ] `api/` 디렉토리에 FastAPI 핸들러 래퍼 생성
- [ ] Vercel Functions 제약사항 확인:
  - 최대 실행 시간: 10초 (Hobby), 60초 (Pro)
  - 메모리 제한: 1024MB
  - Cold start 고려
- [ ] API 엔드포인트별 함수 분리 또는 단일 함수로 라우팅
- [ ] 환경변수 설정 (Vercel 대시보드)

#### 옵션 B: 별도 서버 (권장 - 스케줄러 포함)
- [ ] Railway/Render/Fly.io 중 선택
- [ ] Dockerfile 생성 (또는 플랫폼별 설정)
- [ ] 환경변수 설정:
  - `DATABASE_URL`: Supabase 연결 문자열
  - `OPENAI_API_KEY`: OpenAI API 키
  - `RSS_COLLECTION_INTERVAL_MINUTES`: 수집 주기
  - `CORS_ORIGINS`: 프론트엔드 도메인
- [ ] 서버 시작 명령: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Health check 엔드포인트 확인 (`/health`)

### 6.4 스케줄러 워커 배포

**문제**: Vercel Serverless Functions는 스케줄러 실행에 부적합

**해결 방안**:

#### 옵션 1: Vercel Cron Jobs (간단한 작업용)
- [ ] `vercel.json`에 cron 설정 추가
- [ ] Cron Job이 호출할 API 엔드포인트 생성 (`/api/cron/collect`, `/api/cron/grouping`)
- [ ] 제한: 최대 1분 실행 시간, 복잡한 작업에는 부적합

#### 옵션 2: 별도 워커 서버 (권장)
- [x] 스케줄러 전용 스크립트 생성 (`backend/scripts/worker.py`) - 완료
- [ ] Railway/Render/Fly.io에 워커 프로세스 배포
- [ ] 환경변수: 백엔드와 동일
- [ ] 실행 명령: `poetry run python -m backend.scripts.worker` (스케줄러만 실행)

#### 옵션 3: 외부 스케줄러 서비스
- [ ] GitHub Actions (Scheduled workflows)
- [ ] EasyCron, Cron-job.org 등
- [ ] 주기적으로 API 엔드포인트 호출 (`/api/rss/collect-all`, `/api/cron/backfill`)

### 6.5 환경 변수 설정

- [ ] 프론트엔드 (Vercel) 환경변수 설정:
  - `NEXT_PUBLIC_API_URL`: 백엔드 API URL (예: `https://api.example.com`)
  - 기타 Next.js 환경변수
- [ ] 백엔드 (별도 서버 또는 Vercel Functions) 환경변수 설정:
  - `DATABASE_URL`: Supabase PostgreSQL 연결 문자열
  - `OPENAI_API_KEY`: OpenAI API 키
  - `RSS_COLLECTION_INTERVAL_MINUTES`: RSS 수집 주기 (기본: 20)
  - `CORS_ORIGINS`: 프론트엔드 도메인 (쉼표 구분)
  - `DEBUG`: `false` (프로덕션)
- [ ] 워커 (별도 서버) 환경변수 설정:
  - 백엔드와 동일한 환경변수

### 6.6 데이터베이스 마이그레이션

- [ ] 프로덕션 DB에 마이그레이션 적용:
  ```bash
  cd backend
  DATABASE_URL="..." alembic upgrade head
  ```
- [ ] 마이그레이션 롤백 전략 수립
- [ ] 백업 전략 수립 (Supabase 자동 백업 활용)

---

## 진행 상황 추적

**마지막 업데이트**: 2025-11-19 (Phase 1 완료 ✅, Phase 2.1 완료 ✅, Phase 2.2 완료 ✅, Phase 2.3 완료 ✅)

**프로젝트 진행률**: 백엔드 기반 구조 100% 완료, 프론트엔드 Phase 2.3 완료

**현재 단계**: Phase 2.4 (인물 페이지) 시작

**Phase 구조**:
- **Phase 1**: 백엔드 기반 구조 ✅ (완료)
- **Phase 2**: 프론트엔드 UI (진행 중)
- **Phase 3**: 고급 기능
- **Phase 4**: 통합 테스트 및 E2E 검증
- **Phase 5**: 프로덕션 준비
- **Phase 6**: 배포

---

## 참고사항

### 테스트 전략

**E2E 테스트 데이터 준비 규칙 (필수 - 모든 Phase 적용)**:
- ⚠️ **절대 금지**: DB에 아이템이 0개인 상태로 테스트 진행
- ✅ **필수 준수 사항**:
  1. **소스 확인/생성**: 테스트 시작 시 `PRD_RSS_SOURCES`에서 소스 확인, 없으면 생성 (`is_active=True`)
  2. **기존 아이템 우선 조회**: DB에서 기존 아이템 먼저 조회 (21일 윈도우 또는 전체)
  3. **수집은 보조**: 기존 아이템이 없을 때만 RSS 수집 시도
  4. **최종 검증**: 아이템이 0개면 테스트 실패 (명확한 에러 메시지와 함께)

**E2E 테스트 데이터 소스 규칙 (필수)**:
- ✅ **E2E 테스트**: Supabase 실제 DB에서 데이터 가져오기 (`SessionLocal()` 사용)
- ✅ **단위/통합 테스트**: 테스트 DB 사용 (격리된 테스트 환경)

상세 내용은 `TODOs_v0.md` 및 `.cursor/rules/testing-strategy.mdc`를 참고하세요.

---

## API Contract 동기화 (중요 - 필수 준수)

### 원칙: 단일 진실 공급원 (Single Source of Truth)
백엔드가 상수와 스키마의 진실 공급원이며, 프론트엔드는 이를 정확히 반영해야 함.

### 필수 체크리스트

#### 백엔드 Constants API 구현 (Phase 2.1)
- [ ] `backend/app/api/constants.py` 생성
- [ ] `GET /api/constants/fields`: FIELDS 목록 반환
- [ ] `GET /api/constants/custom-tags`: CUSTOM_TAGS 목록 반환
- [ ] `backend/app/main.py`에 라우터 등록

#### 프론트엔드 상수 정의 전략
- [ ] **옵션 A (권장)**: Constants API 사용 (런타임 동기화)
- [ ] **옵션 B**: 정적 상수 정의 (백엔드와 수동 동기화)
- [ ] `frontend/lib/constants.ts`에 상수 정의
- [ ] 타입 정의: `type Field = typeof FIELDS[number]`, `type CustomTag = typeof CUSTOM_TAGS[number]`

#### 타입 정의 동기화
- [ ] 필드명 일치 (camelCase vs snake_case 주의 - 백엔드는 snake_case)
- [ ] 타입 일치 (string, number, boolean, Date → string)
- [ ] Optional 필드 일치
- [ ] 배열 타입 일치 (List[str] → string[])

#### API 클라이언트 쿼리 파라미터 동기화
- [ ] 백엔드는 snake_case 사용, 프론트엔드도 동일하게 사용
- [ ] `date_from`, `date_to`, `page_size`, `order_by`, `order_desc` 등
- [ ] axios가 자동으로 snake_case 유지

#### 런타임 검증 함수
- [ ] `frontend/lib/validators.ts` 생성
- [ ] `validateField()`: 분야 값 검증
- [ ] `validateCustomTag()`: 커스텀 태그 값 검증
- [ ] URL 파라미터 검증에 사용

#### Common Pitfalls 방지
- [ ] 하드코딩된 문자열 사용 금지 (상수 파일 사용)
- [ ] camelCase vs snake_case 혼용 금지
- [ ] 태그 값 대소문자 일치 확인 (예: "agents" vs "Agents")
- [ ] Query 파라미터 이름 일치 확인
- [ ] Enum 값 문자열 일치 확인

### 동기화 검증 방법
- **타입 체크**: TypeScript 컴파일 시 타입 불일치 감지
- **런타임 검증**: API 호출 시 백엔드 에러 응답으로 검증
- **수동 검증**: 백엔드 스키마 파일과 프론트엔드 타입 파일 비교

**참고 규칙**: `.cursor/rules/api-contract-sync.mdc` 상세 내용 확인