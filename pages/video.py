import streamlit as st

st.title("도시가스 화력 비교 영상")

st.write("도시가스가 높은 화력을 가질 수 있음을 보여주는 영상입니다.")

# 동영상 삽입
video_url = "https://youtu.be/DnKV-znPe-0?si=HMYYhcdB7zWyxgsD"  # 예시 URL, 실제 영상 URL로 변경 필요
st.video(video_url)

st.write("이 영상을 통해 도시가스의 강력한 화력을 확인하세요!")
