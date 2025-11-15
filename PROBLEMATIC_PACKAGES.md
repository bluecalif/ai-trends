# Poetry "Unknown metadata version: 2.4" 문제 패키지 분석

## 문제 원인

Poetry 1.8.4는 PEP 621 메타데이터 버전 2.4를 지원하지 않습니다.  
Poetry 1.8.5 이상에서는 `pkginfo` 패키지의 최소 요구 버전을 1.12로 상향 조정하여 메타데이터 버전 2.4를 인식할 수 있도록 개선되었습니다.

## 문제가 될 가능성이 높은 패키지 목록

### 1. 최신 릴리즈 패키지 (2024년 이후)

다음 패키지들은 최근에 PEP 621 메타데이터 버전 2.4를 채택했을 가능성이 높습니다:

#### 높은 가능성
- **pydantic** (>=2.5.0) - 최신 버전에서 PEP 621 사용
- **pydantic-settings** (>=2.1.0) - Pydantic과 함께 업데이트
- **httpx** (>=0.25.0) - 최신 버전에서 메타데이터 업데이트
- **openai** (>=1.10.0) - 최신 릴리즈에서 PEP 621 채택 가능
- **fastapi** (>=0.104.0) - 최신 버전에서 의존성 업데이트

#### 중간 가능성
- **uvicorn** (>=0.24.0) - 최신 버전
- **sqlalchemy** (>=2.0.20) - 최신 2.0 시리즈
- **alembic** (>=1.12.0) - 최신 버전
- **apscheduler** (>=3.10.0) - 최신 버전

#### 낮은 가능성 (안정적)
- **feedparser** - 오래된 패키지, 메타데이터 변경 가능성 낮음
- **python-dotenv** - 안정적
- **python-dateutil** - 안정적
- **beautifulsoup4** - 안정적
- **lxml** - 안정적
- **scikit-learn** - 안정적
- **numpy** - 안정적
- **psycopg2-binary** - 안정적

### 2. 개발 의존성

- **ruff** (>=0.1.11) - 최신 릴리즈, PEP 621 사용 가능성 높음
- **black** (>=24.1.1) - 최신 버전
- **pytest** (>=7.4.4) - 최신 버전

## 해결 방법

### 방법 1: Poetry 업데이트 (권장)

Poetry 1.8.5 이상으로 업데이트:
```powershell
# Poetry 재설치
pip uninstall poetry -y
pip install poetry>=1.8.5
```

### 방법 2: 문제 패키지 버전 낮추기

`pyproject.toml`에서 다음 패키지들의 버전을 낮춥니다:

```toml
# 문제 가능성 높은 패키지 버전 조정
pydantic = ">=2.4.0,<2.5.0"  # 2.5.0 대신 2.4.x 사용
pydantic-settings = ">=2.0.0,<2.1.0"  # 2.1.0 대신 2.0.x 사용
httpx = ">=0.24.0,<0.25.0"  # 0.25.0 대신 0.24.x 사용
openai = ">=1.9.0,<1.10.0"  # 1.10.0 대신 1.9.x 사용
fastapi = ">=0.103.0,<0.104.0"  # 0.104.0 대신 0.103.x 사용
```

### 방법 3: requirements.txt 사용

Poetry 없이 `requirements.txt`를 사용하여 개발 진행:
```powershell
pip install -r requirements.txt
```

## 확인 방법

특정 패키지가 문제인지 확인하려면:

1. **단일 패키지로 테스트**:
```powershell
poetry add pydantic@2.4.2  # 낮은 버전으로 테스트
poetry lock
```

2. **패키지별로 순차적으로 추가**:
```powershell
# pyproject.toml을 비우고 하나씩 추가
poetry add fastapi
poetry lock  # 성공하면 다음 패키지 추가
```

## 참고 자료

- [Poetry 1.8.5 Release Notes](https://github.com/python-poetry/poetry/releases)
- [PEP 621 - Project metadata](https://peps.python.org/pep-0621/)
- [pkginfo 1.12 changelog](https://pypi.org/project/pkginfo/)

