import streamlit as st

# ── 상수 ─────────────────────────────────────────────────────────────────────
ENERGY_CONTENT = {
    "도시가스(LNG)": 42.48,   # MJ/m³  ← 출처: 대성에너지 도시가스 공급규정
    "LPG(프로판 1호)": 50.4,  # MJ/kg  ← 출처: 에너지기본법 시행규칙 별표
}
DEFAULT_PRICES = {
    "도시가스(LNG)": 21.7,
    "LPG(프로판 1호)": 1405.0,
}
STANDARD_EVAPORATION_RATE = 0.4837  # 대구·대전·울산·경북·경남 영남지역 표준 기화율

# 조정기 압력별 보정계수 및 기화율
REGULATOR_TABLE = {
    #  kPa : (보정계수,  기화율)
    2.8:  (1.0000, 0.4837),
    6.0:  (1.0302, 0.4695),
    10.0: (1.0679, 0.4529),
    15.0: (1.1150, 0.4338),
    20.0: (1.1621, 0.4162),
    25.0: (1.2093, 0.4000),
}
REGULATOR_CORRECTION = {k: v[0] for k, v in REGULATOR_TABLE.items()}


# ── 카드 렌더 헬퍼 ────────────────────────────────────────────────────────────
def card(label: str, value: str, sub: str = "", color: str = "#1e3a8a",
         bg: str = "#eff6ff", border: str = "#2563eb", height: int = 88):
    sub_html = f"<div style='font-size:11px;color:{color};opacity:0.85;margin-top:3px;line-height:1.4;word-break:keep-all'>{sub}</div>" if sub else ""
    st.markdown(f"""
<div style='background:{bg};border:1.5px solid {border};border-radius:10px;
            padding:10px 8px;text-align:center;
            min-height:{height}px;display:flex;flex-direction:column;
            justify-content:center;align-items:center;box-sizing:border-box'>
  <div style='font-size:12px;font-weight:600;color:{color};line-height:1.3;word-break:keep-all'>{label}</div>
  <div style='font-size:15px;font-weight:700;color:{color};margin-top:3px;line-height:1.3;word-break:break-all'>{value}</div>
  {sub_html}
</div>""", unsafe_allow_html=True)


def op(symbol: str, height: int = 90):
    st.markdown(f"""
<div style='height:{height}px;display:flex;align-items:center;
            justify-content:center;font-size:20px;color:#9ca3af;font-weight:300'>
  {symbol}
</div>""", unsafe_allow_html=True)


def arrow_down():
    st.markdown("<div style='text-align:center;font-size:20px;color:#cbd5e1;padding:2px 0'>↓</div>",
                unsafe_allow_html=True)


def arrow_right_center():
    st.markdown("<div style='text-align:center;font-size:20px;color:#9ca3af;line-height:2'>→</div>",
                unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f"<div style='font-size:14px;font-weight:700;color:#374151;margin:8px 0 4px'>{text}</div>",
                unsafe_allow_html=True)


def section_caption(text: str):
    st.markdown(f"<div style='font-size:12px;color:#6b7280;margin-bottom:8px'>{text}</div>",
                unsafe_allow_html=True)


# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="도시가스 vs LPG 비교", layout="wide")
st.title("도시가스 vs LPG 경제성 비교")

# ── 사이드바 입력 ─────────────────────────────────────────────────────────────
st.sidebar.header("입력 값 설정")
st.sidebar.caption("현재 LPG 사용 현황을 입력해주세요.")

usage_type = st.sidebar.radio(
    "LPG 사용량을 어떻게 알고 계세요?",
    ["무게(kg)로 알아요", "부피(m³)로 알아요", "요금(원)으로 알아요"],
    help="영수증이나 계량기에서 확인할 수 있어요."
)

if usage_type == "부피(m³)로 알아요":
    regulator_pressure = st.sidebar.selectbox(
        "조정기 압력 (kPa)",
        options=list(REGULATOR_TABLE.keys()),
        format_func=lambda x: f"{x} kPa"
    )
    correction, evap_rate = REGULATOR_TABLE[regulator_pressure]

    usage_lpg_m3 = st.sidebar.number_input(
        "한 달에 몇 m³ 사용하세요?",
        min_value=0.1, value=1.0, step=0.1, format="%.1f",
        help="계량기 또는 영수증에서 확인하세요."
    )
    lpg_price_per_m3 = st.sidebar.number_input(
        "m³당 요금이 얼마예요? (원/m³)",
        min_value=0.0, value=3278.0, step=10.0, format="%.0f",
        help="영수증의 '단가' 항목을 확인하세요."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📋 기화율 기준** (열량 환산용)")
    st.sidebar.markdown(f"""
| 항목 | 값 |
|------|-----|
| 표준 기화율 | {STANDARD_EVAPORATION_RATE} m³/kg |
| 보정계수 ({regulator_pressure} kPa) | {correction} |
| **실제 기화율** | **{evap_rate} m³/kg** |
""")
    st.sidebar.caption("출처: 대전·대구·울산광역시, 경북·경남 영남지역 기준")

    # ── m³ 모드 계산 ──
    lpg_cost         = usage_lpg_m3 * lpg_price_per_m3          # 단순화: m³ × 원/m³
    usage_lpg_kg     = usage_lpg_m3 / evap_rate                  # 열량 환산용: m³ ÷ 기화율(m³/kg) = kg
    lpg_usage_display = f"{usage_lpg_m3:.1f} m³"

elif usage_type == "무게(kg)로 알아요":
    st.sidebar.markdown("💡 LPG 용기나 영수증에서 kg 단위를 확인할 수 있어요.")
    usage_lpg_kg = float(st.sidebar.number_input(
        "한 달에 몇 kg 사용하세요?",
        min_value=1, value=20, step=1, format="%d"
    ))
    lpg_price = st.sidebar.number_input(
        "kg당 요금이 얼마예요? (원/kg)",
        min_value=0.0, value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.0f",
        help="영수증의 kg당 단가를 입력하세요."
    )
    lpg_cost          = usage_lpg_kg * lpg_price
    lpg_usage_display = f"{usage_lpg_kg:.0f} kg"

else:  # 요금으로 알아요
    st.sidebar.markdown("💡 한 달 LPG 요금 고지서 금액을 입력해주세요.")
    usage_cost = float(st.sidebar.number_input(
        "한 달 LPG 요금이 얼마예요? (원)",
        min_value=1000, value=50000, step=1000, format="%d"
    ))
    lpg_price = st.sidebar.number_input(
        "kg당 요금이 얼마예요? (원/kg)",
        min_value=0.0, value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.0f",
        help="단가를 모르시면 공급업체에 문의하세요. 보통 2,000~3,000원/kg 수준이에요."
    )
    usage_lpg_kg      = usage_cost / lpg_price
    lpg_cost          = usage_cost
    lpg_usage_display = f"{usage_cost:,.0f} 원 → {usage_lpg_kg:.1f} kg"

gas_mj_price     = st.sidebar.number_input("도시가스 가격 (원/MJ)", min_value=0.0, value=float(DEFAULT_PRICES["도시가스(LNG)"]), format="%.2f")
gas_install_cost = st.sidebar.number_input("도시가스 초기 공사비 (원)", min_value=1000000, value=3000000, step=100000, format="%d")

# ── 공통 계산 ─────────────────────────────────────────────────────────────────
usage_gj        = usage_lpg_kg * ENERGY_CONTENT["LPG(프로판 1호)"]  # LPG → MJ
gas_cost        = usage_gj * gas_mj_price
monthly_savings = lpg_cost - gas_cost
payback_period  = (gas_install_cost / monthly_savings) if monthly_savings > 0 else float("inf")
cost_ratio      = (lpg_cost / gas_cost - 1) * 100

# ── 결과 배너 ─────────────────────────────────────────────────────────────────
if gas_cost < lpg_cost:
    st.success(f"✅ 도시가스가 LPG보다 **{abs(cost_ratio):.1f}%** 더 경제적입니다!")
else:
    st.warning(f"⚠️ LPG가 도시가스보다 **{abs(cost_ratio):.1f}%** 더 저렴합니다.")

st.markdown("#### 계산 흐름도")
st.caption("사이드바에서 값을 바꾸면 즉시 업데이트됩니다.")

H = 88

# ════════════════════════════════════════════════════════════
# STEP 1-A (m³ 전용) — m³ → kg 환산 (열량 계산용)
# ════════════════════════════════════════════════════════════
if usage_type == "부피(m³)로 알아요":
    section_title("① LPG 부피(m³) → 무게(kg) 환산 (열량 계산용)")
    section_caption("도시가스와 동일한 열량(MJ) 기준으로 비교하기 위해 m³ → kg으로 환산합니다. 요금 계산에는 영향을 주지 않아요.")

    c1, cx, c2, ce, c3, _, c_note = st.columns([3, 1, 3, 1, 3, 0.3, 5])
    with c1:
        card("LPG 사용량", f"{usage_lpg_m3:.1f} m³",
             color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
    with cx:
        op("÷", H)
    with c2:
        card("기화율", f"{evap_rate} m³/kg",
             sub=f"조정기 {regulator_pressure} kPa 기준",
             color="#065f46", bg="#f0fdf4", border="#16a34a", height=H)
    with ce:
        op("=", H)
    with c3:
        card("LPG 무게", f"{usage_lpg_kg:.3f} kg",
             sub=f"{usage_lpg_m3:.1f} m³ ÷ {evap_rate}",
             color="#065f46", bg="#f0fdf4", border="#16a34a", height=H)
    with c_note:
        st.markdown(f"""
<div style='height:{H}px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
            padding:10px 12px;font-size:11.5px;color:#475569;box-sizing:border-box;
            display:flex;flex-direction:column;justify-content:center'>
  <b>기화율이란?</b> LPG 1 kg이 기화했을 때의 부피(m³).<br>
  m³ ÷ 기화율 = kg (부피 → 무게 환산).<br>
  <span style='color:#64748b'>표준 {STANDARD_EVAPORATION_RATE} ÷ 보정계수 {correction} = <b>{evap_rate} m³/kg</b></span>
</div>""", unsafe_allow_html=True)

    arrow_down()

# ════════════════════════════════════════════════════════════
# STEP 1-B — kg → MJ 열량 환산
# ════════════════════════════════════════════════════════════
step_b = "②" if usage_type == "부피(m³)로 알아요" else "①"
section_title(f"{step_b} LPG 무게(kg) → 열량(MJ) 환산")
section_caption("LPG 1 kg을 완전 연소하면 50.4 MJ의 열이 발생해요. 도시가스와 같은 기준(MJ)으로 비교하기 위해 환산합니다.")

c1, cx, c2, ce, c3 = st.columns([3, 1, 4, 1, 4])
with c1:
    card("LPG 무게",
         f"{usage_lpg_kg:.3f} kg" if usage_type == "부피(m³)로 알아요" else lpg_usage_display,
         color="#065f46" if usage_type == "부피(m³)로 알아요" else "#9f1239",
         bg="#f0fdf4" if usage_type == "부피(m³)로 알아요" else "#fff1f2",
         border="#16a34a" if usage_type == "부피(m³)로 알아요" else "#e11d48",
         height=H)
with cx:
    op("×", H)
with c2:
    card("LPG 기준열량", "50.4 MJ/kg",
         sub="에너지기본법 시행규칙 별표",
         color="#92400e", bg="#fffbeb", border="#d97706", height=H)
with ce:
    op("=", H)
with c3:
    card("총 열량", f"{usage_gj:,.1f} MJ",
         sub=f"{usage_lpg_kg:.3f} kg × 50.4 MJ/kg",
         color="#78350f", bg="#fef3c7", border="#f59e0b", height=H)

arrow_down()

# ════════════════════════════════════════════════════════════
# STEP 2 — 동일 열량 기준 요금 계산
# ════════════════════════════════════════════════════════════
step2_num = "③" if usage_type == "부피(m³)로 알아요" else "②"
step3_num = "④" if usage_type == "부피(m³)로 알아요" else "③"

section_title(f"{step2_num} 동일 열량 기준 요금 계산")

lpg_col, mid_col, gas_col = st.columns([10, 1, 10])

with lpg_col:
    st.markdown("<div style='text-align:center;font-size:13px;font-weight:600;color:#be123c;margin-bottom:6px'>🔴 LPG (현재)</div>",
                unsafe_allow_html=True)
    if usage_type == "부피(m³)로 알아요":
        # ← 단순화: m³ × m³당 단가
        c1, cx, c2, ce, c3 = st.columns([3, 1, 3, 1, 4])
        with c1:
            card("사용량", f"{usage_lpg_m3:.1f} m³",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
        with cx: op("×", H)
        with c2:
            card("m³당 단가", f"{lpg_price_per_m3:,.0f} 원/m³",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
        with ce: op("=", H)
        with c3:
            card("LPG 요금", f"{lpg_cost:,.0f} 원",
                 sub=f"{usage_lpg_m3:.1f} m³ × {lpg_price_per_m3:,.0f} 원/m³",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
    else:
        c1, cx, c2, ce, c3 = st.columns([3, 1, 3, 1, 4])
        with c1:
            card("사용량", f"{usage_lpg_kg:.2f} kg",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
        with cx: op("×", H)
        with c2:
            card("단가", f"{lpg_price:,.0f} 원/kg",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)
        with ce: op("=", H)
        with c3:
            card("LPG 요금", f"{lpg_cost:,.0f} 원",
                 color="#9f1239", bg="#fff1f2", border="#e11d48", height=H)

with mid_col:
    st.markdown(f"""
<div style='height:{H}px;display:flex;align-items:center;justify-content:center'>
  <div style='text-align:center;background:#fef9c3;border:1.5px solid #ca8a04;
              border-radius:10px;padding:8px 4px;font-size:11px;color:#78350f;font-weight:600;line-height:1.5'>
    같은<br>열량<br>{usage_gj:.0f}<br>MJ
  </div>
</div>""", unsafe_allow_html=True)

with gas_col:
    st.markdown("<div style='text-align:center;font-size:13px;font-weight:600;color:#1d4ed8;margin-bottom:6px'>🔵 도시가스 (전환 후)</div>",
                unsafe_allow_html=True)
    c1, cx, c2, ce, c3 = st.columns([3, 1, 3, 1, 4])
    with c1:
        card("총 열량", f"{usage_gj:,.1f} MJ",
             sub=f"{usage_lpg_kg:.3f} kg × 50.4 MJ/kg",
             color="#1e3a8a", bg="#eff6ff", border="#2563eb", height=H)
    with cx: op("×", H)
    with c2:
        card("도시가스 단가", f"{gas_mj_price:.2f} 원/MJ",
             sub="사이드바 입력값",
             color="#1e3a8a", bg="#eff6ff", border="#2563eb", height=H)
    with ce: op("=", H)
    with c3:
        card("도시가스 요금", f"{gas_cost:,.0f} 원",
             sub=f"{usage_gj:,.1f} MJ × {gas_mj_price:.2f} 원/MJ",
             color="#1e3a8a", bg="#eff6ff", border="#2563eb", height=H)

# m³ 전용: MJ당 단가 참고용 뱃지
if usage_type == "부피(m³)로 알아요":
    lpg_price_per_kg_ref = lpg_price_per_m3 / (usage_lpg_kg / usage_lpg_m3) if usage_lpg_m3 > 0 else 0
    lpg_mj_price_calc    = lpg_price_per_kg_ref / ENERGY_CONTENT["LPG(프로판 1호)"]
    diff_pct = (lpg_mj_price_calc / gas_mj_price - 1) * 100
    diff_txt = f"LPG가 {diff_pct:.1f}% 더 {'비쌈' if diff_pct > 0 else '저렴'}"
    st.markdown(f"""
<div style='background:#fef9c3;border:1px solid #ca8a04;border-radius:8px;
            padding:9px 16px;margin-top:8px;font-size:12.5px;color:#78350f'>
  💡 <b>MJ당 단가 참고:</b>
  LPG {lpg_mj_price_calc:.2f} 원/MJ &nbsp;vs&nbsp; 도시가스 {gas_mj_price:.2f} 원/MJ
  &nbsp;→&nbsp; <b>{diff_txt}</b>
</div>""", unsafe_allow_html=True)

arrow_down()

# ════════════════════════════════════════════════════════════
# STEP 3 — 절약금액
# ════════════════════════════════════════════════════════════
section_title(f"{step3_num} 요금 비교")
if monthly_savings > 0:
    savings_label = f"월 {monthly_savings:,.0f} 원 절약"
    savings_sub   = f"{lpg_cost:,.0f} 원 − {gas_cost:,.0f} 원"
    s_bg, s_border, s_color = "#d1fae5", "#059669", "#065f46"
else:
    savings_label = f"월 {abs(monthly_savings):,.0f} 원 손실"
    savings_sub   = f"{lpg_cost:,.0f} 원 − {gas_cost:,.0f} 원"
    s_bg, s_border, s_color = "#fee2e2", "#dc2626", "#991b1b"

card("💰 도시가스 전환 시 월 절약 금액",
     savings_label, sub=savings_sub,
     color=s_color, bg=s_bg, border=s_border, height=80)

arrow_down()

# ════════════════════════════════════════════════════════════
# STEP 4 — 공사비 회수
# ════════════════════════════════════════════════════════════
c1, ca, c2 = st.columns([4, 1, 8])
with c1:
    card("초기 공사비", f"{gas_install_cost:,.0f} 원",
         color="#374151", bg="#f3f4f6", border="#9ca3af", height=H)
with ca:
    op("→", H)
with c2:
    pb = f"{payback_period:.1f} 개월" if monthly_savings > 0 else "회수 불가"
    pb_sub = f"{gas_install_cost:,.0f} 원 ÷ {monthly_savings:,.0f} 원/월" if monthly_savings > 0 else "도시가스 전환 시 비용이 더 높음"
    card("🔮 공사비 회수 기간", pb, sub=pb_sub,
         color="#5b21b6", bg="#faf5ff", border="#7c3aed", height=H)

# ════════════════════════════════════════════════════════════
# 하단 출처
# ════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📌 발열량 기준 출처"):
    st.markdown("""
| 연료 | 기준열량 | 출처 |
|------|----------|------|
| 도시가스(LNG) | **42.48 MJ/m³** | 대성에너지 도시가스 공급규정 |
| LPG(프로판 1호) | **50.4 MJ/kg** | 에너지기본법 시행규칙 별표 (에너지열량 환산기준) |
    """)