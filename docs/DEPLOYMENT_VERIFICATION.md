# 배포 후 검증 가이드

이 문서는 AI Trend Monitor 배포 후 시스템 검증 방법을 설명합니다.

## 목차

1. [API 엔드포인트 검증](#api-엔드포인트-검증)
2. [프론트엔드-백엔드 연동 확인](#프론트엔드-백엔드-연동-확인)
3. [RSS 수집 동작 확인](#rss-수집-동작-확인)
4. [스케줄러 동작 확인](#스케줄러-동작-확인)
5. [모니터링 설정](#모니터링-설정)

---

## API 엔드포인트 검증

### 자동 검증 스크립트

프로젝트 루트에서 실행:

```powershell
$env:API_URL = "https://ai-trends-production.up.railway.app"
poetry run python -m backend.scripts.verify_deployment
```

### 검증 항목

1. **Root endpoint** (`/`)
   - 응답: `{"message": "AI Trend Monitor API", "version": "0.1.0"}`

2. **Health check** (`/health`)
   - 응답: `{"status": "healthy", "scheduler_running": true, "database_connected": true}`

3. **Items list** (`/api/items`)
   - 페이지네이션 확인
   - 필터링 확인 (`field`, `custom_tag`, `date_from`, `date_to`)

4. **Sources list** (`/api/sources`)
   - 활성 소스 목록 확인

5. **Persons list** (`/api/persons`)
   - 인물 목록 확인

6. **Constants** (`/api/constants/fields`, `/api/constants/custom-tags`)
   - 상수 값 확인

---

## 프론트엔드-백엔드 연동 확인

### 브라우저에서 확인

1. 프론트엔드 URL 접속: `https://ai-trends.vercel.app`
2. 개발자 도구 (F12) → Network 탭 열기
3. 다음 항목 확인:
   - API 호출 성공 (200 OK)
   - CORS 헤더 확인 (`Access-Control-Allow-Origin`)
   - 필터링 동작 확인 (Research, Industry 등)

### 확인 사항

- ✅ API 호출 성공
- ✅ CORS 설정 정상
- ✅ 필터링 동작 정상 (field별 필터)
- ✅ 페이지네이션 동작 정상

---

## RSS 수집 동작 확인

### Railway Worker 로그 확인

1. Railway 대시보드 접속
2. Worker 서비스 선택
3. Logs 탭 확인

### 확인할 로그 메시지

```
[Worker] Starting scheduler worker...
[Worker] Scheduler started successfully
[RSS] Starting collection for X active sources
[RSS] Collected Y items from [Source Name]
[RSS] Collection complete: X successful, 0 failed, Y total items
```

### 수집 주기

- **일반 소스**: 20분 간격 (설정 가능: `RSS_COLLECTION_INTERVAL_MINUTES`)
- **arXiv 소스**: 하루 2회 (00:00, 12:00 UTC)

### DB에서 확인

```powershell
poetry run python -m backend.scripts.check_db_status
```

최근 수집된 아이템 확인:
- 아이템 수 증가 확인
- `created_at` 시간 확인
- `field` 값 자동 설정 확인

---

## 스케줄러 동작 확인

### Worker 로그 확인

Railway 대시보드 → Worker → Logs에서 확인:

1. **스케줄러 시작**
   ```
   [Worker] Starting scheduler worker...
   [Worker] Scheduler started successfully
   ```

2. **RSS 수집 작업** (20분 간격)
   ```
   [RSS] Starting collection for X active sources
   [RSS] Collection complete: X successful, 0 failed, Y total items
   ```

3. **증분 그룹화 작업** (20분 간격)
   ```
   [Grouping] Incremental grouping processed X items
   ```

4. **일일 백필 작업** (UTC 00:00)
   ```
   [Grouping] Daily backfill processed X items for ref_date=YYYY-MM-DD
   ```

### Health Check로 확인

```bash
curl https://ai-trends-production.up.railway.app/health
```

응답:
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "database_connected": true
}
```

---

## 모니터링 설정

### Railway 대시보드

1. **로그 확인**
   - API 서버: Railway → API Service → Logs
   - Worker: Railway → Worker Service → Logs

2. **메트릭 확인**
   - CPU 사용률
   - 메모리 사용률
   - 네트워크 트래픽

3. **알림 설정** (선택사항)
   - Railway → Settings → Notifications
   - 이메일 알림 설정
   - Slack 연동 (선택사항)

### Health Check 모니터링

정기적으로 `/health` 엔드포인트 확인:

```bash
# 매시간 확인 (cron 또는 외부 모니터링 서비스)
curl https://ai-trends-production.up.railway.app/health
```

### 외부 모니터링 서비스 (선택사항)

- **UptimeRobot**: 무료, 5분 간격 체크
- **Pingdom**: 상업용, 다양한 체크 옵션
- **StatusCake**: 무료 플랜 제공

---

## 문제 해결

### API 엔드포인트 실패

1. Railway 대시보드에서 서비스 상태 확인
2. 로그에서 에러 메시지 확인
3. 환경변수 확인 (`DATABASE_URL`, `OPENAI_API_KEY` 등)

### RSS 수집 실패

1. Worker 로그 확인
2. 소스 URL 유효성 확인
3. 네트워크 연결 확인

### 스케줄러 미작동

1. Worker 로그 확인
2. `is_scheduler_running()` 상태 확인
3. Railway Worker 서비스 재시작

---

## 검증 체크리스트

### Phase 5.6.1 전체 시스템 테스트

- [x] 프론트엔드-백엔드 연동 확인
- [x] API 엔드포인트 테스트 (8/8 성공)
- [ ] RSS 수집 동작 확인 (Worker 로그)
- [ ] 스케줄러 동작 확인 (Worker 로그)

### Phase 5.6.2 모니터링 설정

- [x] 로그 확인 방법 문서화 (이 문서)
- [ ] Health check 모니터링 설정
- [ ] 에러 알림 설정 (선택사항)

---

**마지막 업데이트**: 2025-11-19

