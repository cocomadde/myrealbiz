# 🏢 MyRealBiz | 수익형 부동산 투자 분석 & 시뮬레이션 포트폴리오

일본 수익형 부동산(아파트, RC 맨션, 상가빌딩 등) 매입 타당성 검토, 공문서 실사(검사필증, 소방, 수질, 지적도), 공실/회전율 정밀 분석 및 인터랙티브 융자 금융 시뮬레이션을 관리하는 통합 포트폴리오 저장소입니다.

---

## 🌐 라이브 웹 대시보드 (GitHub Pages)

GitHub Pages 배포 후 다음 링크를 통해 웹 브라우저 및 모바일에서 바로 접속하여 금융 시뮬레이션을 조작할 수 있습니다:

- **포트폴리오 메인 허브**: `https://cocomadde.github.io/myrealbiz/`
- **[물건 1] 포레스타 힐즈 대시보드**: `https://cocomadde.github.io/myrealbiz/foresthills/`
- **[물건 1] 종합 투자분석 보고서**: `https://cocomadde.github.io/myrealbiz/foresthills/report.html`

---

## 📂 저장소 디렉토리 구조 (물건별 독립 관리)

앞으로 검토하는 모든 물건은 독립된 서브디렉토리로 관리되어, 새로운 물건이 추가되어도 기존 분석에 영향을 주지 않고 지속 확장 가능합니다.

```text
myrealbiz/
├── index.html                           # 포트폴리오 메인 허브 웹 랜딩 페이지 (KO/JA)
├── README.md                            # 전체 프로젝트 가이드
│
└── foresthills/                         # [물건 1] 카나가와현 아츠기시 포레스타 힐즈 (RC조 4층 14세대)
    ├── index.html                       # 실시간 융자 시뮬레이터 & 웹 대시보드 (KO/JA)
    ├── report.html                      # 종합 투자분석 보고서 웹 열람판 (목차·차트·수식)
    ├── README.md                        # 물건 상세 개요 및 지표 요약
    ├── Foresta_Hills_Investment_Report_KO.md        # 종합 투자분석 보고서 원본 (마크다운)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis.md   # 공실 및 회전율 정밀 분석 보고서 (한국어)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis_JA.md  # 空室・回転率分析レポート (日本語)
    ├── Foresta_Hills_Vacancy_Turnover_Analysis_KO.pdf # 인쇄용 공실/회전율 분석 PDF (KO)
    └── Foresta_Hills_Vacancy_Turnover_Analysis_JA.pdf # 印刷用 空室・回転率分析 PDF (JA)
```

> [!NOTE]
> `report.html`은 `Foresta_Hills_Investment_Report_KO.md`를 빌드 시점에 변환해 생성한 정적 페이지입니다.
> 원본 마크다운을 수정한 뒤에는 변환을 다시 실행해 `report.html`을 갱신해야 합니다.

---

## 🏛️ 등록 물건 1: 포레스타 힐즈 (Foresta Hills)

- **소재지**: 일본 카나가와현 아츠기시 이이야마미나미 4초메 (神奈川県厚木市飯山南四丁目) / 오다큐 오다와라선 「본아츠기(本厚木)」역 버스 약 20분, 정류장 「局前」 도보 1분
- **구조/규모**: 철근콘크리트(RC)조 지상 4층 / 14세대 (전실 1DK 30.29㎡) + 옥외 자주식 주차장 14대
- **준공**: 2001년(平成13년) 9월 (만 25년 경과)
- **토지/연면적**: 대지 741.63㎡ (224.34평) / 연면적 451.42㎡ (건폐율 20.18%, 용적률 58.09%)
- **매도자 희망가**: **1억 2,300만 엔** (만실 상정 표면수익률 **8.60%**, 현황 **7.75%**, NOI 수익률 **6.35%**)
- **권장 협상 목표가**: 8,800만 ~ 1억 엔 (사시네 전략)
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
