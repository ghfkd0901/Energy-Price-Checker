import streamlit as st
import pandas as pd

# 페이지 제목
st.title("LPG (체적 단위) vs 도시가스 경제성 비교")

# 사용자 입력 (사이드바)
st.sidebar.header("체적 거래 입력값")
lpg_price_per_m3 = st.sidebar.number_input("프로판(LPG1호) m³당 요금 (원)", value=3000)
standard_evaporation_rate = st.sidebar.number_input("표준 기화율", value=0.251)
regulator_correction_factor = st.sidebar.number_input("조정기 보정계수", value=1.0)

lng_price_per_nm3 = st.sidebar.number_input("도시가스 Nm³당 요금 (원)", value=1003)

# 고정된 총발열량 데이터
lpg_calorific_mj = 50.2  # 1kg 기준
lng_calorific_mj = 42.7  # 1Nm³ 기준

# LPG 체적 단위 가격을 kg 기준으로 변환
lpg_price_per_kg_converted = lpg_price_per_m3 * standard_evaporation_rate / regulator_correction_factor
lpg_price_per_mj_volume = lpg_price_per_kg_converted / lpg_calorific_mj

# MJ당 가격 계산
lng_price_per_mj = lng_price_per_nm3 / lng_calorific_mj

# 비율 계산
lpg_ratio_volume = lpg_price_per_mj_volume / lng_price_per_mj

# 표 출력
data_volume = {
    "항목": ["단위당 가격 (원)", "총발열량 (MJ)", "MJ당 가격 (원)", "비율"],
    "프로판 (LPG1호, 체적 거래)": [
        f"{lpg_price_per_m3:,.2f}",
        f"{lpg_calorific_mj:,.2f}",
        f"{lpg_price_per_mj_volume:,.2f}",
        f"{lpg_ratio_volume:.2%}"
    ],
    "도시가스 (LNG)": [
        f"{lng_price_per_nm3:,.2f}",
        f"{lng_calorific_mj:,.2f}",
        f"{lng_price_per_mj:,.2f}",
        "1.00"
    ]
}
df_volume = pd.DataFrame(data_volume)

# 스타일 적용: 글씨 크기 확대
def highlight_large_text(val):
    return 'font-size: 18px; text-align: center;'

styled_df_volume = df_volume.style.applymap(highlight_large_text)
st.dataframe(styled_df_volume)