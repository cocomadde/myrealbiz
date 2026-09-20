# 🏢 MyRealBiz | 수익형 부동산 투자 분석 & 시뮬레이션 포트폴리오

일본 수익형 부동산(아파트, RC 맨션, 상가빌딩 등) 매입 타당성 검토, 공문서 실사(검사필증, 소방, 수질, 지적도), 공실/회전율 정밀 분석 및 인터랙티브 융자 금융 시뮬레이션을 관리하는 통합 포트폴리오 저장소입니다.

---

## 🌐 라이브 웹 대시보드 (GitHub Pages)

GitHub Pages 배포 후 다음 링크를 통해 웹 브라우저 및 모바일에서 바로 접속하여 금융 시뮬레이션을 조작할 수 있습니다:

- **포트폴리오 메인 허브**: `https://cocomadde.github.io/myrealbiz/`
- **[물건 1] 포레스타 힐즈 대시보드**: `https://cocomadde.github.io/myrealbiz/foresthills/`

---

## 📂 저장소 디렉토리 구조 (물건별 독립 관리)

앞으로 검토하는 모든 물건은 독립된 서브디렉토리로 관리되어, 새로운 물건이 추가되어도 기존 분석에 영향을 주지 않고 지속 확장 가능합니다.

```text
myrealbiz/
├── index.html                           # 포트폴리오 메인 허브 웹 랜딩 페이지
├── README.md                            # 전체 프로젝트 가이드
│
└── foresthills/                         # [물건 1] 지바현 야치요시 포레스타 힐즈 (RC 14세대)
    ├── index.html                       # 실시간 융자 시뮬레이터 & 웹 대시보드 (SPA)
    ├── README.md                        # 물건 상세 개요 및 지표 요약
    ├── Foresta_Hills_Investment_Report_KO.md        # 종합 투자분석 실사 보고서 (한국어)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis.md  # 공실 및 회전율 정밀 분석 보고서 (한국어)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis_JA.md  # 空室・回転率分析レポート (日本語)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis_KO.pdf # 인쇄용 공실/회전율 분석 PDF (KO)
    └── Foresta_Hills_Vacancy_Turnover_Analysis_JA.pdf # 印刷用 空室・回転率分析 PDF (JA)
```

---

## 🏛️ 등록 물건 1: 포레스타 힐즈 (Foresta Hills)

- **소재지**: 일본 지바현 야치요시 요나모토 (八千代市 米本) / 토요소쿠선 야치요츄오역
- **구조/규모**: 철근콘크리트(RC)조 지상 3층 / 14세대 (1K 8호 + 2DK 6호) + 전용 주차장 8대
- **매매 희망가**: **8,700만 엔** (표면 수익률 **10.36%**, 실질 NOI 수익률 **8.25%**)
- **핵심 실사 결과**:
  1. **준공검사필증 100% 완비**: 건축확인대장 기재증명서 확인 (H13確済 第00313호, 2001년 8월 준공) → 일본 1금융권 담보대출 적격.
  2. **도로 접도 요건**: 4.01m 공도에 28.63m 광폭 접도 (재건축 규제 위험 전무).
  3. **소방/수질/수조**: 소방설비 점검 양호(결함 0건), FRP 1.3㎥ 저수조 및 직결 증압펌프 정상, 수질 적합.
  4. **전신주 부지 임대료**: 도쿄전력 연 33,375엔 (전주 1기 + 지선 2조) 매년 4월 안정 입금.

---

## ⚙️ GitHub Pages 배포 설정 (최초 1회)

1. 본 GitHub 저장소(`myrealbiz`) 상단의 **Settings** 탭으로 이동합니다.
2. 좌측 메뉴의 **Pages**를 클릭합니다.
3. **Build and deployment** 섹션에서:
   - **Source**: `Deploy from a branch` 선택
   - **Branch**: `main`, 폴더는 `/(root)` 선택 후 **Save** 클릭
4. 약 1~2분 후 배포가 완료되면 `https://cocomadde.github.io/myrealbiz/` 주소로 접속 가능합니다!

---

## ➕ 새로운 물건 추가 방법

새로운 물건을 분석할 때는 저장소 루트에 영문 물건명으로 폴더를 만들고 분석 자료를 추가하면 됩니다:

```bash
# 1. 새 물건 폴더 생성 (예: tokyo-ap)
mkdir tokyo-ap

# 2. 해당 폴더에 index.html 및 분석 보고서 추가
# 3. 루트 index.html에 카드 링크 추가 후 git commit & push
```
