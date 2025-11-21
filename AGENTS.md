# AI 에이전트 운영 가이드

> **환경**: Windows PowerShell 5.1  
> **프로젝트**: 

---

## ⚠️ 가장 중요: 사용자 설명 필수 원칙

### 핵심 원칙

**모든 작업 전에 반드시 설명하고, 실행은 사용자 확인 후 진행**

1. **설명 우선, 실행 후순위**
   - 작업 내용을 먼저 설명
   - 사용자 확인 후 실행
   - 실행 결과를 해석하고 다음 단계 제시

2. **단계별 명확한 설명**
   - 무엇을 할 것인지 (What)
   - 왜 하는지 (Why)
   - 어떻게 할 것인지 (How)
   - 예상 결과와 대책 (Result & Action)

3. **Sequential Thinking 활용**
   - 복잡한 문제는 단계별 분석
   - 각 단계의 원인과 해결책 제시
   - 사용자에게 명확한 진단 결과 제공

4. **결과 해석 및 대책 제시**
   - 실행 결과를 정량적으로 설명
   - 문제가 있으면 원인 분석
   - 구체적인 해결 방법 제시
   - 다음 단계 명확히 안내

### 설명 템플릿

#### 작업 전 설명
```
## 작업 내용
- 무엇을 할 것인지 명확히 설명

## 작업 이유
- 왜 이 작업이 필요한지 설명

## 실행 방법
- 어떻게 실행할 것인지 단계별 설명

## 예상 결과
- 성공 시: 어떤 결과가 나올지
- 실패 시: 어떤 문제가 발생할지

## 확인 사항
- 사용자가 확인해야 할 것들
- 실행 전 체크리스트
```

#### 실행 후 설명
```
## 실행 결과
- 실제로 무엇이 실행되었는지
- 결과 파일/로그 위치

## 결과 해석
- 성공/실패 여부
- 문제가 있다면 원인 분석
- 로그/데이터 기반 정량적 설명

## 다음 단계
- 성공 시: 다음 작업
- 실패 시: 해결 방법 및 재시도
- 사용자가 해야 할 일
```

### 금지 사항

❌ **절대 하지 말 것**:
- 설명 없이 바로 실행
- 결과만 보여주고 해석 없음
- 사용자 확인 없이 작업 진행
- 모호한 표현만 사용
- 정량적 근거 없이 결론 제시

✅ **반드시 해야 할 것**:
- 실행 전 상세 설명
- 사용자 확인 요청
- 결과 해석 및 근거 제시
- 구체적인 다음 단계 안내
- 문제 발생 시 원인 분석 및 해결책

### 예시

**❌ 나쁜 예시**: "디버깅 로그를 추가했습니다. 커밋하시겠어요?"

**✅ 좋은 예시**: 작업 내용(What) → 작업 이유(Why) → 실행 방법(How) → 예상 결과 → 확인 사항을 포함한 상세 설명 후 사용자 확인 요청

---

## 1. PowerShell 명령어 표준

### 1.1 명령어 연결

```powershell
# ✅ 세미콜론 사용
cd C:\Projects\ideator-books; python -m pytest tests/

# ❌ Bash && 연산자 사용 금지
```

### 1.2 환경 변수

```powershell
# 설정
$env:PYTHONPATH = "C:\Projects\vibe-coding\ai-trend"
$env:OPENAI_API_KEY = "sk-xxx"

# 확인
echo $env:OPENAI_API_KEY
Get-ChildItem Env:
```

### 1.3 디렉토리 및 파일

```powershell
New-Item -ItemType Directory -Path "backend\api\models" -Force  # 디렉토리 생성
Get-Content file.txt          # 읽기
Copy-Item src.txt dst.txt     # 복사
Remove-Item file.txt          # 삭제
Test-Path .env                # 존재 확인
```

### 1.4 Python 실행

```powershell
python -m pytest backend/tests/ -v
$env:LOG_LEVEL = "DEBUG"; python script.py
python -c 'print("Hello")'  # 작은따옴표 사용
```

#### 모듈 실행 시 경로 문제 해결

**문제**: `python backend/scripts/script.py` 실행 시 `ModuleNotFoundError: No module named 'backend'` 발생

**해결 방법** (우선순위 순):
```powershell
# 1. -m 옵션 사용 (권장)
poetry run python -m backend.scripts.script_name

# 2. PYTHONPATH 설정
$env:PYTHONPATH = "C:\Projects\vibe-coding\ai-trend"
poetry run python backend/scripts/script.py
```

**권장**: 항상 `python -m` 형식 사용

### 1.5 서버 실행

**중요**: 모든 서버는 프로젝트 루트(`C:\Projects\vibe-coding\ai-trend`)에서 실행. `cd` 사용 금지.

```powershell
# 백엔드 (FastAPI)
poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드 (Next.js)
npm --prefix frontend run dev
```

**주의**: ❌ `cd backend; poetry run uvicorn...` → `ModuleNotFoundError` 발생

### 1.6 출력 제한

```powershell
git diff file.py | Select-Object -First 50  # head 대체
git log | Select-Object -Last 20            # tail 대체
git status | Select-String "modified"        # 필터링
```

### 1.7 인코딩 규칙

**PowerShell은 이모지 미지원 → 텍스트 사용**

**문제**: `UnicodeEncodeError: 'cp949' codec can't encode character`

**해결**: Python 코드에서 이모지 제거, `[OK]`, `[PASS]`, `[FAIL]` 같은 태그 사용

**권장**: 모든 Python 스크립트에서 이모지 사용 금지

---

### 1.8 실행 경로 규칙 (중요)

- 모든 명령은 프로젝트 루트(`C:\Projects\vibe-coding\ai-trend`) 기준으로 실행
- 세션 중 `cd` 사용 금지 (경로 중첩 오류 방지)

---

### 1.9 답변 가이드라인 (친절 모드)

**⚠️ 중요: 위의 "사용자 설명 필수 원칙"을 먼저 참고하세요.**

- 기본 형식: 요약(결론) → 근거(파일/라인/결과) → 다음 액션
- 정량적 근거 필수 (결과 파일/로그 경로와 핵심 필드 인용)
- 주소/설정 문제와 데이터/시그널 문제 구분
- 실행 전 설명 및 사용자 확인 필수
- 실행 후 결과 해석 및 다음 단계 제시

---

## 2. 터미널 문제 해결

### 2.1 프로세스 강제 종료

```powershell
taskkill /F /IM node.exe
taskkill /F /IM python.exe
# 또는
Stop-Process -Name "node" -Force
```

### 2.2 포트 점유 확인 및 종료

```powershell
netstat -ano | findstr :3000  # 포트 확인
taskkill /F /PID [PID번호]    # PID로 종료
```

### 2.3 프로세스 모니터링

```powershell
Get-Process | Where-Object {$_.ProcessName -eq "node"}
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

---

## 3. 환경변수 파일 관리

### 3.1 핵심 문제

**.env 파일이 숨김 속성 → AI 도구가 인식 못함**

### 3.2 파일 확인 표준 (우선순위 순)

```powershell
Get-ChildItem -Name "*.env*" -Force  # 1. -Force 옵션 (최우선)
Get-Content .env                      # 2. 파일 내용 확인
Test-Path .env                       # 3. 파일 존재 확인
```

**주의**: ❌ `dir *.env*`, `glob_file_search(".env*")` → 숨김 파일 미포함

### 3.3 파일 위치

- `.env`: 백엔드 (프로젝트 루트)
- `frontend/.env.local`: 프론트엔드

### 3.4 환경변수 검증

```powershell
echo $env:OPENAI_API_KEY
Get-ChildItem Env:
```

```python
import os
from dotenv import load_dotenv
load_dotenv()
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
```

### 3.5 Next.js 환경변수 규칙

- 클라이언트 사이드: `NEXT_PUBLIC_` 접두사 필수
- 서버 사이드: 접두사 없음

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
poetry --version  # 1.8.5 이상 확인
poetry lock       # lock 파일 생성
poetry install    # 패키지 설치
```

### 4.4 대안: requirements.txt

Poetry 문제 시: `python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt`

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
