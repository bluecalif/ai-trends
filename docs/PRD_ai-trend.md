# AI Trend Monitor – 통합 사양서 (PRD + 소스/분야/인물 + 기능 백로그 + UI 플로우)

> 개인용 AI 기술 트렌드 모니터링 서비스. **RSS 기반**, **원문 미보관**, **분야·사건 중심 구조화**와 **인물 동향(사업/기술 방향) 누적 정리**를 목표로 함.  
> 분류 체계는 **IPTC Media Topics**와 **IAB Content Taxonomy**를 기반으로 하되, AI 특화 **커스텀 태그(Agents, World Models, Non-Transformer 등)**를 병행한다.  
> (IPTC 공식: :contentReference[oaicite:0]{index=0} / IAB 공식: :contentReference[oaicite:1]{index=1})

---

## 0) 뉴스 소스(공식 RSS/블로그) & 기본 근거
- **TechCrunch (전체)**: https://techcrunch.com/feed/  (RSS 안내/약관: :contentReference[oaicite:2]{index=2})
- **VentureBeat – AI**: https://venturebeat.com/category/ai/feed/  (섹션 RSS 존재 관행)
- **MarkTechPost**: https://www.marktechpost.com/feed/
- **WIRED (All)**: https://www.wired.com/feed/rss  (WIRED RSS 공식 페이지: :contentReference[oaicite:3]{index=3})
- **The Verge (All)**: https://www.theverge.com/rss/index.xml  (The Verge RSS 관련 기사/업데이트: :contentReference[oaicite:4]{index=4})
- **IEEE Spectrum – AI**: https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss  (IEEE 관련 RSS 레퍼런스: :contentReference[oaicite:5]{index=5})
- **AITimes (국내)**: https://www.aitimes.com/rss/allArticle.xml  (공식 사이트: :contentReference[oaicite:6]{index=6})
- **arXiv – cs.AI**: https://rss.arxiv.org/rss/cs.ai  (arXiv RSS 공식 문서: “모든 주제 RSS/ATOM, 매일 0시(EST) 갱신” :contentReference[oaicite:7]{index=7})

> 참고: 상기 URL은 **공식 RSS 또는 공식 도메인에 게재된 경로**를 우선 사용. 제3자 RSS 생성기/큐레이션 페이지는 배제.

---

## 1) PRD (제품 요구사항 문서)

### 1.1 서비스 목적
- AI 기술/산업/연구 트렌드를 **분야·사건 단위**로 구조화하여 한눈에 파악.
- **원문 본문을 저장하지 않고도** 핵심 엔티티(인물·기관·기술)와 상호 관계, 맥락을 **데이터로 보존**하여 언제든 재구성 가능.
- 인물의 단편 이벤트 나열이 아닌, **사업/기술 방향의 누적 타임라인**과 연결 그래프 제공.

### 1.2 사용자 가치
- 정보 과잉에서 **핵심만 추출(요약/엔티티/관계)** → 빠른 파악.
- **분야 탭(Research/Industry/Infra/Policy/Funding + AI-특화 태그)**로 체계적 탐색.
- **Watch(인물·키워드)**로 맞춤 모니터링.

### 1.3 입력 – 처리 – 출력

**입력**
- 공식 RSS/Atom 피드(위 “0) 뉴스 소스”).
- 인물/키워드 규칙(예: “LeCun”, “JEPA”, “agentic”, “NanoChat”).
- 사용자 태그/관심 분야 설정(OPML Import 지원).

**처리**
1) **수집**: 10–30분 폴링으로 RSS 항목 수집. (RSS는 표준, 개인용 합법 사용에 적합 :contentReference[oaicite:8]{index=8})  
2) **정규화**: `title, link, source, published_at, author, language, enclosure` 등 기본 메타.  
3) **요약(1–2문장)**:  
   - 가능하면 RSS `description` 기반. 필요 시 **원문 일시 로드 → 즉시 폐기**, 생성 요약만 저장(본문 미보관).  
4) **엔티티/키워드 추출**: 인물/기관/기술(NER), 핵심 키워드.  
5) **분류(다층)**:  
   - 1차: **IPTC Media Topics** 상위 1–2개. (공식 표준, 연1회+ 업데이트, 다국어 제공 :contentReference[oaicite:9]{index=9})  
   - 2차: **IAB Content Taxonomy** 상위 1개. (콘텐츠 공통어/컨텍스트 분류, 3.0/3.1 안내 :contentReference[oaicite:10]{index=10})  
   - 3차: **AI 커스텀 태그**(Agents, World Models/JEPA, Non-Transformer, Neuro-Symbolic, Infra 등).  
6) **중복/사건 병합**: 제목+링크 해시 1차, 요약 n-gram 유사도 2차 → **근사중복(사건) 그룹**으로 묶어 타임라인화.  
7) **인물 연관처리**: 규칙 매칭 시 해당 인물의 **사업/기술 방향 타임라인**에 누적(연결: 인물↔기술 태그↔기관/소스↔사건).

**출력**
- **홈/분야 탭**: 카드(제목·요약·태그·출처·시간) + “동일 사건 N건” 표시.  
- **스토리(사건) 타임라인**: 최초 보도→후속/해설 흐름.  
- **인물**: 인물별 타임라인 + 연결 그래프(인물–기술–기관–사건 관계).  
- **저장함**: 북마크(URL) + 사용자 태그.  
- **주간 인사이트**: 분야/인물 요약(증감, 테마, 키워드).

### 1.4 분류 체계(서비스 기준)
- **상위 분야 탭(예시)**: Research / Industry / Infra(HW·SW) / Policy·Regulation / Funding·Deals  
- **AI-특화 커스텀 태그(겹침 허용)**:  
  - Agents / Tool-use  
  - World Models / **JEPA**  
  - Non-Transformer (SSM, Mamba 등)  
  - Neuro-Symbolic (예: Apollo-1)  
  - Foundational Models (LMM/멀티모달)  
  - Inference Infra (GPU/ASIC/가속기)  
- **표준 매핑 근거**: IPTC 공식 트리/뉴스코드, IAB Content Taxonomy 공문서. (:contentReference[oaicite:11]{index=11})

### 1.5 인물 트래킹(누적형 지식카드)
- **핵심 인물(초기 세트)**:  
  - David Luan (Amazon, Agents/Nova 등)  
  - Yann LeCun (Meta, **JEPA**)  
  - Andrej Karpathy (Eureka Labs, **NanoChat**)  
  - Llion Jones (Sakana, Non-Transformer 탐색)  
  - AUI / Apollo-1 (Stateful Neuro-Symbolic Reasoning)  
  - (추천) Demis Hassabis, Pieter Abbeel
- **정리 방식**:  
  - 타임라인: 발표(논문/제품/투자/조직/연구 방향) 이벤트 누적  
  - 관계: 인물 ↔ 기술 태그 ↔ 기관/소스 ↔ 사건(기사 묶음)  
  - **사업/기술 방향** 메모: “JEPA 확대”, “Agentic pipeline”, “Non-Transformer 연구” 등 키워드 누적

### 1.6 저장/저작권 정책
- 저장: **제목/짧은 요약/링크/메타/분류/태그/엔티티/관계**만 저장  
- 미보관: 기사 본문/이미지 원본(링크만)  
- 표기: 원문 링크·출처·발행시각 명확 표기  
- 소스: **공식 RSS/블로그**만 사용(예: TechCrunch RSS 이용 약관 명시 :contentReference[oaicite:12]{index=12}, arXiv RSS 공식 운영 :contentReference[oaicite:13]{index=13})

---

## 2) 소스·분야·인물 (실행 세트)

### 2.1 소스(초기 10)  
- TechCrunch – All (RSS)  
- VentureBeat – AI (RSS)  
- MarkTechPost (RSS)  
- WIRED – All (RSS 페이지 제공, 섹션 피드 다수) :contentReference[oaicite:14]{index=14}  
- The Verge – All (RSS 인덱스 경로, RSS 관련 공지/업데이트 다수) :contentReference[oaicite:15]{index=15}  
- IEEE Spectrum – AI (RSS)  
- AITimes – 전체 (RSS)  
- arXiv – cs.AI (RSS, 매일 갱신) :contentReference[oaicite:16]{index=16}  
- OpenAI News (RSS)  
- DeepMind Blog (RSS)

### 2.2 분야(서비스 탭)
- Research / Industry / Infra / Policy·Regulation / Funding·Deals (+ 커스텀 태그 필터)

### 2.3 커스텀 태그 ↔ 표준 매핑(요약)
| 커스텀 | IPTC 예시 | IAB 예시 |
|---|---|---|
| Agents/Tool-use | technology > artificial intelligence | Technology > Computing |
| World Models/JEPA | science & technology > research / AI | Science; Technology |
| Non-Transformer | technology > computing > algorithms | Technology > Computing |
| Neuro-Symbolic | science & technology > AI | Science > Computer Science |
| Foundational Models | technology > AI / data & analytics | Technology > Computing |
| Inference Infra | computing > hardware/semiconductors | Technology > Hardware |
| Policy/Regulation | politics > regulation | News & Politics |
| Funding/Deals | business > finance | Business > Finance |

(표준 근거: IPTC Media Topics, IAB Content Taxonomy 3.x. :contentReference[oaicite:17]{index=17})

### 2.4 인물(초기 워치 규칙)
- **Yann LeCun**: `("JEPA" OR "I-JEPA" OR "V-JEPA") AND (Meta OR LeCun)`  
- **Andrej Karpathy**: `("NanoChat" OR "Eureka Labs" OR "LLM101n")`  
- **David Luan**: `("agentic" OR "Amazon Nova" OR "AGI SF Lab")`  
- **Llion Jones**: `("Sakana AI" AND (model OR paper OR benchmark))`  
- **AUI/Apollo-1**: `("Apollo-1" OR "neuro-symbolic" OR "stateful reasoning")`

---

## 3) 기능 우선순위(백로그)

| 우선 | 기능 | 설명 |
|---:|---|---|
| 1 | **RSS 수집/정규화** | 공식 RSS에서 `title/link/source/published_at/author` 등 메타만 저장 |
| 2 | **요약(1–2문장)** | `description`/일시 로드 기반 자체 요약(본문 폐기) |
| 3 | **자동 분류(표준+커스텀)** | IPTC 1–2 + IAB 1 + 커스텀 태그 추천/확정 |
| 4 | **중복/사건 묶음** | 유사도 기반 근사중복 그룹화 → 타임라인 |
| 5 | **홈/분야 카드 UI** | 분야 탭 + 카드(요약/태그/출처/시간/사건N) |
| 6 | **인물 워치** | 규칙 매칭 → 인물 타임라인/관계 누적 |
| 7 | **저장함/태그** | 북마크(URL) + 사용자 태그 |
| 8 | **주간 인사이트** | 분야/인물 키워드 증감·핵심 이슈 요약 |
| 9 | **OPML Import/Export** | 소스 세트 손쉬운 이관 |
| 10 | **알림(선택)** | 키워드/인물 구독 알림(이메일 등) |

---

## 4) 데이터 스키마(개요)

- **sources**: `id, title, feed_url, site_url, category, lang`  
- **items**: `id, source_id, title, summary_short, link, published_at, author, thumbnail_url, iptc_topics[], iab_categories[], custom_tags[], dup_group_id`  
- **watch_rules**: `id, label, include[], exclude[], priority`  
- **bookmarks**: `id, item_id(or link), title, tags[], note`  

> 기사 본문은 **미보관**. 메타·분류·엔티티/관계만 저장해 **재구성 가능성** 확보.

---

## 5) UI 플로우(와이어)

사용자 접속
├─ 홈(오늘의 브리프)
│ ├─ 상단: 분야 탭(Research / Industry / Infra / Policy / Funding)
│ ├─ 본문: 카드 리스트(제목·요약·태그·출처·시간·사건N)
│ └─ 카드 클릭 → 원문 링크 이동 / "사건 보기" → 타임라인
├─ 분야 탭
│ ├─ 분야 필터/태그 필터
│ └─ 카드 클릭 → 원문/타임라인
├─ 인물(Watch)
│ ├─ 인물 리스트(우선순위/최근 이벤트)
│ └─ 인물 상세 → 타임라인 + 관계 그래프(인물–기술–기관–사건)
├─ 저장함(Saved)
│ └─ 북마크/태그 관리
└─ 설정
├─ 소스(OPML Import/Export)
├─ 인물/키워드 규칙(JSON)
└─ (옵션) 알림 설정


---

## 6) 운영 원칙(요약)
- **법/라이선스**: 원문 미보관, 링크·출처 명시, **공식 RSS**만 사용(TechCrunch RSS 약관 등). :contentReference[oaicite:18]{index=18}  
- **연구 라인**: arXiv RSS는 **매일 0시(EST) 갱신**·주제별 제공 → 하루 1–2회 수집으로 충분. :contentReference[oaicite:19]{index=19}  
- **분류 표준**: IPTC/IAB를 기초로 커스텀 태그 병행 → 확장성/상호운용성 확보. :contentReference[oaicite:20]{index=20}

---

## 7) 후속 작업(바로 실행 가능한 TODO)
1) OPML/JSON(소스·규칙) 임포트 → 수집 시작  
2) IPTC/IAB 코드 테이블/매핑 시트 확정(상위 카테고리부터)  
3) 인물 초기 5명 워치 규칙 등록 → 타임라인 틀 생성  
4) 홈/분야/인물/스토리 4개 화면부터 MVP 릴리즈  
5) 2주간 로그로 **분류 정확도/중복군집 품질** 점검 → 규칙 보정

---
