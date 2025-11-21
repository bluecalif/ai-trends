# 디버깅 가이드

## 개요

이 문서는 프론트엔드에서 API 호출이 실패하거나 로그가 보이지 않을 때 문제를 진단하는 방법을 설명합니다.

## 단계별 로그 시스템

프론트엔드는 8단계 로그 시스템을 사용합니다:

### [STEP 0] Page Load
- 페이지가 처음 로드될 때 실행
- URL, User Agent 정보 로그

### [STEP 1] RootLayout Body Rendered
- React 앱의 루트 레이아웃이 렌더링될 때 실행

### [STEP 2] Providers Mounted
- React Query Provider가 초기화될 때 실행
- QueryClient 생성 확인
- 환경변수 확인 (NEXT_PUBLIC_API_URL)

### [STEP 3] API Client Initialized
- Axios 인스턴스가 생성될 때 실행
- API_BASE_URL 값 확인

### [STEP 4] Navigation Rendered
- 네비게이션 바가 렌더링될 때 실행

### [STEP 5] HomePage Component Mounted
- 홈 페이지 컴포넌트가 마운트될 때 실행
- Suspense 경계 확인

### [STEP 6] HomePageContent Rendered
- 실제 콘텐츠 컴포넌트가 렌더링될 때 실행
- Query 파라미터 파싱 확인

### [STEP 7] useQuery Execution
- React Query가 실행될 때
- queryFn 실행 확인
- Query 상태 변화 추적

### [STEP 8] API Request/Response
- 실제 HTTP 요청이 발생할 때
- 요청 URL, 메서드 확인
- 응답 상태 확인

## 브라우저에서 확인하는 방법

### 1. 콘솔 탭 확인

1. 브라우저에서 사이트 접속
2. F12 (또는 우클릭 → 검사) → Console 탭
3. 다음 로그들을 순서대로 확인:

```
[STEP 0] Page Load
[STEP 1] RootLayout Body Rendered
[STEP 2] Providers Mounted
[STEP 3] API Client Initialized
[STEP 4] Navigation Rendered
[STEP 5] HomePage Component Mounted
[STEP 6] HomePageContent Rendered
[STEP 7] useQuery Execution
[STEP 8] API Request
```

### 2. 환경변수 확인

STEP 2에서 다음 정보를 확인:
```
[DEBUG] Environment Variables
NEXT_PUBLIC_API_URL: https://ai-trends-production.up.railway.app
```

**문제 상황**:
- `NEXT_PUBLIC_API_URL: undefined` → 환경변수가 설정되지 않음
- `NEXT_PUBLIC_API_URL: http://localhost:8000` → 환경변수가 기본값으로 설정됨
- 값이 잘못됨 → Vercel 환경변수 확인 필요

### 3. 네트워크 탭 확인

1. F12 → Network 탭
2. 페이지 새로고침
3. `/api/items` 요청 확인

**정상 상황**:
- 요청이 보임
- Status: 200
- Request URL: `https://ai-trends-production.up.railway.app/api/items`

**문제 상황**:
- 요청이 없음 → STEP 7까지 도달하지 못함
- 404 오류 → URL이 잘못됨
- CORS 오류 → 백엔드 CORS 설정 확인

## 문제 진단 체크리스트

### 로그가 전혀 보이지 않는 경우

1. **JavaScript가 실행되지 않음**
   - 브라우저 콘솔에 다른 에러가 있는지 확인
   - Network 탭에서 JavaScript 파일이 로드되는지 확인
   - 빌드 오류가 있는지 Vercel 로그 확인

2. **페이지가 로드되지 않음**
   - 브라우저 주소창 확인
   - 페이지 소스 보기 (우클릭 → 페이지 소스 보기)
   - HTML이 렌더링되는지 확인

3. **콘솔 필터링**
   - 콘솔 필터가 "All levels"로 설정되어 있는지 확인
   - "Hide network" 옵션이 꺼져 있는지 확인

### STEP 2까지는 보이지만 STEP 3이 안 보이는 경우

- 환경변수가 로드되지 않음
- Vercel 환경변수 확인
- Vercel 재배포 필요

### STEP 7까지는 보이지만 STEP 8이 안 보이는 경우

- React Query가 실행되지 않음
- queryFn이 호출되지 않음
- Suspense가 해제되지 않음
- useSearchParams() 문제 가능성

### STEP 8은 보이지만 네트워크 요청이 없는 경우

- Axios 인터셉터는 실행되지만 실제 HTTP 요청이 발생하지 않음
- 네트워크 연결 문제
- 브라우저 확장 프로그램 간섭

## 디버그 로그 확인

브라우저 콘솔에서 다음 명령어로 모든 로그를 확인할 수 있습니다:

```javascript
// 모든 디버그 로그 확인
window.__debugLogs
```

## 에러 해석

### "NEXT_PUBLIC_API_URL is undefined"
- **원인**: 환경변수가 빌드 시점에 포함되지 않음
- **해결**: Vercel 환경변수 설정 확인 및 재배포

### "Network Error" 또는 "Failed to fetch"
- **원인**: 네트워크 연결 문제 또는 CORS 오류
- **해결**: 백엔드 CORS 설정 확인, Railway URL 확인

### "404 Not Found"
- **원인**: API 경로가 잘못됨
- **해결**: API_BASE_URL과 경로 확인

### "CORS policy: No 'Access-Control-Allow-Origin'"
- **원인**: 백엔드 CORS 설정 문제
- **해결**: Railway 백엔드 CORS_ORIGINS 환경변수 확인

## 다음 단계

문제를 진단한 후:
1. 로그 결과를 기록
2. 어느 단계에서 멈췄는지 확인
3. 해당 단계의 원인 분석
4. 해결책 적용

## 참고

- Vercel 배포 로그: Vercel 대시보드 → Deployments → 최신 배포 → Build Logs
- Railway 백엔드 로그: Railway 대시보드 → API 서비스 → Logs
- 브라우저 개발자 도구: F12

