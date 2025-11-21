# AI Trend Monitor - 작업 계획서 (TODOs)

> 이 문서는 PRD_ai-trend.md를 바탕으로 작성된 상세 구현 계획서입니다.  
> Phase 1, 2는 완료되었으며 핵심만 요약합니다. 상세 내용은 `v1_TODOs.md`를 참고하세요.

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
- 원문 기반 AI 요약은 Phase 6로 이동
- E2E 테스트 통과

#### 1.5 엔티티 추출 서비스 ✅
- OpenAI API로 인물/기관/기술 추출
- entities, item_entities 테이블 저장
- E2E 테스트 통과

#### 1.6 분류 서비스 ✅
- IPTC Media Topics + IAB Content Taxonomy + 커스텀 AI 태그 분류
- OpenAI(gpt-4o-mini) 기반 분류 + 휴리스틱 폴백
- field 추론 로직 추가 (research, industry, infra, policy, funding)
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
  - `/api/constants` - 상수 제공 (FIELDS, CUSTOM_TAGS)
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

- **상세 계획**: `v1_TODOs.md` (Phase 1, 2 전체 상세 내용)
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

## Phase 2: 프론트엔드 UI ✅ (완료)

### 완료 요약

**상태**: Phase 2.1 ~ Phase 2.6 전체 완료 ✅  
**완료일**: 2025-11-19  
**프로젝트 진행률**: 프론트엔드 UI 100% 완료

### 주요 완료 항목

#### 2.1 Next.js 프로젝트 설정 ✅
- Next.js 14 프로젝트 초기화 (TypeScript, Tailwind CSS, App Router)
- 의존성 설치: `@tanstack/react-query`, `axios`, `date-fns`
- API 클라이언트 구현 (`frontend/lib/api.ts`)
- 타입 정의 (`frontend/lib/types.ts`) - 백엔드 스키마와 동기화
- 상수 정의 (`frontend/lib/constants.ts`) - FIELDS, CUSTOM_TAGS
- 런타임 검증 함수 (`frontend/lib/validators.ts`)
- 백엔드 Constants API 구현 (`/api/constants/fields`, `/api/constants/custom-tags`)

#### 2.2 홈/분야 탭 ✅
- 기본 레이아웃 및 네비게이션 바
- 홈 페이지 ("All" 옵션 포함)
- 분야별 페이지 (`/research`, `/industry`, `/infra`, `/policy`, `/funding`)
- `FieldTabs` 컴포넌트 (분야 탭 네비게이션)
- `ItemCard` 컴포넌트 (아이템 카드 표시)
- `TagFilter` 컴포넌트 (태그 필터링)
- `Pagination` 컴포넌트 (페이지네이션)
- 백엔드 field 필터 기능 추가 및 백필

#### 2.3 사건 타임라인 ✅
- 사건 타임라인 페이지 (`/story/[groupId]`)
- `TimelineCard` 컴포넌트
- ItemCard에 "View story" 링크 추가
- **참고**: 중복 그룹화 실행 및 백필은 Phase 6.5에서 진행

#### 2.4 인물 페이지 ✅
- 인물 목록 페이지 (`/persons`)
- 인물 상세 페이지 (`/persons/[id]`)
- `PersonCard` 컴포넌트
- 검색 및 정렬 기능
- 타임라인 표시
- 관계 그래프 플레이스홀더 (Phase 6에서 구현 예정)

#### 2.5 저장함 (북마크) ✅
- 저장함 페이지 (`/saved`)
- `BookmarkCard` 컴포넌트
- `BookmarkModal` 컴포넌트 (북마크 생성)
- ItemCard에 "저장" 버튼 추가
- 태그 필터링 및 검색 기능
- 기존 태그 자동완성 기능
- 북마크 삭제 기능

#### 2.6 설정 페이지 ✅
- 설정 페이지 (`/settings`) - 탭으로 구분
- `SourcesSection` 컴포넌트 (소스 관리)
- `WatchRulesSection` 컴포넌트 (워치 규칙 관리)
- 소스 추가/수정/삭제 기능
- 소스 활성화/비활성화 토글
- 워치 규칙 추가/수정/삭제 기능
- 워치 규칙 JSON 편집 모드 (Form/JSON 전환)
- Watch Rules 라벨을 인물 이름으로 자동 설정
- Watch Rules 모달에서 인물 추가 기능

### 주요 결과

- **프론트엔드 구조**: Next.js 14 App Router 기반 완성
- **페이지**: 6개 주요 페이지 구현 (홈, 분야별, 타임라인, 인물, 저장함, 설정)
- **컴포넌트**: 15+ 재사용 가능한 컴포넌트 구현
- **API 연동**: 모든 백엔드 API 엔드포인트 연동 완료
- **UX 검증**: 모든 페이지 UX 확인 완료

### 참고 파일

- **상세 계획**: `v1_TODOs.md` (Phase 2 전체 상세 내용)
- **프론트엔드 코드**: `frontend/` 디렉토리

---

## Phase 3: 통합 테스트 및 E2E 검증 ✅ (완료)

**참고**: 단위 테스트와 통합 테스트는 각 Phase(1, 2)의 서브섹션에 포함되어 있습니다.
이 Phase 3는 전체 시스템 통합 테스트와 E2E 검증에 집중합니다.

### 완료 요약

**상태**: Phase 3.1 ~ Phase 3.2 전체 완료 ✅  
**완료일**: 2025-11-20  
**프로젝트 진행률**: 통합 테스트 및 E2E 검증 100% 완료

**중요: E2E 테스트는 Supabase 실제 DB 데이터 사용 (필수)**
- 모든 E2E 테스트는 테스트 DB가 아닌 **Supabase 실제 DB**에서 데이터를 가져와야 함
- `backend/app/core/database.py`의 `SessionLocal()`을 사용하여 실제 DB 연결
- 테스트는 실제 수집된 뉴스 아이템으로 검증해야 함
- DB에 데이터가 없는 경우: 수집 먼저 실행 또는 기존 데이터 활용
- 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장 (필수)

### 3.1 백엔드-프론트엔드 연동 테스트

#### 3.1.1 API 연동 테스트 ✅
- [x] **파일**: `backend/tests/integration/test_frontend_backend_integration.py` 생성
- [x] **내용**:
  - 프론트엔드 API 클라이언트(`frontend/lib/api.ts`)와 백엔드 API 엔드포인트 연동 검증
  - 모든 API 엔드포인트에 대한 요청/응답 형식 검증
  - 타입 일치 검증 (Pydantic 스키마 ↔ TypeScript 타입)
- [x] **검증 항목**:
  - Items API: 목록 조회, 필터링, 페이지네이션, 정렬
  - Sources API: CRUD 작업
  - Persons API: 목록, 상세, 타임라인, 관계 그래프
  - Bookmarks API: 생성, 조회, 삭제
  - Watch Rules API: CRUD 작업
  - Insights API: 주간 인사이트, 키워드 트렌드, 인물별 인사이트
  - Constants API: FIELDS, CUSTOM_TAGS

#### 3.1.2 전체 플로우 테스트 (RSS 수집 → 처리 → UI 표시) ✅
- [x] **파일**: `backend/tests/e2e/test_full_pipeline_e2e.py` 생성
- [x] **내용**:
  - RSS 수집 → 요약 → 분류 → 엔티티 추출 → 그룹화 → 인물 트래킹 → API 조회 → 프론트엔드 표시 시뮬레이션
  - 실제 DB 데이터를 사용하여 전체 파이프라인 검증
  - 각 단계별 데이터 상태 확인
- [x] **검증 항목**:
  - 수집된 아이템이 DB에 저장되는지 확인
  - 요약/분류/엔티티 추출이 정상 수행되는지 확인
  - 그룹화가 정상 수행되는지 확인
  - 인물 트래킹이 정상 수행되는지 확인
  - API를 통해 데이터가 정상 조회되는지 확인
  - 결과 JSON 파일 저장 (`backend/tests/results/`)

#### 3.1.3 에러 처리 및 복구 테스트 ✅
- [x] **파일**: `backend/tests/integration/test_error_handling.py` 생성
- [x] **내용**:
  - 잘못된 요청에 대한 에러 응답 검증
  - 존재하지 않는 리소스 조회 시 404 검증
  - 잘못된 필터 값에 대한 400 검증
  - DB 연결 실패 시 에러 처리 검증
  - OpenAI API 실패 시 폴백 로직 검증
- [x] **검증 항목**:
  - HTTP 상태 코드 정확성
  - 에러 메시지 명확성
  - 에러 발생 후 시스템 복구 가능 여부

#### 3.1.4 CORS 및 인증 테스트 ✅
- [x] **파일**: `backend/tests/integration/test_cors.py` 생성
- [x] **내용**:
  - CORS 설정 검증 (`backend/app/main.py`의 CORS 설정)
  - 프론트엔드 도메인에서의 API 호출 시뮬레이션
  - OPTIONS 요청 처리 검증
  - 인증이 필요한 경우를 위한 준비 (현재는 인증 없음, 향후 확장 대비)
- [x] **검증 항목**:
  - 허용된 Origin에서의 요청 성공
  - 허용되지 않은 Origin에서의 요청 차단
  - CORS 헤더 정확성

### 3.2 전체 시스템 E2E 테스트

#### 완료된 E2E 테스트 (Phase 1에서 완료)
- [x] 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장 (필수)
- [x] **RSS 수집 E2E**: 소스 등록 → 수집 → **Supabase 실제 DB** 저장 확인 (Phase 1.3에서 완료)
- [x] **요약 E2E**: **실제 DB의 아이템** → 요약 생성 → 저장 확인 (Phase 1.4에서 완료)
- [x] **분류 E2E**: **실제 DB의 아이템** → IPTC/IAB/커스텀 태그 분류 → 저장 확인 (Phase 1.6에서 완료)
- [x] **엔티티 추출 E2E**: **실제 DB의 아이템** → 엔티티 추출 → 관계 저장 확인 (Phase 1.5에서 완료)
- [x] **중복 그룹화 E2E**: **실제 DB의 아이템**으로 초기 백필(21일) + 증분(REF_DATE 이후) → 그룹/타임라인/메타 조회 확인 (Phase 1.7에서 완료)
- [x] **인물 트래킹 E2E**: **실제 DB의 아이템**으로 워치 규칙 → 매칭 → 타임라인 생성 확인 (Phase 1.8에서 완료)

#### 3.2.1 API 전체 플로우 E2E (실행 및 검증) ✅
- [x] **파일**: `backend/tests/e2e/test_api_e2e.py` (이미 존재)
- [x] **작업**:
  - 테스트 실행 및 결과 검증
  - 모든 엔드포인트가 정상 동작하는지 확인
  - 결과 JSON 파일 검토 및 문제점 파악
  - 필요 시 테스트 보완
- [x] **실행 명령**: `poetry run python -m pytest backend/tests/e2e/test_api_e2e.py -v -s -m e2e_real_data`
- [x] **검증 항목**:
  - Items API: 목록, 상세, 필터, 그룹 조회
  - Sources API: 목록, 상세
  - Persons API: 목록, 상세, 타임라인, 관계 그래프
  - Bookmarks API: 목록, 생성, 삭제
  - Watch Rules API: 목록, 상세
  - Insights API: 주간, 키워드, 인물별

#### 3.2.2 폴링 작업자 E2E ✅
- [x] **파일**: `backend/tests/e2e/test_worker_e2e.py` 생성
- [x] **내용**:
  - Worker 프로세스(`backend/scripts/worker.py`) 실행 시뮬레이션
  - 스케줄러가 정상 시작되는지 확인
  - RSS 수집 작업이 스케줄대로 실행되는지 확인
  - 증분 그룹화 작업이 스케줄대로 실행되는지 확인
  - 일일 백필 작업이 스케줄대로 실행되는지 확인
  - Worker 프로세스 종료 시 정상 종료되는지 확인
- [x] **검증 항목**:
  - 스케줄러 시작/종료 정상 동작
  - RSS 수집 작업 실행 (20분 간격)
  - arXiv 수집 작업 실행 (하루 2회)
  - 증분 그룹화 작업 실행 (20분 간격)
  - 일일 백필 작업 실행 (UTC 00:00)
  - 결과 JSON 파일 저장

#### 3.2.3 성능 테스트 ✅
- [x] **파일**: `backend/tests/e2e/test_performance_e2e.py` 생성
- [x] **내용**:
  - 대량 데이터 처리 성능 검증 (1000+ 아이템)
  - API 응답 시간 측정
  - 페이지네이션 성능 검증
  - 필터링 성능 검증
  - 정렬 성능 검증
  - 동시 요청 처리 성능 검증
- [x] **검증 항목**:
  - 1000+ 아이템 조회 시 응답 시간 < 2초
  - 페이지네이션 응답 시간 < 1초
  - 필터링 응답 시간 < 1초
  - 정렬 응답 시간 < 1초
  - 동시 요청(10개) 처리 성능
  - 결과 JSON 파일 저장 (성능 메트릭 포함)

### 테스트 실행 전략

#### 필수 준수 사항
1. **실제 DB 데이터 사용**: 모든 E2E 테스트는 Supabase 실제 DB 사용 (`SessionLocal()`)
2. **데이터 준비**: 소스 확인/생성 → 기존 아이템 조회 → 없으면 수집
3. **결과 저장**: 모든 E2E 테스트 결과는 `backend/tests/results/`에 JSON 파일로 저장
4. **아이템 0개 금지**: 테스트 시작 전 반드시 아이템 존재 확인

#### 테스트 실행 순서
1. API 전체 플로우 E2E 실행 및 검증
2. 백엔드-프론트엔드 연동 테스트 작성 및 실행
3. 전체 플로우 테스트 작성 및 실행
4. 에러 처리 테스트 작성 및 실행
5. CORS 테스트 작성 및 실행
6. 폴링 작업자 E2E 작성 및 실행
7. 성능 테스트 작성 및 실행

### 예상 결과물

#### 테스트 파일
- `backend/tests/integration/test_frontend_backend_integration.py`
- `backend/tests/integration/test_error_handling.py`
- `backend/tests/integration/test_cors.py`
- `backend/tests/e2e/test_full_pipeline_e2e.py`
- `backend/tests/e2e/test_worker_e2e.py`
- `backend/tests/e2e/test_performance_e2e.py`

#### 결과 파일
- `backend/tests/results/full_pipeline_e2e_*.json`
- `backend/tests/results/worker_e2e_*.json`
- `backend/tests/results/performance_e2e_*.json`

### 완료 조건

- [x] 모든 통합 테스트 통과
- [x] 모든 E2E 테스트 통과 (실제 DB 데이터 사용)
- [x] 모든 테스트 결과 JSON 파일 저장
- [x] 성능 테스트 통과 (목표 성능 달성)
- [x] Phase 3 완료 처리 (TODOs.md 업데이트)

### 주요 결과

- **통합 테스트**: 3개 테스트 파일 작성 및 통과
  - API 연동 테스트: 프론트엔드-백엔드 계약 검증
  - 에러 처리 테스트: 404, 400, 422 등 에러 시나리오 검증
  - CORS 테스트: CORS 설정 및 OPTIONS 요청 검증
- **E2E 테스트**: 3개 E2E 테스트 파일 작성 및 통과
  - 전체 플로우 테스트: RSS 수집 → 처리 → API 조회 파이프라인 검증
  - Worker E2E: 스케줄러 시작/종료 및 작업 등록 검증
  - 성능 테스트: 대량 데이터 처리 및 동시 요청 성능 검증
- **API 전체 플로우 E2E**: 기존 테스트 실행 및 검증 완료
- **테스트 결과**: 모든 E2E 테스트 결과 JSON 파일 저장 (`backend/tests/results/`)

### 참고 파일

- **통합 테스트**: `backend/tests/integration/` (3개 파일)
- **E2E 테스트**: `backend/tests/e2e/` (3개 파일 추가)
- **테스트 결과**: `backend/tests/results/` (E2E 테스트 결과 JSON 파일)

---

## Phase 4: 프로덕션 준비 ✅ (완료)

**목표**: 프로덕션 배포를 위한 문서화, 환경 설정, 모니터링 구성을 완료하여 Phase 5 배포를 준비합니다.

### 완료 요약

**상태**: Phase 4.1 ~ Phase 4.3 전체 완료 ✅  
**완료일**: 2025-11-20  
**프로젝트 진행률**: 프로덕션 준비 100% 완료

**현재 상태**:
- ✅ Health check 엔드포인트 존재 및 개선 (`/health`)
- ✅ 로깅 설정 완료 (개발/프로덕션 분리, JSON 형식 지원)
- ✅ Worker 스크립트 존재 (`backend/scripts/worker.py`)
- ✅ 프로덕션 환경변수 가이드 작성 완료
- ✅ 데이터베이스 마이그레이션 가이드 작성 완료
- ✅ 사용자/개발자 가이드 작성 완료
- ✅ 환경변수 예시 파일 존재 (`backend/.env.example`)

### 4.1 초기 데이터 설정 스크립트 정리

#### 4.1.1 초기 데이터 설정 가이드 문서화 ✅
- [x] **파일**: `docs/SETUP.md` 생성
- [x] **내용**:
  - 프로젝트 초기 설정 가이드
  - 환경변수 설정 방법
  - 데이터베이스 마이그레이션 실행 방법
  - 초기 RSS 소스 등록 방법 (`backend/scripts/init_sources.py` 사용)
  - 개발 환경 실행 방법
- [x] **포함 항목**:
  - Poetry 설치 및 의존성 설치
  - `.env` 파일 설정
  - Supabase 연결 설정
  - Alembic 마이그레이션 실행
  - 초기 소스 등록

**완료된 항목**:
- [x] `backend/app/core/constants.py` 생성 완료 확인
- [x] `backend/scripts/init_sources.py` 리팩토링 완료 확인
- [x] 테스트 파일 리팩토링 완료 확인

### 4.2 환경 설정 및 문서화

#### 4.2.1 프로덕션 환경변수 설정 가이드 ✅
- [x] **파일**: `docs/DEPLOYMENT.md` 생성
- [x] **내용**:
  - 프로덕션 환경변수 목록 및 설명
  - 각 환경변수의 역할과 설정 방법
  - 보안 고려사항 (API 키 관리)
  - 환경별 설정 예시 (개발/스테이징/프로덕션)
- [x] **환경변수 목록**:
  - `DATABASE_URL`: Supabase PostgreSQL 연결 문자열
  - `OPENAI_API_KEY`: OpenAI API 키
  - `CORS_ORIGINS`: 프론트엔드 도메인 (쉼표 구분)
  - `RSS_COLLECTION_INTERVAL_MINUTES`: RSS 수집 주기 (기본: 20)
  - `DEBUG`: 디버그 모드 (프로덕션: false)
  - `REF_DATE`: 그룹화 기준 날짜 (선택사항)

#### 4.2.2 환경변수 예시 파일 생성 ✅
- [x] **파일**: `backend/.env.example` 생성 (이미 존재)
- [x] **내용**: 모든 환경변수 목록 및 예시 값 (실제 값 제외)

#### 4.2.3 데이터베이스 마이그레이션 가이드 ✅
- [x] **파일**: `docs/DEPLOYMENT.md`에 섹션 추가
- [x] **내용**:
  - Alembic 마이그레이션 실행 방법
  - 프로덕션 DB에 마이그레이션 적용
  - 마이그레이션 롤백 방법
  - 백업 전략 (Supabase 자동 백업 활용)

#### 4.2.4 API 문서 정리 ✅
- [x] **작업**: FastAPI 자동 생성 문서 확인 및 보완
- [x] **내용**:
  - `/docs` 엔드포인트 확인
  - API 엔드포인트 설명 보완 (필요 시)
  - 예시 요청/응답 확인
  - 에러 응답 문서화

#### 4.2.5 사용자 가이드 작성 ✅
- [x] **파일**: `docs/USER_GUIDE.md` 생성
- [x] **내용**:
  - 서비스 개요 및 주요 기능
  - 분야별 아이템 조회 방법
  - 사건 타임라인 보기
  - 인물 페이지 사용법
  - 북마크 기능 사용법
  - 설정 페이지 사용법 (소스 관리, 워치 규칙)

#### 4.2.6 개발자 가이드 작성 ✅
- [x] **파일**: `docs/DEVELOPER_GUIDE.md` 생성
- [x] **내용**:
  - 프로젝트 구조 설명
  - 개발 환경 설정
  - 코드 스타일 및 컨벤션
  - 테스트 실행 방법
  - API 개발 가이드
  - 데이터베이스 스키마 설명
  - 배포 프로세스

### 4.3 성능 최적화 및 모니터링 설정

#### 4.3.1 로깅 설정 개선 ✅
- [x] **파일**: `backend/app/core/logging.py` 생성
- [x] **내용**:
  - 개발 환경: 콘솔 출력 (기존 형식 유지)
  - 프로덕션 환경: 구조화된 로그 (JSON 형식)
  - 로그 레벨 설정 (DEBUG/INFO/WARNING/ERROR)
  - 로그 로테이션 설정 (선택사항)
- [x] **구현**:
  - 환경변수 `DEBUG` 또는 `LOG_FORMAT`으로 형식 선택
  - JSON 로그 포맷터 구현
  - `backend/app/main.py`에서 로깅 설정 적용

#### 4.3.2 Health Check 엔드포인트 개선 ✅
- [x] **파일**: `backend/app/main.py` 수정
- [x] **내용**:
  - `/health` 엔드포인트 개선 (이미 존재, 보완)
  - 스케줄러 상태 확인 (이미 구현됨)
  - 데이터베이스 연결 상태 확인 추가
  - 상세 상태 정보 반환 (선택사항)

#### 4.3.3 배포 전 검증 (프로덕션 빌드 테스트) ✅
- [x] **목적**: 배포 전 로컬에서 프로덕션 빌드를 테스트하여 타입 오류 및 빌드 문제를 사전에 발견
- [x] **배경**: 
  - `next dev` (개발 모드)는 타입 오류를 경고로만 표시하고 빌드를 계속 진행할 수 있음
  - `next build` (프로덕션 빌드)는 타입 오류가 있으면 빌드 실패
  - Vercel은 `next build`를 실행하므로, 로컬에서 빌드 테스트를 하지 않으면 배포 시 오류 발견
  - `.gitignore` 패턴이 의도치 않게 중요한 파일을 무시할 수 있음 (예: `lib/` 패턴이 `frontend/lib/`도 무시)
  - 로컬에서는 파일이 존재하지만 Git에 커밋되지 않으면 배포 환경에 파일이 없어 빌드 실패
- [x] **검증 항목**:
  - [x] `.gitignore` 확인:
    ```bash
    # Git에 추적되는 파일 확인
    git ls-files frontend/lib/
    git ls-files backend/
    
    # .gitignore에 의해 무시되는 파일 확인
    git check-ignore -v frontend/lib/*.ts
    git check-ignore -v backend/**/*.py
    ```
    - **목적**: `.gitignore` 패턴이 의도치 않게 중요한 파일을 무시하는지 확인
    - **배경**: 
      - 로컬에서는 파일이 존재하지만 Git에 커밋되지 않으면 배포 시 누락됨
      - 예: `lib/` 패턴이 `frontend/lib/`도 무시하는 경우
      - Vercel/Railway는 Git 저장소를 클론하므로, Git에 없는 파일은 배포 환경에 존재하지 않음
    - **확인 사항**:
      - 필수 파일이 Git에 포함되어 있는지 확인
      - `.gitignore` 패턴이 의도치 않은 파일을 무시하지 않는지 확인
      - 특히 하위 디렉토리(`frontend/`, `backend/`)의 파일 확인
  - [x] 프론트엔드 프로덕션 빌드 테스트:
    ```bash
    cd frontend
    npm run build
    ```
    - TypeScript 타입 오류 확인
    - 빌드 성공 여부 확인
    - 빌드 산출물 확인 (`.next` 디렉토리)
  - [x] 백엔드 프로덕션 빌드 테스트 (Docker):
    ```bash
    docker build -t ai-trend-backend .
    docker run -p 8000:8000 ai-trend-backend
    ```
    - Docker 이미지 빌드 성공 확인
    - 컨테이너 실행 확인
    - Health check 확인 (`/health` 엔드포인트)
- [x] **체크리스트**:
  - [x] `.gitignore` 확인 완료 (필수 파일이 Git에 포함되어 있는지 확인)
  - [x] 프론트엔드 빌드 성공 확인
  - [x] 백엔드 Docker 빌드 성공 확인
  - [x] 타입 오류 없음 확인
  - [x] 빌드 산출물 정상 생성 확인
- [x] **권장 사항**:
  - 배포 전 반드시 `.gitignore` 확인 수행 (필수 파일이 Git에 포함되어 있는지)
  - 배포 전 반드시 로컬에서 프로덕션 빌드 테스트 수행
  - CI/CD 파이프라인에 빌드 테스트 단계 추가 (선택사항)
  - 타입 오류는 개발 중에도 주의 깊게 확인
  - `.gitignore` 패턴 수정 시 하위 디렉토리 영향 확인 (예: `lib/` → `/lib/`)

#### 4.3.4 에러 추적 (선택사항)
- [ ] **작업**: Sentry 또는 유사 서비스 연동 검토
- [ ] **우선순위**: 낮음 (MVP에서는 선택사항)
- [ ] **내용**:
  - Sentry SDK 설치 및 설정
  - 에러 자동 수집 및 알림
  - 프로덕션 환경에서만 활성화

#### 4.3.5 메트릭 수집 (선택사항)
- [ ] **작업**: 기본 메트릭 수집 구현 검토
- [ ] **우선순위**: 낮음 (MVP에서는 선택사항)
- [ ] **내용**:
  - 수집된 아이템 수 추적
  - API 응답 시간 측정
  - 에러율 추적
  - 간단한 엔드포인트로 메트릭 노출 (예: `/metrics`)

### 문서 파일 구조

```
docs/
├── SETUP.md              # 초기 설정 가이드
├── DEPLOYMENT.md         # 배포 가이드 (환경변수, 마이그레이션)
├── USER_GUIDE.md         # 사용자 가이드
└── DEVELOPER_GUIDE.md    # 개발자 가이드

backend/
├── .env.example          # 환경변수 예시 파일
└── app/core/
    └── logging.py        # 로깅 설정 모듈
```

### 완료 조건

- [x] 초기 데이터 설정 가이드 문서화 완료
- [x] 프로덕션 환경변수 설정 가이드 작성 완료
- [x] 환경변수 예시 파일 생성 완료 (이미 존재)
- [x] 데이터베이스 마이그레이션 가이드 작성 완료
- [x] API 문서 확인 및 보완 완료
- [x] 사용자 가이드 작성 완료
- [x] 개발자 가이드 작성 완료
- [x] 로깅 설정 개선 완료 (개발/프로덕션 분리)
- [x] Health check 엔드포인트 개선 완료
- [x] 배포 전 검증 (프로덕션 빌드 테스트) 완료
- [x] Phase 4 완료 처리 (TODOs.md 업데이트)

### 주요 결과

- **문서화**: 4개 문서 파일 작성 완료
  - 초기 설정 가이드 (`docs/SETUP.md`)
  - 배포 가이드 (`docs/DEPLOYMENT.md`)
  - 사용자 가이드 (`docs/USER_GUIDE.md`)
  - 개발자 가이드 (`docs/DEVELOPER_GUIDE.md`)
- **로깅 설정**: 개발/프로덕션 환경 분리 완료
  - 개발: 콘솔 출력 (가독성)
  - 프로덕션: JSON 형식 (로그 수집 서비스 연동)
- **Health Check**: 데이터베이스 연결 상태 확인 추가
- **환경변수**: 예시 파일 존재 확인 (`backend/.env.example`)
- **배포 전 검증**: 프로덕션 빌드 테스트 프로세스 수립
  - `.gitignore` 확인: 필수 파일이 Git에 포함되어 있는지 확인
  - 프론트엔드: `npm run build` 로컬 테스트
  - 백엔드: Docker 빌드 및 실행 테스트
  - 타입 오류 사전 발견 프로세스 확립

### 참고 파일

- **문서**: `docs/` 디렉토리 (4개 파일)
- **로깅 설정**: `backend/app/core/logging.py`
- **환경변수 예시**: `backend/.env.example`

### 우선순위

**높음 (MVP 필수)**:
- 초기 데이터 설정 가이드
- 프로덕션 환경변수 설정 가이드
- 환경변수 예시 파일
- 데이터베이스 마이그레이션 가이드
- 로깅 설정 개선
- 배포 전 검증 (프로덕션 빌드 테스트)

**중간 (권장)**:
- 사용자 가이드
- 개발자 가이드
- Health check 개선

**낮음 (선택사항)**:
- 에러 추적 (Sentry)
- 메트릭 수집

---

## Phase 5: 배포

**목표**: MVP 배포를 완료하여 프로덕션 환경에서 서비스를 운영합니다.

**배포 플랫폼 선택**: Railway (백엔드 API + 스케줄러 워커)

### 5.1 배포 아키텍처

**배포 전략**:
- **프론트엔드**: Vercel에 배포 (Next.js 최적화)
- **백엔드 API**: Railway에 배포 (FastAPI)
- **스케줄러 워커**: Railway에 별도 서비스로 배포 (APScheduler)

**권장 아키텍처**:
```
┌─────────────────┐
│  Vercel (Next.js) │  ← 프론트엔드
└────────┬────────┘
         │ API 호출
┌────────▼────────┐
│ Backend API      │  ← Railway (FastAPI)
│ (FastAPI)        │
└────────┬────────┘
         │
┌────────▼────────┐
│ Supabase (DB)   │
└─────────────────┘
         │
┌────────▼────────┐
│ Worker Process  │  ← Railway (스케줄러)
│ (APScheduler)   │
└─────────────────┘
```

**Railway 선택 이유**:
- 간단한 설정 (GitHub 연동, 자동 배포)
- Docker 지원 (Dockerfile 또는 Nixpacks 자동 감지)
- 무료 플랜: $5 크레딧/월 (소규모 프로젝트에 충분)
- 환경변수 관리 용이
- 로그 확인 쉬움
- 여러 서비스(API + Worker) 동시 배포 가능

### 5.2 프론트엔드 배포 (Vercel)

#### 5.2.1 Vercel 프로젝트 설정
- [x] Vercel 계정 생성 및 GitHub 연동
- [x] 새 프로젝트 생성
- [x] GitHub 저장소 연결
- [x] 프로젝트 루트 설정: `frontend/` 디렉토리 (Vercel UI에서 설정)

#### 5.2.2 빌드 설정
- [x] `frontend/vercel.json` 생성 시도 (후 삭제 - Vercel이 지원하지 않음)
- [x] 빌드 명령 확인: `next build --webpack` (webpack 명시적 사용)
- [x] 출력 디렉토리 설정: `.next` (기본값)
- [x] 프레임워크 프리셋: Next.js (자동 감지)
- [x] `frontend/next.config.ts` webpack 설정 추가 (경로 별칭 해석)
- [x] `frontend/tsconfig.json` baseUrl 설정 추가

#### 5.2.3 환경변수 설정
- [ ] **현재 상태**: Vercel 대시보드에서 환경변수 설정 필요
  - [ ] `NEXT_PUBLIC_API_URL`: 백엔드 API URL (Railway URL 확인 후 설정 필요)
    - **현재 문제**: 이 환경변수가 설정되지 않아 API 호출 시 404 오류 발생
    - **설정 방법**: Vercel 프로젝트 → Settings → Environment Variables → Add
    - **값 형식**: `https://your-api.railway.app` (Railway 백엔드 URL)
    - **주의**: `http://` 또는 `https://` 포함하여 전체 URL 입력
  - 기타 프론트엔드 환경변수 (필요 시)

#### 5.2.4 배포 문제 해결
- [x] **문제 1 발견**: `Module not found: Can't resolve '@/lib/constants'` 오류
- [x] **문제 1 원인 분석**: 
  - `.gitignore`의 `lib/` 패턴이 `frontend/lib/`도 무시함
  - `constants.ts`, `validators.ts`, `providers.tsx` 파일이 Git에 커밋되지 않음
  - Vercel 빌드 시 `lib` 디렉토리에 `api.ts`만 존재
- [x] **문제 1 해결 조치**:
  - `.gitignore` 수정: `lib/` → `/lib/` (프로젝트 루트만 무시)
  - `frontend/next.config.ts`에 디버깅 로그 추가 (파일 존재 여부 확인)
  - webpack resolve 설정 강화 (extensions 명시적 설정)
- [x] **문제 1 해결 완료**: 파일 Git 추가 및 푸시 완료 (`f9eed75`)
- [x] **문제 2 발견**: TypeScript 타입 오류
  - **오류 위치**: `./components/SourcesSection.tsx:169:51`
  - **오류 내용**: `Argument of type 'SourceCreate | SourceUpdate' is not assignable to parameter of type 'SourceCreate'`
  - **상세**: `SourceUpdate`의 `title`이 `string | null | undefined`인데, `SourceCreate`는 `string`을 요구
- [x] **문제 2 해결 완료**:
  - **원인**: `SourceModal`의 `onSave`가 `SourceCreate | SourceUpdate`를 받지만, `createMutation.mutate`는 `SourceCreate`만 받음
  - **해결 조치**:
    - 타입 가드 함수 `isSourceCreate()` 추가 (런타임 검증)
    - 디버깅 로그 추가 (타입 검증 과정 추적)
    - 폴백 로직 추가 (SourceUpdate → SourceCreate 변환 시도)
  - **구현 내용**:
    - `isSourceCreate()`: `title`과 `feed_url`이 필수 문자열인지 확인
    - `onSave` 콜백에서 타입 가드 사용 및 상세 로그 출력
    - 타입 불일치 시 에러 로그 및 폴백 처리

#### 5.2.5 배포 및 검증
- [x] 파일 Git 추가 및 커밋 완료
- [x] 자동 배포 확인 (GitHub push 시 자동 배포)
- [x] 빌드 성공 확인 (TypeScript 타입 오류 해결 완료)
- [x] Vercel 배포 성공 확인
- [x] CORS 설정 완료 (백엔드 Railway URL을 CORS_ORIGINS에 추가)
- [ ] **현재 작업**: 프론트엔드에서 API 호출 시 404 오류 해결
  - **오류 메시지**: "Request failed with status code 404"
  - **발생 위치**: 아이템 목록 조회 시 (`/api/items`)
  - **가능한 원인**:
    1. `NEXT_PUBLIC_API_URL` 환경변수가 Vercel에 설정되지 않았거나 잘못된 값
    2. 백엔드 API 경로가 잘못되었을 수 있음 (예: `/api/items` vs `/items`)
    3. Railway 백엔드 URL이 변경되었을 수 있음
  - **해결 단계**:
    - [x] Git 변경사항 커밋 완료 (수정된 파일, 이상한 파일명 파일들 정리)
    - [x] Railway 백엔드 URL 확인: `https://ai-trends-production.up.railway.app`
    - [x] Vercel 환경변수 설정 확인: `NEXT_PUBLIC_API_URL` = `https://ai-trends-production.up.railway.app`
    - [ ] Vercel 재배포 확인 (환경변수 변경 후 재배포 필요)
    - [ ] 브라우저 개발자 도구에서 실제 API 호출 URL 확인
    - [ ] Railway 백엔드 API 직접 테스트 (`/health`, `/api/items`)
    - [ ] 프론트엔드에서 API 호출 성공 확인
- [ ] 도메인 설정 (선택사항)
- [ ] 프론트엔드-백엔드 연동 테스트 (404 오류 해결 후)

### 5.3 백엔드 API 배포 (Railway)

#### 5.3.1 Railway 프로젝트 설정
- [x] Railway 계정 생성 (https://railway.app)
- [x] GitHub 연동
- [x] 새 프로젝트 생성
- [x] GitHub 저장소 연결

#### 5.3.2 Dockerfile 생성 및 수정
- [x] **파일**: `Dockerfile` 생성 (프로젝트 루트)
- [x] **초기 문제 및 해결**:
  - [x] **문제 1**: `alembic/` 디렉토리 경로 오류
    - **원인**: `alembic/`가 `backend/` 안에 있는데 루트에서 복사 시도
    - **해결**: `COPY backend/ ./backend/`로 통합 (alembic 포함)
  - [x] **문제 2**: `uvicorn` 명령어를 찾을 수 없음
    - **원인**: Poetry 가상환경 경로가 PATH에 없음
    - **해결**: `ENV PATH="/app/.venv/bin:$PATH"` 추가 및 절대 경로 사용 (`/app/.venv/bin/uvicorn`)
  - [x] **문제 3**: Poetry 가상환경 생성 확인
    - **해결**: `poetry config virtualenvs.in-project true` 및 설치 검증 추가
- [x] **최종 Dockerfile 구조**:
  - Python 3.11 베이스 이미지
  - Poetry 1.8.5 설치
  - 의존성 설치 (`poetry install --no-dev`)
  - 애플리케이션 복사 (`COPY backend/ ./backend/`)
  - 포트 노출 (8000)
  - 실행 명령: `/app/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`

#### 5.3.3 Railway 서비스 생성
- [x] 프로젝트에 새 서비스 추가 (API 서버)
- [x] GitHub 저장소 연결
- [x] 빌드 설정 확인 (Dockerfile 자동 감지)
- [x] 시작 명령 확인

#### 5.3.4 환경변수 설정 및 문제 해결
- [x] Railway 대시보드에서 환경변수 설정:
  - [x] `DATABASE_URL`: Supabase PostgreSQL 연결 문자열
    - **형식**: `postgresql+psycopg2://user:password@host:port/db?sslmode=require`
    - **주의**: `postgresql://` → `postgresql+psycopg2://` (드라이버 명시)
    - **주의**: `?sslmode=require` 추가 (Supabase 필수)
  - [x] `OPENAI_API_KEY`: OpenAI API 키
  - [x] `CORS_ORIGINS`: 프론트엔드 도메인 (쉼표 구분)
  - [x] `DEBUG`: `false`
  - [x] `RSS_COLLECTION_INTERVAL_MINUTES`: `20`
  - [x] `REF_DATE`: (선택사항, 비워두면 오늘 UTC 자정)
  - [x] `PORT`: Railway가 자동 설정 (변경 불필요)
- [x] **DATABASE_URL 파싱 오류 해결**:
  - [x] **문제**: `DATABASE_URL` 값에 `DATABASE_URL=` 접두사 포함
    - **원인**: Railway 환경변수 설정 시 값에 변수명이 포함됨
    - **해결**: `backend/app/core/config.py`에 validator 추가하여 접두사 자동 제거
  - [x] **디버깅 로그 추가**: `backend/app/core/database.py`에 DATABASE_URL 마스킹 로그 추가

#### 5.3.5 배포 및 검증
- [x] 서비스 배포 (자동 배포)
- [x] Health check 확인: `https://your-api.railway.app/health`
  - **결과**: `{ status: "healthy", scheduler_running: true, database_connected: true }`
- [x] API 엔드포인트 테스트: `https://your-api.railway.app/api/items`
- [x] 로그 확인 (Railway 대시보드)
- [ ] CORS 설정 확인 (프론트엔드 배포 후 테스트)

### 5.4 스케줄러 워커 배포 (Railway)

#### 5.4.1 Worker 서비스 생성
- [ ] Railway 프로젝트에 새 서비스 추가 (Worker)
  - Railway 대시보드 → "New" 클릭
  - "GitHub Repo" 선택
  - 동일한 저장소 선택 (현재 저장소)
  - 서비스 이름: `worker` (또는 `scheduler-worker`)
- [ ] GitHub 저장소 연결 (동일 저장소)
- [ ] 빌드 설정 확인 (동일 Dockerfile 사용)
- [ ] 시작 명령 설정 (Railway 대시보드 → Settings → Deploy):
  ```
  poetry run python -m backend.scripts.worker
  ```

#### 5.4.2 Worker 환경변수 설정
- [ ] Railway 대시보드에서 환경변수 설정 (Worker 서비스 → Variables):
  - `DATABASE_URL`: Supabase PostgreSQL 연결 문자열 (API 서버와 동일)
  - `OPENAI_API_KEY`: OpenAI API 키 (API 서버와 동일)
  - `DEBUG`: `false`
  - `RSS_COLLECTION_INTERVAL_MINUTES`: `20`
  - **참고**: Worker는 `CORS_ORIGINS`와 `PORT` 불필요

#### 5.4.3 배포 및 검증
- [ ] Worker 서비스 배포 (자동 또는 수동)
- [ ] 배포 로그 확인 (Railway 대시보드 → Worker → Logs)
- [ ] 스케줄러 시작 확인:
  ```
  [Worker] Starting scheduler worker...
  [Worker] Scheduler started successfully
  ```
- [ ] RSS 수집 작업 실행 확인 (20분 간격)
- [ ] 증분 그룹화 작업 실행 확인 (20분 간격)
- [ ] 로그 확인 (Railway 대시보드)

### 5.5 데이터베이스 마이그레이션

#### 5.5.1 프로덕션 DB 마이그레이션
- [ ] Supabase 프로젝트 확인
- [ ] 프로덕션 `DATABASE_URL` 확인
- [ ] 로컬에서 마이그레이션 실행:
  ```bash
  $env:DATABASE_URL = "postgresql+psycopg2://..."
  poetry run alembic upgrade head
  ```
- [ ] 테이블 생성 확인 (Supabase 대시보드)

#### 5.5.2 초기 데이터 설정
- [ ] RSS 소스 등록:
  ```bash
  $env:DATABASE_URL = "postgresql+psycopg2://..."
  poetry run python -m backend.scripts.init_sources
  ```
- [ ] 초기 인물 및 워치 규칙 설정 (선택사항)

### 5.6 배포 후 검증

#### 5.6.1 전체 시스템 테스트
- [ ] 프론트엔드-백엔드 연동 확인
  - 프론트엔드에서 API 호출 성공 확인
  - CORS 설정 확인
- [ ] API 엔드포인트 테스트
  - `/api/items` 조회 확인
  - `/api/sources` 조회 확인
  - `/api/persons` 조회 확인
  - `/health` 엔드포인트 확인
- [ ] RSS 수집 동작 확인
  - Worker 로그에서 수집 작업 실행 확인
  - DB에 새 아이템 추가 확인
- [ ] 스케줄러 동작 확인
  - Worker 로그에서 스케줄러 시작 확인
  - 정기 작업 실행 확인

#### 5.6.2 모니터링 설정
- [ ] 로그 확인 방법 문서화
  - Railway 대시보드에서 로그 확인 방법
  - API 서버 로그 확인
  - Worker 로그 확인
- [ ] Health check 모니터링
  - `/health` 엔드포인트 정기 확인
  - 데이터베이스 연결 상태 확인
  - 스케줄러 상태 확인
- [ ] 에러 알림 설정 (선택사항)
  - Railway 알림 설정
  - 또는 외부 모니터링 서비스 연동

### 배포 파일 구조

```
ai-trend/
├── Dockerfile                    # Docker 이미지 빌드 (Railway용)
├── frontend/
│   └── vercel.json              # Vercel 설정
└── backend/
    └── scripts/
        └── worker.py            # Worker 스크립트 (이미 존재)
```

### 배포 순서

1. **데이터베이스 마이그레이션**: 프로덕션 DB에 스키마 적용
2. **초기 데이터 설정**: RSS 소스 등록
3. **백엔드 API 배포**: Railway에 FastAPI 서버 배포
4. **스케줄러 워커 배포**: Railway에 Worker 프로세스 배포
5. **프론트엔드 배포**: Vercel에 Next.js 앱 배포
6. **전체 시스템 검증**: 모든 구성 요소 동작 확인

### 비용 예상

**Railway**:
- 무료: $5 크레딧/월 (소규모 프로젝트에 충분)
- 유료: $5/월 + 사용량 (필요 시)

**Vercel**:
- 무료: Hobby 플랜 (프론트엔드)
- 유료: Pro $20/월 (필요 시)

**Supabase**:
- 무료: PostgreSQL 데이터베이스 (제한적)
- 유료: Pro $25/월 (필요 시)

### 완료 조건

- [ ] 프론트엔드 Vercel 배포 완료
- [ ] 백엔드 API Railway 배포 완료
- [ ] 스케줄러 워커 Railway 배포 완료
- [ ] 데이터베이스 마이그레이션 적용 완료
- [ ] 초기 데이터 설정 완료
- [ ] 전체 시스템 검증 완료
- [ ] 배포 문서화 완료
- [ ] Phase 5 완료 처리 (TODOs.md 업데이트)

### 참고: 다른 배포 옵션

#### Render (대안)
- 무료 플랜 제공 (제한적, Cold start 있음)
- Background Workers 지원
- 배포 방법: `render.yaml` 설정 파일 사용

#### Fly.io (대안)
- 무료 플랜 제공 (3개 VM, 3GB 스토리지)
- 글로벌 배포
- 배포 방법: `fly.toml` 설정 파일 사용

#### Vercel Serverless Functions (비권장)
- 제약사항: 최대 실행 시간 10초(Hobby)/60초(Pro)
- APScheduler는 stateless 환경에서 작동하지 않음
- 스케줄러는 별도 서버 필요


---

## Phase 6: 고급 기능 (배포 후 진행)

> **중요**: Phase 6은 MVP 배포(Phase 5) 완료 후 진행합니다.  
> 고급 기능은 프로덕션 환경에서 안정화된 후 점진적으로 추가합니다.

### 6.1 고급 요약 서비스 (원문 기반 AI 요약)
- [ ] `backend/app/services/summarizer.py` 확장:
  - [ ] 원문 일시 로드 함수 (httpx)
  - [ ] OpenAI API로 1-2문장 요약 생성 함수
  - [ ] 본문 폐기 후 요약만 반환
  - [ ] RSS description 부족 시 원문 로드 → AI 요약 자동 수행
- [ ] **단위 테스트**: 원문 로드 함수 테스트 (mock httpx)
- [ ] **통합 테스트**: OpenAI API 호출 테스트 (실제 API 또는 mock)
- [ ] **E2E 테스트**: 원문 기반 요약 생성 → DB 저장 확인

### 6.2 OPML Import/Export
- [ ] `backend/app/services/opml_handler.py` 생성:
  - [ ] OPML 파싱 함수 (feedparser 또는 opml 라이브러리)
  - [ ] 소스 일괄 추가 함수
  - [ ] OPML 생성 함수
- [ ] `backend/app/api/opml.py` 생성:
  - [ ] `POST /api/opml/import` - OPML 파일 업로드 및 소스 추가
  - [ ] `GET /api/opml/export` - 현재 소스 목록을 OPML로 내보내기
- [ ] 프론트엔드 OPML Import/Export UI 연동

### 6.3 주간 인사이트
- [ ] `backend/app/services/insights.py` 생성:
  - [ ] 분야별 키워드 증감 분석 함수
  - [ ] 인물별 핵심 이슈 요약 함수
  - [ ] 주간 리포트 생성 함수
- [ ] `backend/app/api/insights.py` 확장:
  - [ ] `GET /api/insights/weekly` - 주간 인사이트 상세
  - [ ] `GET /api/insights/keywords` - 키워드 트렌드
  - [ ] `GET /api/insights/persons` - 인물별 요약
- [ ] `frontend/app/insights/page.tsx` 생성 (인사이트 시각화)

### 6.4 알림 (선택사항)
- [ ] `backend/app/services/notifier.py` 생성:
  - [ ] 이메일 알림 함수 (SMTP)
  - [ ] 웹푸시 알림 함수
- [ ] `backend/app/models/subscription.py` 생성 (구독 설정)
- [ ] Celery 작업 큐 설정 (비동기 알림 처리)
- [ ] `backend/app/api/subscriptions.py` 생성
- [ ] 프론트엔드 알림 설정 UI

### 6.5 고급 중복/사건 묶음 (임베딩/LSH 기반)
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

### 6.6 소스 재활성화(DeepMind)
- [ ] DeepMind 수집 재개(Phase 6)
  - [ ] The Keyword 전체 피드(`https://blog.google/feed/`) 구독
  - [ ] 카테고리 메타 기반 필터("Google DeepMind") + 백업 키워드(`deepmind`, `/technology/google-deepmind/`)
  - [ ] 초기 E2E: 수집 → 요약 → 분류 → 그룹핑 → `/api/groups` 노출 검증(결과 JSON 저장)

---

## 진행 상황 추적

**마지막 업데이트**: 2025-11-21 (Phase 1 완료 ✅, Phase 2 완료 ✅, Phase 3 완료 ✅, Phase 4 완료 ✅, Phase 5 진행 중 🔄)

**프로젝트 진행률**: 
- 백엔드 기반 구조 100% 완료 ✅
- 프론트엔드 UI 100% 완료 ✅
- 통합 테스트 및 E2E 검증 100% 완료 ✅
- 프로덕션 준비 100% 완료 ✅
- 배포 진행 중 🔄
  - 백엔드 API (Railway): 배포 완료 ✅
    - ✅ Health check 통과 (`/health` 엔드포인트 정상)
    - ✅ CORS 설정 완료 (프론트엔드 URL 추가)
  - 프론트엔드 (Vercel): 배포 완료 ✅
    - ✅ Module not found 오류 해결 (파일 Git 추가 완료)
    - ✅ TypeScript 타입 오류 해결 완료 (`SourcesSection.tsx`, `WatchRulesSection.tsx`)
    - ✅ 빌드 성공 및 Vercel 배포 완료
    - ⚠️ **현재 문제**: API 호출 시 404 오류 발생
      - 오류: "Request failed with status code 404" (`/api/items` 호출 시)
      - 가능한 원인: `NEXT_PUBLIC_API_URL` 환경변수 미설정 또는 잘못된 값
      - 다음 단계: Vercel 환경변수 확인 및 Railway 백엔드 URL 설정

**현재 단계**: Phase 5 (배포) 진행 중 🔄

**Phase 구조** (MVP 우선 전략):
- **Phase 1**: 백엔드 기반 구조 ✅ (완료)
- **Phase 2**: 프론트엔드 UI ✅ (완료)
- **Phase 3**: 통합 테스트 및 E2E 검증 ✅ (완료)
- **Phase 4**: 프로덕션 준비 ✅ (완료)
- **Phase 5**: 배포 (MVP) 🔄 (진행 중)
  - 5.3 백엔드 API 배포: 완료 ✅
  - 5.2 프론트엔드 배포: 거의 완료 (API 연동 404 오류 해결 진행 중)
    - ✅ 파일 Git 추가 완료
    - ✅ TypeScript 타입 오류 해결 완료
    - ✅ Vercel 배포 성공
    - 🔄 API 연동 404 오류 해결 진행 중
      - Git 커밋 완료 필요
      - Railway 백엔드 URL 확인 필요
      - Vercel 환경변수 설정 필요
  - 5.4 스케줄러 워커 배포: 진행 중
    - Worker 서비스 생성 필요
    - 환경변수 설정 필요
    - 배포 및 검증 필요
  - 5.5 데이터베이스 마이그레이션: 대기 중
  - 5.6 배포 후 검증: 대기 중
- **Phase 6**: 고급 기능 (배포 후 진행)

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

상세 내용은 `v1_TODOs.md` 및 `.cursor/rules/testing-strategy.mdc`를 참고하세요.

---

## API Contract 동기화 (중요 - 필수 준수)

### 원칙: 단일 진실 공급원 (Single Source of Truth)
백엔드가 상수와 스키마의 진실 공급원이며, 프론트엔드는 이를 정확히 반영해야 함.

### 필수 체크리스트

#### 백엔드 Constants API 구현 (Phase 2.1)
- [x] `backend/app/api/constants.py` 생성
- [x] `GET /api/constants/fields`: FIELDS 목록 반환
- [x] `GET /api/constants/custom-tags`: CUSTOM_TAGS 목록 반환
- [x] `backend/app/main.py`에 라우터 등록

#### 프론트엔드 상수 정의 전략
- [x] **옵션 B**: 정적 상수 정의 (백엔드와 수동 동기화)
- [x] `frontend/lib/constants.ts`에 상수 정의
- [x] 타입 정의: `type Field = typeof FIELDS[number]`, `type CustomTag = typeof CUSTOM_TAGS[number]`

#### 타입 정의 동기화
- [x] 필드명 일치 (camelCase vs snake_case 주의 - 백엔드는 snake_case)
- [x] 타입 일치 (string, number, boolean, Date → string)
- [x] Optional 필드 일치
- [x] 배열 타입 일치 (List[str] → string[])

#### API 클라이언트 쿼리 파라미터 동기화
- [x] 백엔드는 snake_case 사용, 프론트엔드도 동일하게 사용
- [x] `date_from`, `date_to`, `page_size`, `order_by`, `order_desc` 등
- [x] axios가 자동으로 snake_case 유지

#### 런타임 검증 함수
- [x] `frontend/lib/validators.ts` 생성
- [x] `validateField()`: 분야 값 검증
- [x] `validateCustomTag()`: 커스텀 태그 값 검증
- [x] URL 파라미터 검증에 사용

#### Common Pitfalls 방지
- [x] 하드코딩된 문자열 사용 금지 (상수 파일 사용)
- [x] camelCase vs snake_case 혼용 금지
- [x] 태그 값 대소문자 일치 확인 (예: "agents" vs "Agents")
- [x] Query 파라미터 이름 일치 확인
- [x] Enum 값 문자열 일치 확인

### 동기화 검증 방법
- **타입 체크**: TypeScript 컴파일 시 타입 불일치 감지
- **런타임 검증**: API 호출 시 백엔드 에러 응답으로 검증
- **수동 검증**: 백엔드 스키마 파일과 프론트엔드 타입 파일 비교

**참고 규칙**: `.cursor/rules/api-contract-sync.mdc` 상세 내용 확인
