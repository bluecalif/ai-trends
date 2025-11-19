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

**마지막 업데이트**: 2025-11-19 (Phase 1 완료 ✅, Phase 2 시작 준비)

**프로젝트 진행률**: 백엔드 기반 구조 100% 완료, 프론트엔드 0%

**현재 단계**: Phase 2 (프론트엔드) 시작

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
