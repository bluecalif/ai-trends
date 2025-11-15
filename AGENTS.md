# AI 에이전트 운영 가이드

> **환경**: Windows PowerShell 5.1  
> **프로젝트**: 

---

## 1. PowerShell 명령어 표준

### 1.1 명령어 연결

```powershell
# ✅ 세미콜론 사용
cd C:\Projects\ideator-books; python -m pytest tests/

# ❌ Bash && 연산자 사용 금지
cd C:\Projects\ideator-books && python -m pytest tests/
```

### 1.2 환경 변수

```powershell
# 설정
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
$env:OPENAI_API_KEY = "sk-xxx"

# 확인
echo $env:OPENAI_API_KEY
Get-ChildItem Env:
```

### 1.3 디렉토리 및 파일

```powershell
# 디렉토리 생성 (부모 디렉토리 자동 생성)
New-Item -ItemType Directory -Path "backend\api\models" -Force

# 파일 작업
Get-Content file.txt          # 읽기
Copy-Item src.txt dst.txt     # 복사
Remove-Item file.txt          # 삭제
Test-Path .env                # 존재 확인
```

### 1.4 Python 실행

```powershell
# 스크립트 실행
python backend/tests/test_kb_parser.py
python -m pytest backend/tests/ -v

# 환경 변수 설정 후 실행
$env:LOG_LEVEL = "DEBUG"; python script.py

# Python -c (작은따옴표 사용)
python -c 'print("Hello")'
```

### 1.5 서버 실행

```powershell
# 백엔드 (FastAPI) - PYTHONPATH 필수
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
cd backend; python -m uvicorn main:app --reload --port 8000

# 프론트엔드 (Next.js)
cd frontend; npm run dev
```

### 1.6 출력 제한

```powershell
# head/tail 대체
git diff file.py | Select-Object -First 50
git log | Select-Object -Last 20

# 필터링
git status | Select-String "modified"
git status | Select-String -NotMatch "node_modules"
```

### 1.7 인코딩 규칙

**PowerShell은 이모지 미지원 → 텍스트 사용**

#### 문제 상황
```powershell
python test.py
# UnicodeEncodeError: 'cp949' codec can't encode character '\U0001f680'
```

#### 해결 방법 1: Python 코드에서 이모지 제거

```python
# ❌ 이모지 사용 금지
print("✓ Test passed")
print("✅ Success")
print("🚀 Starting...")
print("📊 Report")

# ✅ 텍스트 사용
print("[OK] Test passed")
print("[PASS] Success")
print("[START] Starting...")
print("[REPORT] Report")
```

#### 해결 방법 2: Python에서 UTF-8 강제 출력

```python
import sys
import io

# 스크립트 맨 위에 추가 (import 전)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 이후 이모지 출력 가능 (권장하지 않음)
print("✅ Success")
```

#### 권장 사항
- **모든 Python 스크립트에서 이모지 사용 금지**
- **로그 출력은 `[OK]`, `[FAIL]`, `[WARN]` 같은 태그 사용**
- **테스트 결과는 텍스트로 표현** (`PASS`/`FAIL`)
- **파일명에도 이모지 사용 금지**

---

### 1.8 실행 경로 규칙 (중요)

- 모든 명령은 프로젝트 루트(`C:\Projects\vibe-coding\ai-trend`) 기준으로 실행
- 세션 중 `cd` 사용 금지 (경로 중첩 오류 방지)
- 예시:
  - `poetry run alembic upgrade head`
  - `poetry run python -m pytest backend/tests/integration -v`
  - `poetry run python -m pytest backend/tests/e2e -m e2e_real_data -v -s`

---

### 1.9 답변 가이드라인 (친절 모드)

- 목적: 사용자가 빠르게 이해하고 바로 조치할 수 있도록, 간결하고 배려 있는 형식으로 답변합니다.
- 기본 형식
  - 요약(결론): 한두 문장으로 핵심을 명확히 제시
  - 근거(파일/라인/결과): 결과 JSON이나 로그 파일 경로와 핵심 필드만 인용
  - 다음 액션: 바로 실행 가능한 1~2개 후속 조치 제안
- 예시
  - 요약: “대체 피드(URL)가 DB에 반영되었고 수집이 성공했습니다. DeepMind만 오류가 남았습니다.”
  - 근거: backend/tests/results/rss_collect_verify_YYYYMMDD_HHMMSS.json → IEEE 수집 30, OpenAI 수집 732, DeepMind malformed 오류
  - 다음 액션: “수집 재실행 → 백필/증분 실행 → /api/groups E2E 재검증 결과 JSON 저장”

주의
- 모호한 표현만으로 결론을 내지 말고, 반드시 결과 파일/로그의 정량 근거를 포함합니다.
- 주소/설정 문제와 데이터/시그널 문제를 구분해 진단을 제시합니다.

---

## 2. 터미널 문제 해결

### 2.1 프로세스 강제 종료

```powershell
# Ctrl+C로 종료 시도 후

# 프로세스 종료
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# 또는
Stop-Process -Name "node" -Force
Stop-Process -Name "python" -Force
```

### 2.2 포트 점유 확인 및 종료

```powershell
# 포트 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# PID로 종료
taskkill /F /PID [PID번호]
```

### 2.3 프로세스 모니터링

```powershell
# 프로세스 확인
Get-Process | Where-Object {$_.ProcessName -eq "node"}
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

---

## 3. 환경변수 파일 관리

### 3.1 핵심 문제

**.env 파일이 숨김 속성 → AI 도구가 인식 못함**

### 3.2 파일 확인 표준 (우선순위 순)

```powershell
# 1. PowerShell -Force 옵션 (최우선)
Get-ChildItem -Name "*.env*" -Force

# 2. 파일 내용 확인
Get-Content .env
Get-Content .env.example
Get-Content frontend\.env.local

# 3. 파일 존재 확인
Test-Path .env
Test-Path frontend\.env.local
```

```powershell
# ❌ 작동 안 함 (숨김 파일 미포함)
dir *.env*
ls .env*

# ❌ AI 도구 사용 불가 (숨김 파일 인식 한계)
glob_file_search(".env*")
read_file(".env")
```

### 3.3 파일 위치

```
ideator-books/
├── .env                # 백엔드 (프로젝트 루트)
├── .env.example        # 예시
└── frontend/
    └── .env.local      # 프론트엔드
```

### 3.4 환경변수 검증

**PowerShell**
```powershell
echo $env:OPENAI_API_KEY
echo $env:PYTHONPATH
Get-ChildItem Env:
```

**Python**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
```

### 3.5 Next.js 환경변수 규칙

```bash
# 클라이언트 사이드 (NEXT_PUBLIC_ 접두사 필수)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co

# 서버 사이드 (접두사 없음)
OPENAI_API_KEY=sk-xxx
```

---

## 4. Poetry 패키지 관리

### 4.1 버전 요구사항

**Poetry 1.8.5 이상 필수** (최신 패키지의 PEP 621 메타데이터 버전 2.4 지원)

```powershell
# 버전 확인 및 업데이트
poetry --version
pip install --upgrade poetry>=1.8.5
```

### 4.2 주요 오류: "Unknown metadata version: 2.4"

**원인**: Poetry 1.8.4 이하는 메타데이터 버전 2.4 미지원  
**해결**: Poetry 1.8.5 이상으로 업데이트

```powershell
pip uninstall poetry -y
pip install poetry>=1.8.5
poetry lock
poetry install
```

### 4.3 프로젝트 초기 설정

```powershell
poetry --version          # 1.8.5 이상 확인
poetry lock              # lock 파일 생성
poetry install           # 패키지 설치
```

### 4.4 대안: requirements.txt

Poetry 문제 시:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 체크리스트

### Poetry 프로젝트 시작 전
- [ ] `poetry --version` 확인 (1.8.5 이상 필수)
- [ ] `poetry lock` 성공 확인
- [ ] `poetry install` 완료 확인

### 서버 실행 전
- [ ] `Get-Content .env` 로 파일 확인
- [ ] `echo $env:OPENAI_API_KEY` 로 환경변수 확인
- [ ] `$env:PYTHONPATH` 설정
- [ ] `netstat -ano | findstr :8000` 포트 충돌 확인

### 코드 작성 시
- [ ] 이모지 사용 금지 → `[OK]`, `[PASS]`, `[FAIL]` 사용
- [ ] 명령어 연결은 세미콜론(`;`) 사용
- [ ] 환경변수는 PowerShell 명령어로 확인
