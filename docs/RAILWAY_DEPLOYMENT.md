# Railway 배포 가이드

이 문서는 AI Trend Monitor를 Railway에 배포하는 상세 가이드를 제공합니다.

## 목차

1. [Railway 계정 설정](#railway-계정-설정)
2. [백엔드 API 배포](#백엔드-api-배포)
3. [스케줄러 워커 배포](#스케줄러-워커-배포)
4. [환경변수 설정](#환경변수-설정)
5. [배포 검증](#배포-검증)
6. [문제 해결](#문제-해결)

---

## Railway 계정 설정

### 1. Railway 계정 생성

1. [Railway](https://railway.app) 접속
2. "Start a New Project" 클릭
3. GitHub 계정으로 로그인
4. GitHub 저장소 권한 부여

### 2. 새 프로젝트 생성

1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 저장소 선택: `bluecalif/ai-trends`
4. 프로젝트 이름 설정 (예: `ai-trend-monitor`)

---

## 백엔드 API 배포

### 1. 서비스 생성

1. Railway 프로젝트 대시보드에서 "New" 클릭
2. "GitHub Repo" 선택
3. 저장소 선택: `bluecalif/ai-trends`
4. 서비스 이름 설정: `api` (또는 `backend-api`)

### 2. 빌드 설정

Railway는 자동으로 Dockerfile을 감지합니다:

- **Dockerfile**: 프로젝트 루트에 존재 (`Dockerfile`)
- **빌드 명령**: 자동 감지 (Dockerfile의 `RUN` 명령)
- **시작 명령**: Dockerfile의 `CMD` 또는 Railway 설정에서 오버라이드

**시작 명령 설정** (Railway 대시보드):
```
poetry run uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**참고**: Railway는 `$PORT` 환경변수를 자동으로 설정합니다.

### 3. 환경변수 설정

Railway 대시보드 → 서비스 → Variables 탭에서 설정:

**필수 환경변수**:
```
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database?sslmode=require
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=https://your-frontend.vercel.app
DEBUG=false
RSS_COLLECTION_INTERVAL_MINUTES=20
PORT=8000
```

**설명**:
- `DATABASE_URL`: Supabase PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키
- `CORS_ORIGINS`: 프론트엔드 도메인 (Vercel 배포 후 업데이트)
- `DEBUG`: 프로덕션에서는 `false`
- `PORT`: Railway가 자동 설정 (변경 불필요)

### 4. 배포

1. Railway가 자동으로 GitHub push 시 배포 (기본 설정)
2. 또는 "Deploy" 버튼으로 수동 배포
3. 배포 로그 확인 (Railway 대시보드 → Deployments)

### 5. 도메인 설정

1. Railway 대시보드 → 서비스 → Settings → Networking
2. "Generate Domain" 클릭
3. 생성된 도메인 복사 (예: `api-production.up.railway.app`)
4. 이 도메인을 프론트엔드 `NEXT_PUBLIC_API_URL`에 설정

---

## 스케줄러 워커 배포

### 1. Worker 서비스 생성

1. Railway 프로젝트 대시보드에서 "New" 클릭
2. "GitHub Repo" 선택
3. **동일한 저장소 선택**: `bluecalif/ai-trends`
4. 서비스 이름 설정: `worker` (또는 `scheduler-worker`)

### 2. 빌드 설정

- **Dockerfile**: API 서버와 동일한 Dockerfile 사용
- **시작 명령**: Railway 설정에서 오버라이드

**시작 명령 설정** (Railway 대시보드):
```
poetry run python -m backend.scripts.worker
```

### 3. 환경변수 설정

API 서버와 동일한 환경변수 설정:

```
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database?sslmode=require
OPENAI_API_KEY=sk-your-openai-api-key
DEBUG=false
RSS_COLLECTION_INTERVAL_MINUTES=20
```

**참고**: Worker는 `CORS_ORIGINS`와 `PORT`가 필요 없습니다.

### 4. 배포

1. 자동 배포 또는 수동 배포
2. 배포 로그 확인
3. Worker 로그에서 스케줄러 시작 확인

---

## 환경변수 설정

### Railway 환경변수 관리

**방법 1: 서비스별 설정** (권장)
- 각 서비스(API, Worker)에서 개별적으로 설정
- 서비스별로 다른 값 사용 가능

**방법 2: 프로젝트 공통 설정**
- 프로젝트 레벨에서 설정
- 모든 서비스에서 공유

**권장**: API와 Worker는 대부분 동일한 환경변수를 사용하므로, 프로젝트 레벨에서 설정하고 서비스별로 오버라이드하는 방식이 효율적입니다.

### 환경변수 설정 순서

1. **프로젝트 레벨 설정** (공통):
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `DEBUG=false`
   - `RSS_COLLECTION_INTERVAL_MINUTES=20`

2. **API 서비스별 설정**:
   - `CORS_ORIGINS` (프론트엔드 도메인)
   - `PORT` (Railway 자동 설정)

3. **Worker 서비스별 설정**:
   - 추가 설정 불필요 (프로젝트 레벨 설정 사용)

---

## 배포 검증

### 1. API 서버 검증

#### Health Check
```bash
curl https://your-api.railway.app/health
```

예상 응답:
```json
{
  "status": "healthy",
  "scheduler_running": false,
  "database_connected": true
}
```

**참고**: API 서버에서는 `scheduler_running`이 `false`인 것이 정상입니다 (스케줄러는 Worker에서 실행).

#### API 엔드포인트 테스트
```bash
# Items API
curl https://your-api.railway.app/api/items?page=1&page_size=5

# Sources API
curl https://your-api.railway.app/api/sources

# Health Check
curl https://your-api.railway.app/health
```

### 2. Worker 검증

#### 로그 확인
1. Railway 대시보드 → Worker 서비스 → Logs
2. 다음 메시지 확인:
   ```
   [Worker] Starting scheduler worker...
   [Worker] Scheduler started successfully
   ```

#### 스케줄러 작업 확인
로그에서 다음 작업 실행 확인:
- RSS 수집 작업 (20분 간격)
- 증분 그룹화 작업 (20분 간격)
- arXiv 수집 작업 (하루 2회)

### 3. 전체 시스템 검증

#### 프론트엔드-백엔드 연동
1. 프론트엔드에서 API 호출 테스트
2. CORS 오류 확인 (없어야 함)
3. 데이터 로딩 확인

#### 데이터 수집 확인
1. Worker 로그에서 RSS 수집 실행 확인
2. DB에 새 아이템 추가 확인
3. API를 통해 새 아이템 조회 확인

---

## 문제 해결

### 배포 실패

**문제**: Docker 빌드 실패

**해결**:
1. 로그 확인 (Railway 대시보드 → Deployments → 로그)
2. Dockerfile 문법 확인
3. 의존성 설치 오류 확인
4. Poetry 버전 확인 (1.8.5 이상)

**문제**: 애플리케이션 시작 실패

**해결**:
1. 시작 명령 확인 (Railway 설정)
2. 환경변수 확인 (모든 필수 변수 설정되었는지)
3. 포트 설정 확인 (`$PORT` 사용)
4. 로그 확인 (애플리케이션 에러 메시지)

### 데이터베이스 연결 실패

**문제**: `psycopg2.OperationalError: could not connect to server`

**해결**:
1. `DATABASE_URL` 형식 확인 (`postgresql+psycopg2://`)
2. Supabase 프로젝트 상태 확인
3. SSL 모드 확인 (`sslmode=require`)
4. Connection Pooling 사용 확인

### 스케줄러가 시작되지 않음

**문제**: Worker 로그에 스케줄러 시작 메시지 없음

**해결**:
1. 시작 명령 확인: `poetry run python -m backend.scripts.worker`
2. 환경변수 확인 (`DATABASE_URL`, `OPENAI_API_KEY`)
3. 로그에서 에러 메시지 확인
4. Worker 서비스 재배포

### CORS 오류

**문제**: 프론트엔드에서 API 호출 시 CORS 오류

**해결**:
1. `CORS_ORIGINS` 환경변수 확인
2. 프론트엔드 도메인이 정확히 포함되었는지 확인
3. 프로토콜 확인 (`https://` 사용)
4. 쉼표 구분 확인 (여러 도메인인 경우)

---

## Railway 대시보드 사용법

### 서비스 관리

- **서비스 목록**: 프로젝트 대시보드에서 모든 서비스 확인
- **서비스 설정**: 각 서비스 → Settings
- **환경변수**: 각 서비스 → Variables
- **로그**: 각 서비스 → Logs
- **배포**: 각 서비스 → Deployments

### 모니터링

- **리소스 사용량**: 각 서비스 → Metrics
- **트래픽**: 각 서비스 → Metrics → Requests
- **에러**: 각 서비스 → Logs → 에러 필터

### 비용 관리

- **사용량 확인**: 프로젝트 대시보드 → Usage
- **크레딧 확인**: 프로젝트 대시보드 → Billing
- **무료 플랜**: $5 크레딧/월

---

## 배포 체크리스트

### 배포 전

- [ ] Dockerfile 생성 및 테스트
- [ ] 환경변수 목록 정리
- [ ] Supabase 프로젝트 준비
- [ ] OpenAI API 키 준비
- [ ] 프론트엔드 도메인 확인 (Vercel 배포 후)

### 배포 중

- [ ] Railway 프로젝트 생성
- [ ] API 서비스 생성 및 배포
- [ ] Worker 서비스 생성 및 배포
- [ ] 환경변수 설정
- [ ] 도메인 생성 및 확인

### 배포 후

- [ ] Health check 확인
- [ ] API 엔드포인트 테스트
- [ ] Worker 로그 확인
- [ ] 스케줄러 작업 실행 확인
- [ ] 프론트엔드-백엔드 연동 테스트
- [ ] 데이터 수집 확인

---

## 참고 자료

- **Railway 문서**: https://docs.railway.app
- **배포 가이드**: `docs/DEPLOYMENT.md`
- **초기 설정 가이드**: `docs/SETUP.md`
- **프로젝트 계획**: `TODOs.md`

