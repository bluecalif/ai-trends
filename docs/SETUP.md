# AI Trend Monitor - 초기 설정 가이드

이 문서는 AI Trend Monitor 프로젝트의 초기 설정 및 개발 환경 구축 방법을 설명합니다.

## 목차

1. [필수 요구사항](#필수-요구사항)
2. [프로젝트 클론 및 설치](#프로젝트-클론-및-설치)
3. [환경변수 설정](#환경변수-설정)
4. [데이터베이스 설정](#데이터베이스-설정)
5. [초기 데이터 설정](#초기-데이터-설정)
6. [개발 서버 실행](#개발-서버-실행)
7. [문제 해결](#문제-해결)

---

## 필수 요구사항

### 소프트웨어

- **Python**: 3.11 이상
- **Poetry**: 1.8.5 이상 (의존성 관리)
- **Node.js**: 18 이상 (프론트엔드 개발 시)
- **PostgreSQL**: Supabase 사용 (프로덕션) 또는 로컬 PostgreSQL (개발)

### 계정 및 API 키

- **Supabase**: PostgreSQL 데이터베이스 (무료 플랜 사용 가능)
- **OpenAI**: API 키 (GPT-4o-mini 사용)

---

## 프로젝트 클론 및 설치

### 1. 저장소 클론

```bash
git clone https://github.com/bluecalif/ai-trends.git
cd ai-trends
```

### 2. Poetry 설치 확인

```bash
poetry --version
# Poetry 1.8.5 이상이어야 함
```

Poetry가 설치되어 있지 않다면:

```bash
pip install poetry>=1.8.5
```

### 3. 백엔드 의존성 설치

```bash
# 프로젝트 루트에서 실행
poetry install
```

### 4. 프론트엔드 의존성 설치 (선택사항)

프론트엔드 개발을 진행하는 경우:

```bash
cd frontend
npm install
cd ..
```

---

## 환경변수 설정

### 1. 환경변수 파일 생성

프로젝트 루트에 `backend/.env` 파일을 생성합니다:

```bash
# Windows PowerShell
New-Item -ItemType File -Path "backend\.env" -Force

# 또는 텍스트 에디터로 직접 생성
```

### 2. 환경변수 설정

`backend/.env` 파일에 다음 내용을 추가합니다:

```env
# 데이터베이스 (Supabase PostgreSQL)
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database?sslmode=require

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key

# 애플리케이션 설정
APP_NAME=AI Trend Monitor
APP_VERSION=0.1.0
DEBUG=true

# CORS 설정 (개발 환경)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# RSS 수집 주기 (분)
RSS_COLLECTION_INTERVAL_MINUTES=20

# 그룹화 기준 날짜 (선택사항, 비워두면 오늘 UTC 자정)
REF_DATE=
```

**중요**: 
- `DATABASE_URL`은 Supabase 프로젝트 설정에서 "Connection string"을 가져옵니다.
- `OPENAI_API_KEY`는 [OpenAI Platform](https://platform.openai.com/api-keys)에서 생성합니다.
- 실제 값은 `.env` 파일에 저장하고 Git에 커밋하지 마세요 (`.gitignore`에 포함되어 있음).

### 3. 환경변수 확인

PowerShell에서 환경변수가 제대로 로드되는지 확인:

```bash
# Python으로 확인
poetry run python -c "from backend.app.core.config import get_settings; s = get_settings(); print(f'DATABASE_URL: {s.DATABASE_URL[:30]}...')"
```

---

## 데이터베이스 설정

### 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 가입 및 로그인
2. 새 프로젝트 생성
3. 프로젝트 설정 → Database → Connection string 복사
4. `DATABASE_URL`에 연결 문자열 설정

### 2. 데이터베이스 마이그레이션 실행

Alembic를 사용하여 데이터베이스 스키마를 생성합니다:

```bash
# 프로젝트 루트에서 실행
poetry run alembic upgrade head
```

**참고**: 
- `alembic.ini`는 `backend/` 디렉토리에 있습니다.
- Alembic는 `backend/app/core/config.py`에서 `DATABASE_URL`을 자동으로 읽습니다.
- 마이그레이션은 `backend/alembic/versions/` 디렉토리에 있습니다.

### 3. 마이그레이션 확인

마이그레이션이 성공적으로 적용되었는지 확인:

```bash
# 현재 마이그레이션 버전 확인
poetry run alembic current

# 마이그레이션 히스토리 확인
poetry run alembic history
```

---

## 초기 데이터 설정

### 1. 초기 RSS 소스 등록

PRD에 정의된 10개 RSS 소스를 데이터베이스에 등록합니다:

```bash
# 프로젝트 루트에서 실행
poetry run python -m backend.scripts.init_sources
```

**등록되는 소스**:
- TechCrunch
- VentureBeat – AI
- MarkTechPost
- WIRED (All)
- The Verge (All)
- IEEE Spectrum – AI
- AITimes
- arXiv – cs.AI
- OpenAI News
- The Keyword (Google DeepMind filtered)

**출력 예시**:
```
[InitSources] DATABASE_URL=postgresql+psycopg2://...
[InitSources] created=10 skipped=0 total=10
[InitSources] sources total=10, active=10
```

### 2. 초기 데이터 확인

소스가 제대로 등록되었는지 확인:

```bash
# Python으로 확인
poetry run python -c "from backend.app.core.database import SessionLocal; from backend.app.models.source import Source; db = SessionLocal(); sources = db.query(Source).all(); print(f'Total sources: {len(sources)}'); [print(f'  - {s.title}: {s.feed_url}') for s in sources]; db.close()"
```

---

## 개발 서버 실행

### 1. 백엔드 서버 실행

FastAPI 개발 서버를 시작합니다:

```bash
# 프로젝트 루트에서 실행
poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**참고**:
- `--reload`: 코드 변경 시 자동 재시작
- `--host 0.0.0.0`: 로컬 네트워크에서 접근 가능
- 서버는 `http://localhost:8000`에서 실행됩니다.

### 2. API 문서 확인

브라우저에서 다음 URL을 열어 API 문서를 확인합니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Health Check 확인

```bash
# PowerShell
curl http://localhost:8000/health

# 또는 브라우저에서
# http://localhost:8000/health
```

예상 응답:
```json
{
  "status": "healthy",
  "scheduler_running": true
}
```

### 4. 프론트엔드 서버 실행 (선택사항)

프론트엔드 개발을 진행하는 경우:

```bash
cd frontend
npm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

### 5. RSS 수집 테스트

초기 RSS 수집을 테스트합니다:

```bash
# API를 통해 수동 수집
curl -X POST http://localhost:8000/api/rss/collect-all

# 또는 Python 스크립트로
poetry run python -c "from backend.app.core.database import SessionLocal; from backend.app.services.rss_collector import RSSCollector; from backend.app.models.source import Source; db = SessionLocal(); sources = db.query(Source).filter(Source.is_active == True).all(); collector = RSSCollector(db); [print(f'Collected {collector.collect_source(s)} items from {s.title}') for s in sources[:2]]; db.close()"
```

---

## 문제 해결

### Poetry 버전 오류

**문제**: `Unknown metadata version: 2.4` 오류

**해결**:
```bash
pip uninstall poetry -y
pip install poetry>=1.8.5
poetry lock
poetry install
```

### 데이터베이스 연결 오류

**문제**: `psycopg2.OperationalError: could not connect to server`

**해결**:
1. `DATABASE_URL`이 올바른지 확인
2. Supabase 프로젝트가 활성화되어 있는지 확인
3. 방화벽 설정 확인 (Supabase는 SSL 연결 필요)

### 모듈을 찾을 수 없음

**문제**: `ModuleNotFoundError: No module named 'backend'`

**해결**:
- 프로젝트 루트(`C:\Projects\vibe-coding\ai-trend`)에서 명령 실행
- `-m` 옵션 사용: `poetry run python -m backend.scripts.init_sources`

### 환경변수 로드 오류

**문제**: 환경변수가 로드되지 않음

**해결**:
1. `backend/.env` 파일이 올바른 위치에 있는지 확인
2. 파일 인코딩이 UTF-8인지 확인
3. `python-dotenv` 패키지가 설치되어 있는지 확인: `poetry show python-dotenv`

### 마이그레이션 오류

**문제**: `Target database is not up to date`

**해결**:
```bash
# 현재 상태 확인
poetry run alembic current

# 최신 버전으로 업그레이드
poetry run alembic upgrade head

# 문제가 있으면 롤백 후 재시도
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

---

## 다음 단계

초기 설정이 완료되면 다음을 진행하세요:

1. **RSS 수집 테스트**: `/api/rss/collect-all` 엔드포인트로 수집 테스트
2. **API 테스트**: `/docs`에서 API 엔드포인트 테스트
3. **프론트엔드 개발**: `frontend/` 디렉토리에서 Next.js 개발 시작
4. **프로덕션 배포**: `docs/DEPLOYMENT.md` 참고

---

## 참고 자료

- **프로젝트 개요**: `README.md`
- **상세 계획**: `TODOs.md`
- **PRD**: `docs/PRD_ai-trend.md`
- **개발자 가이드**: `docs/DEVELOPER_GUIDE.md` (작성 예정)
- **배포 가이드**: `docs/DEPLOYMENT.md` (작성 예정)

