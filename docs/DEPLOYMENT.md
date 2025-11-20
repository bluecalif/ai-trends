# AI Trend Monitor - 배포 가이드

이 문서는 AI Trend Monitor를 프로덕션 환경에 배포하는 방법을 설명합니다.

## 목차

1. [빠른 시작](#빠른-시작)
2. [프로덕션 환경변수 설정](#프로덕션-환경변수-설정)
3. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
4. [배포 아키텍처](#배포-아키텍처)
5. [Railway 배포 (백엔드)](#railway-배포-백엔드)
6. [Vercel 배포 (프론트엔드)](#vercel-배포-프론트엔드)
7. [보안 고려사항](#보안-고려사항)

---

## 빠른 시작

### 배포 순서

1. **백엔드 API 배포** (Railway)
   - Railway 프로젝트 생성
   - API 서비스 배포
   - Worker 서비스 배포
   - 환경변수 설정
   - 도메인 확인

2. **프론트엔드 배포** (Vercel)
   - Vercel 프로젝트 생성
   - 환경변수 설정 (`NEXT_PUBLIC_API_URL`)
   - 배포 실행
   - 도메인 확인

3. **CORS 설정 업데이트**
   - 백엔드 `CORS_ORIGINS`에 프론트엔드 도메인 추가

4. **배포 검증**
   - Health check 확인
   - API 엔드포인트 테스트
   - 프론트엔드-백엔드 연동 확인

### 상세 가이드

- **Railway 배포**: `docs/RAILWAY_DEPLOYMENT.md` 참고
- **Vercel 배포**: `docs/VERCEL_DEPLOYMENT.md` 참고

---

## 프로덕션 환경변수 설정

### 필수 환경변수

프로덕션 환경에서 다음 환경변수를 설정해야 합니다:

#### 1. DATABASE_URL

**설명**: Supabase PostgreSQL 데이터베이스 연결 문자열

**형식**:
```
postgresql+psycopg2://user:password@host:port/database?sslmode=require
```

**설정 방법**:
1. Supabase 프로젝트 대시보드 접속
2. Settings → Database → Connection string
3. "URI" 형식 선택
4. `postgresql://`을 `postgresql+psycopg2://`로 변경
5. `?sslmode=require` 추가

**예시**:
```env
DATABASE_URL=postgresql+psycopg2://postgres.xxxxx:your_password@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require
```

**보안**:
- 프로덕션 비밀번호는 강력한 비밀번호 사용
- 연결 문자열은 환경변수로만 관리 (코드에 하드코딩 금지)
- Supabase Connection Pooling 사용 권장

#### 2. OPENAI_API_KEY

**설명**: OpenAI API 키 (GPT-4o-mini 사용)

**설정 방법**:
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. API Keys → Create new secret key
3. 키 생성 및 복사 (한 번만 표시됨)

**예시**:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**보안**:
- API 키는 절대 Git에 커밋하지 마세요
- 키가 노출되면 즉시 재생성
- 사용량 모니터링 설정 권장

#### 3. CORS_ORIGINS

**설명**: 허용할 프론트엔드 도메인 (쉼표로 구분)

**프로덕션 예시**:
```env
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

**개발 환경 예시**:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**주의사항**:
- 프로덕션에서는 실제 도메인만 허용
- 와일드카드(`*`) 사용 금지 (보안 위험)
- HTTPS 사용 권장

#### 4. DEBUG

**설명**: 디버그 모드 활성화 여부

**프로덕션 설정**:
```env
DEBUG=false
```

**주의사항**:
- 프로덕션에서는 반드시 `false`로 설정
- `true`로 설정 시 상세한 에러 정보가 노출될 수 있음

#### 5. RSS_COLLECTION_INTERVAL_MINUTES

**설명**: RSS 수집 주기 (분 단위)

**기본값**: `20`

**프로덕션 예시**:
```env
RSS_COLLECTION_INTERVAL_MINUTES=20
```

**권장값**:
- 일반 소스: 20-30분
- arXiv: 하루 2회 (스케줄러에서 별도 처리)

#### 6. REF_DATE (선택사항)

**설명**: 그룹화 기준 날짜 (YYYY-MM-DD 형식)

**설정 예시**:
```env
REF_DATE=2024-11-20
```

**주의사항**:
- 비워두면 오늘 UTC 자정을 사용
- 백필 윈도우는 이 날짜 포함 과거 21일

### 환경별 설정 예시

#### 개발 환경

```env
DATABASE_URL=postgresql+psycopg2://postgres:dev_password@localhost:5432/ai_trend_dev
OPENAI_API_KEY=sk-dev-key-here
APP_NAME=AI Trend Monitor
APP_VERSION=0.1.0
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
RSS_COLLECTION_INTERVAL_MINUTES=20
REF_DATE=
```

#### 스테이징 환경

```env
DATABASE_URL=postgresql+psycopg2://postgres:staging_password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
OPENAI_API_KEY=sk-staging-key-here
APP_NAME=AI Trend Monitor
APP_VERSION=0.1.0
DEBUG=false
CORS_ORIGINS=https://staging.your-domain.com
RSS_COLLECTION_INTERVAL_MINUTES=20
REF_DATE=
```

#### 프로덕션 환경

```env
DATABASE_URL=postgresql+psycopg2://postgres:production_password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
OPENAI_API_KEY=sk-production-key-here
APP_NAME=AI Trend Monitor
APP_VERSION=0.1.0
DEBUG=false
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
RSS_COLLECTION_INTERVAL_MINUTES=20
REF_DATE=
```

---

## 데이터베이스 마이그레이션

### 프로덕션 DB에 마이그레이션 적용

#### 1. 마이그레이션 준비

프로덕션 DB에 마이그레이션을 적용하기 전에:

1. **백업 확인**: Supabase는 자동 백업을 제공하지만, 수동 백업도 권장
2. **스테이징 환경에서 테스트**: 프로덕션 전에 스테이징 환경에서 마이그레이션 테스트
3. **다운타임 계획**: 필요 시 유지보수 시간대 계획

#### 2. 마이그레이션 실행

**로컬에서 실행** (프로덕션 DB 연결):

```bash
# 프로젝트 루트에서 실행
# DATABASE_URL 환경변수 설정
$env:DATABASE_URL = "postgresql+psycopg2://user:password@host:port/database?sslmode=require"

# 마이그레이션 실행
poetry run alembic upgrade head
```

**또는 직접 연결 문자열 지정**:

```bash
poetry run alembic -x sqlalchemy.url="postgresql+psycopg2://user:password@host:port/database?sslmode=require" upgrade head
```

#### 3. 마이그레이션 확인

마이그레이션이 성공적으로 적용되었는지 확인:

```bash
# 현재 버전 확인
poetry run alembic current

# 마이그레이션 히스토리 확인
poetry run alembic history

# 데이터베이스 테이블 확인 (Supabase 대시보드에서)
```

#### 4. 마이그레이션 롤백

문제가 발생한 경우 롤백:

```bash
# 한 단계 롤백
poetry run alembic downgrade -1

# 특정 버전으로 롤백
poetry run alembic downgrade <revision>

# 모든 마이그레이션 롤백 (주의!)
poetry run alembic downgrade base
```

**주의사항**:
- 롤백은 데이터 손실을 일으킬 수 있음
- 롤백 전에 반드시 백업 확인
- 프로덕션에서는 신중하게 진행

### 백업 전략

#### Supabase 자동 백업

Supabase는 자동으로 일일 백업을 제공합니다:

1. **백업 확인**: Supabase 대시보드 → Database → Backups
2. **백업 복원**: 필요 시 대시보드에서 복원 가능
3. **백업 보관 기간**: 플랜에 따라 다름 (무료 플랜: 7일)

#### 수동 백업

중요한 변경 전에는 수동 백업을 권장:

```bash
# pg_dump를 사용한 백업 (로컬 PostgreSQL 클라이언트 필요)
pg_dump "postgresql://user:password@host:port/database?sslmode=require" > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Supabase 대시보드에서도 수동 백업 가능
```

#### 백업 검증

백업이 올바른지 확인:

```bash
# 백업 파일 크기 확인
Get-Item backup_*.sql | Select-Object Name, Length

# 백업 내용 확인 (일부)
Get-Content backup_*.sql | Select-Object -First 50
```

---

## 배포 아키텍처

### 권장 아키텍처

```
┌─────────────────┐
│  Vercel (Next.js) │  ← 프론트엔드
└────────┬────────┘
         │ API 호출
┌────────▼────────┐
│ Backend API      │  ← 별도 서버 (Railway/Render/Fly.io)
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

### 배포 구성 요소

1. **프론트엔드**: Vercel (Next.js 최적화)
2. **백엔드 API**: Railway/Render/Fly.io (FastAPI)
3. **스케줄러 워커**: 별도 서버 (Railway/Render/Fly.io)
4. **데이터베이스**: Supabase (PostgreSQL)

### 배포 순서

1. **데이터베이스 마이그레이션**: 프로덕션 DB에 스키마 적용
2. **초기 데이터 설정**: RSS 소스 등록
3. **백엔드 API 배포**: FastAPI 서버 배포
4. **스케줄러 워커 배포**: Worker 프로세스 배포
5. **프론트엔드 배포**: Next.js 앱 배포

자세한 배포 방법은 `TODOs.md`의 Phase 5 섹션을 참고하세요.

---

## Railway 배포 (백엔드)

Railway는 Dockerfile 기반 배포를 지원합니다. 상세 가이드는 `docs/RAILWAY_DEPLOYMENT.md`를 참고하세요.

### 주요 단계

1. **Railway 프로젝트 생성**
   - GitHub 저장소 연동
   - 프로젝트 이름 설정

2. **API 서비스 배포**
   - 서비스 생성 (이름: `api`)
   - Dockerfile 자동 감지
   - 시작 명령: `poetry run uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - 환경변수 설정

3. **Worker 서비스 배포**
   - 서비스 생성 (이름: `worker`)
   - 동일한 Dockerfile 사용
   - 시작 명령: `poetry run python -m backend.scripts.worker`
   - 환경변수 설정 (API와 동일)

4. **도메인 생성**
   - Railway 대시보드 → Settings → Networking
   - "Generate Domain" 클릭
   - 생성된 도메인을 프론트엔드 `NEXT_PUBLIC_API_URL`에 설정

### 필수 파일

- `Dockerfile`: 프로젝트 루트에 위치
- `.dockerignore`: 빌드 최적화
- `pyproject.toml`: Poetry 의존성 관리
- `poetry.lock`: 의존성 잠금 파일

---

## Vercel 배포 (프론트엔드)

Vercel은 Next.js를 자동으로 감지하고 배포합니다. 상세 가이드는 `docs/VERCEL_DEPLOYMENT.md`를 참고하세요.

### 주요 단계

1. **Vercel 프로젝트 생성**
   - GitHub 저장소 연동
   - Root Directory: `frontend`
   - Framework Preset: Next.js (자동 감지)

2. **환경변수 설정**
   - `NEXT_PUBLIC_API_URL`: Railway API 도메인

3. **배포 실행**
   - 자동 배포 (GitHub push 시)
   - 또는 수동 배포

4. **도메인 확인**
   - Vercel 기본 도메인 확인
   - 백엔드 `CORS_ORIGINS`에 추가

### 필수 파일

- `frontend/vercel.json`: Vercel 설정 (선택사항)
- `frontend/package.json`: Next.js 프로젝트 설정
- `frontend/next.config.ts`: Next.js 설정

---

## 보안 고려사항

### API 키 관리

1. **환경변수 사용**: 코드에 하드코딩 금지
2. **비밀 관리 서비스**: 배포 플랫폼의 환경변수 기능 사용
3. **키 로테이션**: 정기적으로 API 키 변경
4. **접근 제한**: 최소 권한 원칙 적용

### 데이터베이스 보안

1. **SSL 연결**: `sslmode=require` 사용
2. **강력한 비밀번호**: 복잡한 비밀번호 사용
3. **연결 풀링**: Supabase Connection Pooler 사용
4. **백업 암호화**: 백업 파일 암호화 저장

### CORS 설정

1. **명시적 도메인**: 와일드카드 사용 금지
2. **HTTPS 사용**: 프로덕션에서는 HTTPS만 허용
3. **자격 증명**: `allow_credentials=True`는 신중하게 사용

### 로깅 및 모니터링

1. **민감 정보 제외**: 로그에 API 키, 비밀번호 등 포함 금지
2. **에러 추적**: Sentry 등 에러 추적 서비스 사용 (선택사항)
3. **접근 로그**: API 접근 로그 모니터링

---

## 환경변수 체크리스트

배포 전 확인사항:

- [ ] `DATABASE_URL`이 올바른 프로덕션 DB를 가리키는지 확인
- [ ] `OPENAI_API_KEY`가 프로덕션 키인지 확인
- [ ] `DEBUG=false`로 설정되었는지 확인
- [ ] `CORS_ORIGINS`에 올바른 프론트엔드 도메인이 포함되어 있는지 확인
- [ ] 모든 환경변수가 배포 플랫폼에 설정되었는지 확인
- [ ] 환경변수가 Git에 커밋되지 않았는지 확인

---

## 문제 해결

### 마이그레이션 실패

**문제**: 마이그레이션 실행 중 오류 발생

**해결**:
1. 에러 메시지 확인
2. 데이터베이스 연결 확인
3. 이전 마이그레이션 상태 확인: `alembic current`
4. 필요 시 롤백 후 재시도

### 환경변수 로드 실패

**문제**: 환경변수가 제대로 로드되지 않음

**해결**:
1. 배포 플랫폼의 환경변수 설정 확인
2. 환경변수 이름이 정확한지 확인 (대소문자 구분)
3. 애플리케이션 재시작

### 데이터베이스 연결 실패

**문제**: 프로덕션 DB에 연결할 수 없음

**해결**:
1. `DATABASE_URL` 형식 확인
2. Supabase 프로젝트 상태 확인
3. 방화벽/네트워크 설정 확인
4. SSL 모드 확인 (`sslmode=require`)

---

## 참고 자료

- **초기 설정 가이드**: `docs/SETUP.md`
- **개발자 가이드**: `docs/DEVELOPER_GUIDE.md` (작성 예정)
- **프로젝트 계획**: `TODOs.md`
- **Supabase 문서**: https://supabase.com/docs
- **OpenAI API 문서**: https://platform.openai.com/docs

