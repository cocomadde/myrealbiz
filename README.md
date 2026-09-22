# 🏢 MyRealBiz | 수익형 부동산 투자 분석 & 시뮬레이션 듀얼 포털

일본 수익형 부동산(아파트, RC 맨션, 상가빌딩 등) 매입 타당성 검토, 공문서 실사(검사필증, 소방, 수질, 지적도), 공실/회전율 정밀 분석 및 인터랙티브 융자 금융 시뮬레이션을 관리하는 통합 포트폴리오 저장소입니다.

본 저장소는 **외부공개용 포털(Public)**과 **모아비즈 전용 내부 포털(Moabiz Internal)**의 듀얼 아키텍처로 분리 운영됩니다.

---

### 🌐 포털 접속 링크 (GitHub Pages)

| 포털 구분 | 대상 및 성격 | 라이브 URL | 주요 특징 |
| :--- | :--- | :--- | :--- |
| **🌐 외부공개용 인트로** | 일반/파트너 오픈용 | `https://cocomadde.github.io/myrealbiz/` | 후나바시 제외(3개 물건 노출), 모아비즈 법인 결산서 베이스라인 제외/단품 지표 중심 |
| **🏢 모아비즈 전용 포털** | 모아비즈 법인 내부용 | `https://cocomadde.github.io/myrealbiz/moabiz/` | 후나바시 포함 4개 물건 전수 수록, 모아비즈 4기 결산서 베이스라인 및 9호 판정 완비 |
| **⚙️ 어드민 관리 콘솔** | 외부공개 온오프 관리 | `https://cocomadde.github.io/myrealbiz/moabiz/admin.html` | 물건별 외부공개 스위치(ON/OFF), 실시간 통계, 변경사항 저장 및 Git 배포 명령어 연동 |

---

### 📁 물건별 바로가기

#### 1. 외부공개용 물건 (Public Dossiers)
- **[물건 1] 포레스타 힐즈 (아츠기시)**: [시뮬레이터 & 웹 대시보드](./foresthills/) · [종합분석 보고서](./foresthills/report.html)
- **[물건 2] 익시드 애로우 (마츠도시)**: [시뮬레이터 & 웹 대시보드](./matsudo-kawaharazuka/) · [종합분석 보고서](./matsudo-kawaharazuka/report.html)
- **[물건 3] 크리오 키쿠나 이번관 (요코하마시)**: [시뮬레이터 & 웹 대시보드](./clio-kikuna/) · [종합분석 보고서](./clio-kikuna/report.html)
- **[물건 4] 에어폴크 츠다누마 (후나바시시)**: [시뮬레이터 & 웹 대시보드](./erfolg-tsudanuma/) · [종합분석 보고서](./erfolg-tsudanuma/report.html)

#### 2. 모아비즈 전용 물건 (Moabiz Full Dossiers)
- **[모아비즈 1] 포레스타 힐즈**: [모아비즈 시뮬레이터](./moabiz/foresthills/) · [모아비즈 보고서](./moabiz/foresthills/report.html)
- **[모아비즈 2] 후나바시 미야모토 1초메 (내부전용)**: [모아비즈 시뮬레이터](./moabiz/funabashi-miyamoto/) · [모아비즈 보고서](./moabiz/funabashi-miyamoto/report.html)
- **[모아비즈 3] 익시드 애로우**: [모아비즈 시뮬레이터](./moabiz/matsudo-kawaharazuka/) · [모아비즈 보고서](./moabiz/matsudo-kawaharazuka/report.html)
- **[모아비즈 4] 크리오 키쿠나 이번관**: [모아비즈 시뮬레이터](./moabiz/clio-kikuna/) · [모아비즈 보고서](./moabiz/clio-kikuna/report.html)
- **[모아비즈 5] 에어폴크 츠다누마**: [모아비즈 시뮬레이터](./moabiz/erfolg-tsudanuma/) · [모아비즈 보고서](./moabiz/erfolg-tsudanuma/report.html)

---

## 🔒 보안 및 크롤링·AI 스크래핑 방지 정책 (Anti-Crawling & Anti-AI Scraping)

본 저장소의 모든 부동산 실사 자료 및 보고서는 개인 투자 분석용으로, 외부 검색엔진 노출 및 AI 학습 데이터 수집을 방지하기 위해 다음 2중 차단 체계가 강제 적용되어 있습니다:
1. **`robots.txt`**: 루트 디렉토리에서 모든 검색엔진 크롤러(`User-agent: *`) 및 15개 이상의 상용 AI 봇(`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `Bytespider`, `PerplexityBot` 등)에 대해 전면 접근 차단(`Disallow: /`).
2. **HTML `<meta>` 로봇 태그**: 모든 웹 문서(`<head>`)에 `<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">` 및 `googlebot` 차단 태그 필수 삽입.

---

## 📂 저장소 디렉토리 구조

```text
myrealbiz/
├── index.html                           # [외부공개용] 포트폴리오 인트로 대시보드 (후나바시 제외, 모아비즈 정보 미노출)
├── robots.txt                           # 크롤러 & AI 스크래퍼 전면 차단 정책
├── properties.json                      # 포트폴리오 중앙 데이터베이스 (public_enabled 플래그 탑재)
├── README.md                            # 전체 프로젝트 가이드
├── build_report.py                      # 마크다운 보고서 → 종합분석 보고서(report.html) 빌더
├── publish_to_github.py                 # 듀얼 퍼블리싱 자동화 CLI 스크립트
│
├── moabiz/                              # [모아비즈 전용 내부 포털]
│   ├── index.html                       # 모아비즈 포트폴리오 메인 (후나바시 포함 4건 전수 수록)
│   ├── admin.html                       # 어드민 콘솔 (물건별 외부공개 ON/OFF 제어 및 설정 적용)
│   ├── properties.json                  # 내부 동기화 DB
│   ├── foresthills/                     # 모아비즈 결산서 착지 지표 완비
│   ├── funabashi-miyamoto/              # 내부 전용 물건 (외부 비공개)
│   ├── matsudo-kawaharazuka/            # 모아비즈 결산서 착지 지표 완비
│   ├── clio-kikuna/                     # 모아비즈 결산서 착지 지표 완비
│   └── erfolg-tsudanuma/                # 모아비즈 결산서 착지 지표 완비
│
├── foresthills/                         # [외부공개용 1] 포레스타 힐즈 (모아비즈 정보 제외/정제)
├── matsudo-kawaharazuka/                # [외부공개용 2] 익시드 애로우 (모아비즈 정보 제외/정제)
├── clio-kikuna/                         # [외부공개용 3] 크리오 키쿠나 이번관 (모아비즈 정보 제외/정제)
├── erfolg-tsudanuma/                    # [외부공개용 4] 에어폴크 츠다누마 (모아비즈 정보 제외/정제)
└── funabashi-miyamoto/                  # [외부 리스트 제외] 후나바시 미야모토
```

---

## ⚡ 듀얼 퍼블리싱 CLI 실행 가이드

향후 분석 의뢰하는 모든 부동산은 스크립트를 통해 자동으로 외부공개용과 모아비즈용 두 군데에 동시 배포됩니다:

```bash
# 신규 물건 듀얼 배포 (기본 공개)
python3 publish_to_github.py \
  --slug "foresta-hills" \
  --name-ko "포레스타 힐즈" \
  --report-ko "/path/to/report_KO.md" \
  --metrics "/path/to/metrics.json" \
  --push

# 내부 전용(외부 비공개)으로 발행할 때 (후나바시 유형)
python3 publish_to_github.py \
  --slug "funabashi-miyamoto" \
  --name-ko "후나바시 미야모토 1초메" \
  --private \
  --push

# 특정 물건의 외부 공개 온오프(On/Off) 변경
python3 publish_to_github.py --set-public funabashi-miyamoto off --push
```
