import streamlit as st
import streamlit.components.v1 as components
import datetime

# ── 상수 ─────────────────────────────────────────────────────
ENERGY_CONTENT = {
    "도시가스(LNG)": 42.48,
    "LPG(프로판 1호)": 50.4,
}
DEFAULT_PRICES = {
    "도시가스(LNG)": 21.7,
    "LPG(프로판 1호)": 1405.0,
}
STANDARD_EVAPORATION_RATE = 0.4837
REGULATOR_TABLE = {
    2.8:  (1.0000, 0.4837),
    6.0:  (1.0302, 0.4695),
    10.0: (1.0679, 0.4529),
    15.0: (1.1150, 0.4338),
    20.0: (1.1621, 0.4162),
    25.0: (1.2093, 0.4000),
}

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(page_title="도시가스 전환 경제성 비교", layout="centered")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
footer { display: none !important; }

.report-container {
    width: 100%;
    max-width: 190mm;
    margin: 0 auto;
    padding: 15mm;
    background-color: #ffffff;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    font-family: "맑은 고딕", "Apple SD Gothic Neo", sans-serif;
    color: #222;
    box-sizing: border-box;
}
.report-header { margin-bottom: 18px; text-align: center; }
.report-title-main { font-size: 20pt; font-weight: 800; margin-bottom: 6px; }
.report-title-sub { font-size: 11pt; color: #555; margin-bottom: 12px; }
.report-meta {
    font-size: 10pt; color: #777;
    text-align: right;
    border-bottom: 2px solid #222;
    padding-bottom: 8px;
}

.section-title {
    font-size: 13pt; font-weight: 700;
    margin-top: 20px; margin-bottom: 8px;
    border-left: 5px solid #2d6a4f;
    padding-left: 10px;
}

.styled-table {
    border-collapse: collapse;
    width: 100%;
    font-size: 10.5pt;
    margin-bottom: 14px;
}
.styled-table thead tr {
    background-color: #2d6a4f;
    color: white;
}
.styled-table th, .styled-table td {
    border: 1px solid #e0e0e0;
    padding: 8px 12px;
    text-align: right;
    vertical-align: middle;
}
.styled-table th { font-weight: 600; text-align: center; }
.styled-table td.label {
    text-align: left;
    background-color: #f9fafb;
    font-weight: 600;
    width: 28%;
}
.styled-table td.highlight {
    background-color: #ecfdf5;
    color: #065f46;
    font-weight: 700;
}

.formula-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 10pt;
    color: #374151;
    line-height: 1.9;
    margin-bottom: 14px;
    text-align: left;
}
.formula-box b { color: #2d6a4f; }

.footer-note {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #eee;
    font-size: 9pt;
    color: #888;
    line-height: 1.7;
    text-align: left;
}

@media print {
    @page { size: A4 portrait; margin: 0; }

    section[data-testid="stSidebar"],
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="collapsedControl"],
    footer,
    .stDeployButton { display: none !important; }

    html, body { margin: 0 !important; padding: 0 !important; }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    .block-container {
        padding: 0 !important; margin: 0 !important;
        max-width: 100% !important; width: 100% !important;
    }

    /* 여백을 컨테이너 내부 padding으로 직접 부여 (브라우저 여백 설정과 무관하게 항상 적용) */
    .report-container {
        width: 100% !important;
        max-width: 100% !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 15mm !important;
        border: none !important;
    }

    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }

    /* 한 페이지에 들어가도록 약간 압축 */
    .report-header { margin-bottom: 10px; }
    .report-title-main { font-size: 17pt; }
    .report-title-sub { font-size: 10pt; margin-bottom: 8px; }
    .report-meta { font-size: 9pt; }
    .section-title { font-size: 11.5pt; margin-top: 12px; margin-bottom: 6px; }
    .styled-table { font-size: 9pt; margin-bottom: 10px; }
    .styled-table th, .styled-table td { padding: 5px 10px; }
    .formula-box { font-size: 8.5pt; padding: 8px 12px; line-height: 1.7; margin-bottom: 10px; }
    .footer-note { font-size: 8pt; margin-top: 8px; padding-top: 8px; }

    .styled-table { page-break-inside: avoid; }
    .section-title { page-break-after: avoid; }
    .report-container { page-break-inside: avoid; }
}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 입력 ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 고객 정보 입력")
    st.caption("영업사원 전용 입력 화면입니다.")

    customer_name = st.text_input("고객명 (선택)", placeholder="예: 홍길동 사장님")

    usage_type = st.radio(
        "LPG 사용량 확인 방법",
        ["무게(kg)", "부피(m³)", "요금(원)"],
    )

    if usage_type == "부피(m³)":
        regulator_pressure = st.selectbox(
            "조정기 압력 (kPa)",
            options=list(REGULATOR_TABLE.keys()),
            format_func=lambda x: f"{x} kPa",
        )
        correction, evap_rate = REGULATOR_TABLE[regulator_pressure]
        usage_lpg_m3 = st.number_input(
            "월 LPG 사용량 (m³)", min_value=0.1, value=1.0, step=0.1, format="%.1f"
        )
        lpg_price_per_m3 = st.number_input(
            "m³당 요금 (원/m³)", min_value=0.0, value=3278.0, step=10.0, format="%.0f"
        )
        usage_lpg_kg        = usage_lpg_m3 / evap_rate
        lpg_cost            = usage_lpg_m3 * lpg_price_per_m3
        lpg_unit            = "m³"
        lpg_usage_disp      = f"{usage_lpg_m3:.2f} m³"
        lpg_unit_price      = f"{lpg_price_per_m3:,.0f} 원/m³"
        lpg_energy_per_unit = ENERGY_CONTENT["LPG(프로판 1호)"] / evap_rate
        lpg_mj_price        = lpg_price_per_m3 / lpg_energy_per_unit

    elif usage_type == "무게(kg)":
        evap_rate    = STANDARD_EVAPORATION_RATE
        usage_lpg_kg = st.number_input(
            "월 LPG 사용량 (kg)", min_value=0.1, value=1.0, step=0.1, format="%.1f"
        )
        lpg_price_per_kg = st.number_input(
            "kg당 요금 (원/kg)", min_value=0.0,
            value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.0f"
        )
        lpg_cost            = usage_lpg_kg * lpg_price_per_kg
        lpg_unit            = "kg"
        lpg_usage_disp      = f"{usage_lpg_kg:.2f} kg"
        lpg_unit_price      = f"{lpg_price_per_kg:,.0f} 원/kg"
        lpg_energy_per_unit = ENERGY_CONTENT["LPG(프로판 1호)"]
        lpg_mj_price        = lpg_price_per_kg / lpg_energy_per_unit

    else:
        evap_rate      = STANDARD_EVAPORATION_RATE
        lpg_cost_input = st.number_input(
            "월 LPG 요금 (원)", min_value=1000, value=50000, step=1000, format="%d"
        )
        lpg_price_per_kg = st.number_input(
            "kg당 요금 (원/kg)", min_value=0.0,
            value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.0f"
        )
        usage_lpg_kg        = lpg_cost_input / lpg_price_per_kg
        lpg_cost            = lpg_cost_input
        lpg_unit            = "kg"
        lpg_usage_disp      = f"{usage_lpg_kg:.2f} kg"
        lpg_unit_price      = f"{lpg_price_per_kg:,.0f} 원/kg"
        lpg_energy_per_unit = ENERGY_CONTENT["LPG(프로판 1호)"]
        lpg_mj_price        = lpg_price_per_kg / lpg_energy_per_unit

    st.markdown("---")
    gas_mj_price = st.number_input(
        "도시가스 단가 (원/MJ)", min_value=0.0,
        value=float(DEFAULT_PRICES["도시가스(LNG)"]), format="%.2f"
    )
    gas_install_cost = st.number_input(
        "도시가스 공사비 (원)", min_value=0, value=3000000, step=100000, format="%d"
    )

    # ── 인쇄 버튼 (사이드바 안) ──
    st.markdown("---")
    st.markdown("### 🖨 보고서 인쇄")
    components.html(
        """
        <style>
            .print-btn {
                width: 100%;
                background-color: #2d6a4f;
                color: white;
                border: none;
                padding: 12px 0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                font-family: "맑은 고딕", sans-serif;
            }
            .print-btn:hover { background-color: #1a5c38; }
        </style>
        <button class="print-btn" onclick="window.top.print()">🖨️ 인쇄 / PDF 저장</button>
        """,
        height=60,
    )

# ── 계산 ─────────────────────────────────────────────────────
usage_mj        = usage_lpg_kg * ENERGY_CONTENT["LPG(프로판 1호)"]
gas_cost        = usage_mj * gas_mj_price
monthly_savings = lpg_cost - gas_cost
annual_savings  = monthly_savings * 12
cost_ratio_pct  = (lpg_mj_price / gas_mj_price * 100) if gas_mj_price > 0 else 0
payback_months  = (gas_install_cost / monthly_savings) if monthly_savings > 0 else None
today           = datetime.date.today().strftime("%Y년 %m월 %d일")
payback_str     = f"{payback_months:.1f} 개월" if payback_months else "회수 불가"

# ── 헤더 메타 조립 ────────────────────────────────────────────
meta_lines = []
if customer_name:
    meta_lines.append(f"고객명: <strong>{customer_name} 고객님</strong>")
meta_lines.append(f"보고서 생성일: {today}")
meta_lines.append("대성에너지(주)")
meta_html = "<br>".join(meta_lines)

# ── 메인 리포트 ───────────────────────────────────────────────
report_html = f"""
<div class="report-container">

<div class="report-header">
    <div class="report-title-main">도시가스 전환 경제성 비교표</div>
    <div class="report-title-sub">LPG → 도시가스(LNG) 전환 시 절약 효과 분석</div>
    <div class="report-meta">{meta_html}</div>
</div>

<div class="section-title">1. 경제성 비교표</div>
<table class="styled-table">
    <thead>
        <tr>
            <th style="text-align:left; width:28%">항목</th>
            <th>LPG(프로판 1호)</th>
            <th>도시가스(LNG)</th>
        </tr>
    </thead>
    <tbody>
        <tr><td class="label">단위</td><td>{lpg_unit}</td><td>MJ</td></tr>
        <tr><td class="label">단위당 가격</td><td>{lpg_unit_price}</td><td>{gas_mj_price:.2f} 원/MJ</td></tr>
        <tr><td class="label">기준열량</td><td>{lpg_energy_per_unit:.2f} MJ/{lpg_unit}</td><td>{ENERGY_CONTENT["도시가스(LNG)"]:.2f} MJ/m³</td></tr>
        <tr><td class="label">열량당 가격</td><td>{lpg_mj_price:.2f} 원/MJ</td><td>{gas_mj_price:.2f} 원/MJ</td></tr>
        <tr><td class="label">월 사용량</td><td>{lpg_usage_disp}</td><td>{usage_mj:,.2f} MJ</td></tr>
        <tr><td class="label">총 열량</td><td>{usage_mj:,.2f} MJ</td><td>{usage_mj:,.2f} MJ</td></tr>
        <tr><td class="label">월 예상 요금</td><td class="highlight">{lpg_cost:,.0f} 원</td><td class="highlight">{gas_cost:,.0f} 원</td></tr>
        <tr><td class="label">도시가스 기준 비율</td><td>{cost_ratio_pct:.2f}%</td><td>100%</td></tr>
    </tbody>
</table>

<div class="formula-box">
0. <b>기준열량</b> = 에너지기본법 시행규칙 별표 에너지열량 환산기준(제5조제1항 관련)<br>
1. <b>열량당 가격(원/MJ)</b> = 단위당 가격 ÷ 기준열량<br>
2. <b>월 사용량</b> = 총 열량 ÷ 기준열량<br>
3. <b>총 열량(MJ)</b> = LPG 사용량({lpg_unit}) × 기준열량({lpg_energy_per_unit:.2f} MJ/{lpg_unit})<br>
4. <b>월 예상 요금</b> = 총 열량(MJ) × 열량당 가격(원/MJ)<br>
5. <b>도시가스 기준 비율</b> = (LPG 열량당 가격 ÷ 도시가스 열량당 가격) × 100
</div>

<div class="section-title">2. 공사비 회수 기간 산정</div>
<table class="styled-table">
    <thead>
        <tr>
            <th style="text-align:left; width:28%">항목</th>
            <th>금액</th>
        </tr>
    </thead>
    <tbody>
        <tr><td class="label">초기 공사비</td><td>{gas_install_cost:,.0f} 원</td></tr>
        <tr><td class="label">월 절약금액</td><td class="highlight">{monthly_savings:,.0f} 원</td></tr>
        <tr><td class="label">연간 절약금액</td><td>{annual_savings:,.0f} 원</td></tr>
        <tr><td class="label">공사비 회수기간</td><td class="highlight">{payback_str}</td></tr>
    </tbody>
</table>

<div class="formula-box">
이 계산기는 LPG와 도시가스의 경제성을 비교하기 위해 다음 공식을 사용합니다.<br>
1. <b>발열량 기준 비용 계산:</b> 연료비 = 총 열량(MJ) × 열량당 가격(원/MJ)<br>
2. <b>절약 금액:</b> 절약금액 = LPG 요금 − 도시가스 요금<br>
3. <b>공사비 회수 기간:</b> 회수기간(개월) = 도시가스 공사비 ÷ 월 절약금액
</div>

<div class="footer-note">
※ 본 계산서는 현재 LPG 사용량 기준이며, 실제 절약금액은 사용 패턴에 따라 달라질 수 있습니다.<br>
※ 도시가스 단가 기준: 대성에너지(주) 도시가스 공급규정 적용 &nbsp;|&nbsp; {today} 기준
</div>

</div>
"""

st.markdown(report_html, unsafe_allow_html=True)