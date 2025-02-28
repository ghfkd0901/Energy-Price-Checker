import streamlit as st
import pandas as pd

# 기본 설정: 발열량 (MJ 단위)
ENERGY_CONTENT = {
    "도시가스(LNG)": 43.1,  # MJ per Nm³
    "LPG(프로판 1호)": 50.4  # MJ per kg
}

# 표준 기화율 및 조정기 보정계수
STANDARD_EVAPORATION_RATE = 0.4837
REGULATOR_CORRECTION = {
    2.8: 1.000,
    6.0: 1.0307,
    10.0: 1.0692
}

# 기본 가격 (사용자 수정 가능)
DEFAULT_PRICES = {
    "도시가스(LNG)": 21.7,  # 원/MJ
    "LPG(프로판 1호)": 2500.0  # 원/kg
}

st.title("도시가스 vs LPG 비교")

# 사이드바 입력
st.sidebar.header("입력 값 설정")
usage_type = st.sidebar.radio("사용량 입력 방식", ["Kg 단위", "m³ 단위", "금액 단위"])

if usage_type == "m³ 단위":
    regulator_pressure = st.sidebar.selectbox("조정기 압력 선택 (kPa)", options=[2.8, 6.0, 10.0])
    st.sidebar.markdown(f"**표준 기화율:** {STANDARD_EVAPORATION_RATE}")
    st.sidebar.markdown(f"**현재 선택된 조정기 보정계수:** {REGULATOR_CORRECTION[regulator_pressure]}")
    
    usage_lpg_m3 = st.sidebar.number_input("사용할 LPG량 (m³)", min_value=0.1, value=5.0, step=0.1, format="%.1f")
    lpg_price = st.sidebar.number_input("LPG(프로판 1호) 가격 (원/kg)", min_value=0.0, value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.2f")
    usage_lpg_kg = usage_lpg_m3 * STANDARD_EVAPORATION_RATE / REGULATOR_CORRECTION[regulator_pressure]
    usage_gj = usage_lpg_kg * ENERGY_CONTENT["LPG(프로판 1호)"]

elif usage_type == "Kg 단위":
    usage_lpg_kg = st.sidebar.number_input("사용할 LPG량 (kg)", min_value=1, value=20, step=1, format="%d")
    lpg_price = st.sidebar.number_input("LPG(프로판 1호) 가격 (원/kg)", min_value=0.0, value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.2f")
    usage_gj = usage_lpg_kg * ENERGY_CONTENT["LPG(프로판 1호)"]

else:  # 금액 단위
    usage_cost = st.sidebar.number_input("사용할 LPG 비용 (원)", min_value=1000, value=50000, step=10000, format="%d")
    lpg_price = st.sidebar.number_input("LPG(프로판 1호) 가격 (원/kg)", min_value=0.0, value=float(DEFAULT_PRICES["LPG(프로판 1호)"]), format="%.2f")
    usage_lpg_kg = usage_cost / lpg_price
    usage_gj = usage_lpg_kg * ENERGY_CONTENT["LPG(프로판 1호)"]

# 도시가스 MJ당 가격 입력
gas_mj_price = st.sidebar.number_input("도시가스 가격 (원/MJ)", min_value=0.0, value=float(DEFAULT_PRICES["도시가스(LNG)"]), format="%.2f")

# 도시가스 초기 공사비 입력
gas_install_cost = st.sidebar.number_input("도시가스 초기 공사비 (원)", min_value=1000000, value=3000000, step=100000, format="%d")

# 도시가스 m³당 가격 환산
gas_price = gas_mj_price * ENERGY_CONTENT["도시가스(LNG)"]

# LPG MJ당 가격 계산
lpg_mj_price = lpg_price / ENERGY_CONTENT["LPG(프로판 1호)"]

# 사용량 기준 예상 비용
gas_cost = usage_gj * gas_mj_price
lpg_cost = usage_gj * lpg_mj_price

# 경제성 비교
cost_ratio = (lpg_cost / gas_cost - 1) * 100
monthly_savings = lpg_cost - gas_cost

# 공사비 회수기간 계산
if monthly_savings > 0:
    payback_period = gas_install_cost / monthly_savings
else:
    payback_period = float('inf')  # 절약 금액이 없으면 회수 불가

# 데이터 정리
data = {
    "항목": ["단위", "단위당 가격", "기준열량(MJ)", "열량당 가격", "총사용량", "총열량", "예상 비용", "도시가스 기준 비율"],
    "도시가스(LNG)": ["m³", f"{gas_price:,.0f} 원/m³", f"{ENERGY_CONTENT['도시가스(LNG)']}", f"{gas_mj_price:.2f} 원/MJ", f"{usage_gj / ENERGY_CONTENT['도시가스(LNG)']:.2f} m³", f"{usage_gj:,.2f} MJ", f"{gas_cost:,.0f} 원", "100%"],
    "LPG(프로판 1호)": ["kg", f"{lpg_price:,.0f} 원/kg", f"{ENERGY_CONTENT['LPG(프로판 1호)']}", f"{lpg_mj_price:.2f} 원/MJ", f"{usage_lpg_kg:,.0f} kg", f"{usage_gj:,.2f} MJ", f"{lpg_cost:,.0f} 원", f"{(lpg_mj_price / gas_mj_price * 100):.2f}%"]
}
df = pd.DataFrame(data)

# 경제성 비교 결과 출력
if gas_cost < lpg_cost:
    st.success(f"도시가스가 LPG보다 {abs(cost_ratio):.2f}% 더 경제적입니다!")
else:
    st.warning(f"LPG를 사용하면 도시가스보다 {abs(cost_ratio):.2f}% 더 많은 비용이 듭니다!")

# 표 출력
st.subheader("경제성 비교표")
st.dataframe(df)

# 경제성 비교 설명 추가
st.markdown("""
##### 주요 항목 설명

0. **기준 발열량** = `에너지기본법 시행규칙 별표 에너지열량 환산기준(제5조제1항 관련)`
1. **열량당 가격 (원/MJ)** = `단위당 가격 ÷ 발열량`
2. **총 사용량** = `총 발열량 ÷ 기준열량`
3. **총 발열량 (MJ)** = `사용한 LPG량(kg) × LPG의 기준열량`
4. **예상 비용** = `총 사용량 × 단위당 가격`
5. **도시가스 기준 비율** = `(LPG의 열량당 가격 ÷ 도시가스의 열량당 가격) × 100`
""")

# 추가적인 경제성 분석 데이터
extra_data = {
    "항목": ["초기 공사비", "매월 절약금액", "공사비 회수기간"],
    "금액": [f"{gas_install_cost:,.0f} 원", f"{monthly_savings:,.0f} 원", f"{payback_period:.1f} 개월" if monthly_savings > 0 else "회수 불가"]
}
extra_df = pd.DataFrame(extra_data)

st.subheader("공사비 회수 기간 산정")
st.dataframe(extra_df)

# 설명 추가
st.markdown("""
이 계산기는 LPG와 도시가스의 경제성을 비교하기 위해 다음 공식을 사용합니다:

1. **발열량 기준 비용 계산:**
    - `연료비 = 사용량(MJ) × 단위 MJ당 가격(원/MJ)`
2. **절약 금액:**
   - `절약 금액 = LPG 비용 - 도시가스 비용`
3. **공사비 회수 기간:**
   - `회수 기간(개월) = 도시가스 공사비 ÷ 매월 절약금액`
""")