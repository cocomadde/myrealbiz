# 🏢 포레스타 힐즈 (Foresta Hills) 부동산 투자분석 & 융자 시뮬레이터
### Foresta Hills Real Estate Investment Analysis & Dynamic Loan Simulator

카나가와현 아츠기시 소재 1동 RC 맨션 **「포레스타 힐즈 (Foresta Hills / フォレスタヒルズ)」**(총 14세대, 전실 1DK 30.29㎡)에 대한 전문 수익형 부동산 투자분석 웹 대시보드 및 실시간 은행 대출 시뮬레이터입니다.

---

## 🌟 핵심 기능 (Key Features)

1. **실시간 은행 융자 조건 시뮬레이터 (Dynamic Loan Simulator)**:
   - **조정 매개변수**: 매매가격, LTV(50%~100%), 대출 금리(1.0%~4.5%), 융자기간(15년~35년), 융자 제비용율(0%~3.0%), 취득제비용율(4%~10%), 공실률 시나리오(실적 5.32% / 10% / 0%), 임대료 시나리오(현황 / 만실 / 밸류애드).
   - **실시간 산출 지표**: 월/연간 원리금상환액(ADS), 총 취득소요자금, 필요 자기자본, 순영업소득(NOI), 세전 현금흐름(BTCF), Cap Rate(FCR), 자기자본수익률(CCR), 부채감당률(DSCR), 손익분기 입주율(BER), 론 콘스턴트(K%), 레버리지 판정(Positive / Negative Leverage).

2. **신규 추가 인허가·검사필증·소방·설비 실사 전수 대조 (Legal & Due Diligence Audit)**:
   - **建築確認台帳記載証明書**: **준공검사필증(検査済証) 취득 완벽 확인!** (검사필증번호: H13確済建築厚木 第00313号, 2001년 8월 29일). 위반건축물 리스크 제로 및 금융기관 담보인정비율(LTV) 극대화.
   - **建築計画概要書**: 전국구 임대맨션 전문 건설사 **(주)크라스트(クラスト)** 완공. 대지 741.60㎡(224평), 건폐율 20.18%(지정 60%), 용적률 58.09%(지정 160.4%), 시도 4.01m에 **28.63m 대규모 접도**.
   - **消防用設備等点検結果報告書**: 소화기구·피난기구 전수 양호(良), 지적사항 0건, 아츠기 소방서 정식 수리 완료, 차기 보고 기한 **2028년(令和10년) 10월 말일**까지 유예.
   - **貯水槽清掃 & 水質試験検査報告書**: 옥외 지상 1.3㎥ FRP 수조 청소 완료, 에바라 가압펌프 2대 양호, 일반세균 0, 대장균 불검출, **수도법 수질기준 100% 적합 판정**.
   - **東京電力 電柱敷地料**: 본주 1본(11,125엔) + 지선 2본(22,250엔) = **연간 33,375엔 무위험 부대수입 확정** (매년 4월 입금, NOI 기본 가산 반영).

3. **장기 원금 상환 & 순자산 축적 궤적 (Amortization & Equity Build-Up Chart)**:
   - 30년간의 대출 잔액 감소 곡선과 세입자의 월세로 상환되는 누적 순자산(Equity Build-up)을 Chart.js 시각화.

4. **[금리 × LTV] 25개 셀 감응도 분석 매트릭스 (Sensitivity Heatmap)**:
   - 금리(1.5%~3.5%)와 LTV(60%~100%) 변동에 따른 CCR 및 DSCR의 안전 구간을 색상별 실시간 히트맵 판정.

5. **[모집시기 × 가격대] 2차원 교차 매트릭스 & DOM 분석**:
   - 봄 극성수기 302호(60,000엔 성약, DOM 68일) vs 여름 비수기 305호(61,000엔 95일+ 공실) 실증 비교.
   - 임대료 저항선: 월 63,000엔 (야칭 59,000엔 + 관리비 4,000엔).
   - 305호 가을 전근 직장인 타깃 2,000엔 인하 즉각 처방.

6. **전 14개 호실 렌트롤 포렌식 감사표 (Rent Roll Forensics)**:
   - 호실별 계약일, 거주기간, 직전 DOM, 시세 대비 갭(+8,000~12,000엔) 전수 대조.

7. **완벽한 이중언어 지원 (한국어 ↔ 日本語)**:
   - 원클릭으로 한국어/일본어 UI 및 전문 용어 완벽 전환.

8. **원클릭 인쇄 및 PDF 저장**:
   - `@media print` 최적화로 브라우저에서 즉시 인쇄 또는 고해상도 PDF 보고서 저장 가능.

---

## 🚀 GitHub Pages 배포 가이드 (Deployment Guide)

이 프로젝트는 별도의 빌드 단계(`npm build`, `node` 등)가 전혀 필요 없는 **100% 독립형 SPA(Single Page Application)**로 제작되어, GitHub 저장소에 올리기만 하면 즉시 GitHub Pages로 무료 배포됩니다.

### 방법 1: 신규 GitHub 저장소 생성 및 푸시 (CLI)

```bash
# 1. foresta-hills-web 디렉토리로 이동
cd foresta-hills-web

# 2. 본인의 GitHub 신규 레포지토리 URL을 remote로 추가 (예: foresta-hills-analysis)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git

# 3. main 브랜치로 푸시
git branch -M main
git push -u origin main
```

### 방법 2: GitHub Pages 활성화 (웹 브라우저)

1. GitHub에서 생성한 저장소 페이지로 이동합니다.
2. 상단 메뉴의 **`Settings` (설정)** 탭을 클릭합니다.
3. 좌측 사이드바에서 **`Pages`** 메뉴를 선택합니다.
4. **`Build and deployment` > `Source`** 항목을 **`Deploy from a branch`**로 설정합니다.
5. **`Branch`**를 **`main`** / **`/ (root)`** 로 선택하고 **`Save`**를 누릅니다.
6. 약 1~2분 후, 상단에 배포 완료 알림과 함께 공개 웹사이트 주소가 생성됩니다:
   - `https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPO_NAME>/`

---

## 📊 기술 스택
- **HTML5 / Vanilla JavaScript (ES6+)**
- **Tailwind CSS (CDN)**: 반응형 및 모던 금융 대시보드 UI
- **Chart.js (CDN)**: 대출 잔액 및 순자산 상환 추이 동적 차트
- **Google Fonts**: Pretendard, Noto Sans JP
