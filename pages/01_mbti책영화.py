import streamlit as st

st.title("MBTI 책과 영화 추천소")

st.write("앱이 정상적으로 실행되고 있어요!")

mbti = st.selectbox(
    "나의 MBTI를 선택하세요.",
    [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
)

st.success("선택한 MBTI: " + mbti)
