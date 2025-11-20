# Vercel 프론트엔드 배포 가이드

이 문서는 AI Trend Monitor 프론트엔드를 Vercel에 배포하는 상세 가이드를 제공합니다.

## 목차

1. [Vercel 계정 설정](#vercel-계정-설정)
2. [프로젝트 배포](#프로젝트-배포)
3. [환경변수 설정](#환경변수-설정)
4. [도메인 설정](#도메인-설정)
5. [배포 검증](#배포-검증)
6. [문제 해결](#문제-해결)

---

## Vercel 계정 설정

### 1. Vercel 계정 생성

1. [Vercel](https://vercel.com) 접속
2. "Sign Up" 클릭
3. GitHub 계정으로 로그인
4. GitHub 저장소 권한 부여

### 2. 새 프로젝트 생성

1. Vercel 대시보드에서 "Add New..." → "Project" 클릭
2. GitHub 저장소 선택: `bluecalif/ai-trends`
3. 프로젝트 설정:
   - **Framework Preset**: Next.js (자동 감지)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (기본값)
   - **Output Directory**: `.next` (기본값)
   - **Install Command**: `npm install` (기본값)

---

## 프로젝트 배포

### 1. 자동 배포 설정

Vercel은 GitHub 저장소와 연동하여 자동 배포를 지원합니다:

- **기본 브랜치**: `main` (또는 `master`)
- **자동 배포**: `main` 브랜치에 push 시 자동 배포
- **Preview 배포**: Pull Request 생성 시 자동 Preview 배포

### 2. 수동 배포

1. Vercel 대시보드 → 프로젝트 → "Deployments"
2. "Redeploy" 버튼 클릭
3. 배포 설정 확인 후 "Redeploy" 클릭

### 3. 빌드 설정 확인

`frontend/vercel.json` 파일이 자동으로 감지됩니다:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install",
  "devCommand": "npm run dev"
}
```

**참고**: Vercel은 Next.js를 자동으로 감지하므로 `vercel.json`은 선택사항입니다.

---

## 환경변수 설정

### 1. 환경변수 추가

Vercel 대시보드 → 프로젝트 → Settings → Environment Variables

**필수 환경변수**:
```
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**설명**:
- `NEXT_PUBLIC_` 접두사: Next.js에서 클라이언트 사이드에서 접근 가능한 환경변수
- 백엔드 API URL: Railway에서 배포한 API 서버 도메인

### 2. 환경별 설정

Vercel은 환경별로 다른 환경변수를 설정할 수 있습니다:

- **Production**: 프로덕션 환경 (기본 도메인)
- **Preview**: Preview 배포 (Pull Request)
- **Development**: 로컬 개발 환경

**권장**: Production과 Preview에서 동일한 API URL 사용 (Railway API 서버)

### 3. 환경변수 적용

환경변수 추가 후:
1. "Save" 클릭
2. **중요**: 기존 배포에 적용하려면 "Redeploy" 필요
3. 새 배포는 자동으로 새 환경변수 사용

---

## 도메인 설정

### 1. Vercel 기본 도메인

1. Vercel 대시보드 → 프로젝트 → Settings → Domains
2. 자동 생성된 도메인 확인 (예: `ai-trend-monitor.vercel.app`)
3. 이 도메인을 백엔드 `CORS_ORIGINS`에 추가

### 2. 커스텀 도메인 (선택사항)

1. Vercel 대시보드 → 프로젝트 → Settings → Domains
2. "Add Domain" 클릭
3. 도메인 입력 (예: `ai-trends.example.com`)
4. DNS 설정 안내에 따라 DNS 레코드 추가
5. SSL 인증서 자동 발급 (몇 분 소요)

### 3. 백엔드 CORS 설정 업데이트

프론트엔드 도메인을 백엔드 `CORS_ORIGINS`에 추가:

**Railway 환경변수 업데이트**:
```
CORS_ORIGINS=https://ai-trend-monitor.vercel.app,https://your-custom-domain.com
```

**참고**: 여러 도메인은 쉼표로 구분합니다.

---

## 배포 검증

### 1. 프론트엔드 접속 확인

1. Vercel 대시보드 → 프로젝트 → "Deployments"
2. 최신 배포의 도메인 클릭
3. 브라우저에서 프론트엔드 페이지 로드 확인

### 2. API 연동 확인

브라우저 개발자 도구 → Network 탭:
1. 페이지 로드 시 API 호출 확인
2. API 응답 상태 확인 (200 OK)
3. CORS 오류 확인 (없어야 함)

### 3. 기능 테스트

- [ ] 홈 페이지 로드
- [ ] 분야별 탭 전환
- [ ] 아이템 목록 표시
- [ ] 아이템 상세 페이지
- [ ] 인물 페이지
- [ ] 북마크 기능
- [ ] 설정 페이지

---

## 문제 해결

### 빌드 실패

**문제**: `npm run build` 실패

**해결**:
1. 빌드 로그 확인 (Vercel 대시보드 → Deployments → 로그)
2. TypeScript 오류 확인
3. 의존성 설치 오류 확인
4. 환경변수 확인 (`NEXT_PUBLIC_API_URL`)

**문제**: `Module not found` 오류

**해결**:
1. `package.json` 의존성 확인
2. `node_modules` 삭제 후 재설치
3. Vercel 빌드 캐시 삭제 (Settings → General → Clear Build Cache)

### API 연결 실패

**문제**: API 호출 시 `Network Error` 또는 `CORS Error`

**해결**:
1. `NEXT_PUBLIC_API_URL` 환경변수 확인
2. 백엔드 API 서버 상태 확인 (Health check)
3. 백엔드 `CORS_ORIGINS`에 프론트엔드 도메인 포함 확인
4. 프로토콜 확인 (`https://` 사용)

**문제**: API 응답이 `undefined` 또는 빈 데이터

**해결**:
1. API 클라이언트 코드 확인 (`frontend/lib/api.ts`)
2. API 응답 형식 확인 (백엔드 스키마와 일치하는지)
3. 브라우저 콘솔 에러 확인
4. Network 탭에서 실제 API 응답 확인

### 환경변수 미적용

**문제**: 환경변수 변경 후에도 이전 값 사용

**해결**:
1. 환경변수 저장 확인 (Vercel 대시보드)
2. **중요**: 환경변수 변경 후 "Redeploy" 필요
3. 빌드 로그에서 환경변수 확인 (Vercel은 빌드 시 환경변수 주입)

---

## Vercel 대시보드 사용법

### 배포 관리

- **배포 목록**: 프로젝트 → Deployments
- **배포 상세**: 각 배포 클릭 → 로그, 설정 확인
- **재배포**: 배포 → "Redeploy" 버튼
- **롤백**: 이전 배포 → "Promote to Production" 버튼

### 설정 관리

- **환경변수**: Settings → Environment Variables
- **도메인**: Settings → Domains
- **빌드 설정**: Settings → General → Build & Development Settings
- **Git 연동**: Settings → Git

### 모니터링

- **Analytics**: 프로젝트 → Analytics (Vercel Pro 필요)
- **Logs**: 프로젝트 → Logs (실시간 로그)
- **Functions**: 프로젝트 → Functions (Serverless Functions 로그)

---

## 배포 체크리스트

### 배포 전

- [ ] `vercel.json` 생성 (선택사항)
- [ ] `package.json` 빌드 스크립트 확인
- [ ] TypeScript 오류 없음 확인
- [ ] 백엔드 API 서버 배포 완료
- [ ] 백엔드 API 도메인 확인

### 배포 중

- [ ] Vercel 프로젝트 생성
- [ ] GitHub 저장소 연동
- [ ] Root Directory 설정 (`frontend`)
- [ ] 환경변수 설정 (`NEXT_PUBLIC_API_URL`)
- [ ] 첫 배포 실행

### 배포 후

- [ ] 프론트엔드 도메인 확인
- [ ] 페이지 로드 확인
- [ ] API 연동 확인
- [ ] CORS 오류 없음 확인
- [ ] 백엔드 `CORS_ORIGINS` 업데이트
- [ ] 기능 테스트

---

## 참고 자료

- **Vercel 문서**: https://vercel.com/docs
- **Next.js 배포**: https://nextjs.org/docs/deployment
- **Railway 배포 가이드**: `docs/RAILWAY_DEPLOYMENT.md`
- **전체 배포 가이드**: `docs/DEPLOYMENT.md`

