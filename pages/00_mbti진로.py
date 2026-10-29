```python
import streamlit as st

st.set_page_config(
    page_title="MBTI 진로 탐험소",
    page_icon="🧭",
    layout="wide"
)

# MBTI별 진로 추천 데이터
careers = {
    "ISTJ": [
        {
            "name": "회계사",
            "major": "회계학과, 경영학과",
            "personality": "꼼꼼하고 책임감이 강하며 숫자를 다루는 것을 좋아하는 사람",
            "salary": "약 5,000만~8,000만 원",
            "description": "기업의 회계 자료와 재무 상태를 분석해요."
        },
        {
            "name": "품질관리 전문가",
            "major": "산업공학과, 식품공학과",
            "personality": "세심하고 체계적이며 작은 차이를 잘 발견하는 사람",
            "salary": "약 3,500만~5,500만 원",
            "description": "제품이 정해진 품질 기준을 충족하는지 확인해요."
        }
    ],
    "ISFJ": [
        {
            "name": "간호사",
            "major": "간호학과",
            "personality": "책임감이 강하고 다른 사람을 세심하게 배려하는 사람",
            "salary": "약 3,500만~5,500만 원",
            "description": "환자의 건강을 살피고 치료와 회복을 도와요."
        },
        {
            "name": "초등학교 교사",
            "major": "초등교육과",
            "personality": "인내심이 있고 다른 사람을 잘 이해하는 사람",
            "salary": "약 4,000만~7,000만 원",
            "description": "어린 학생들의 학습과 성장을 도와요."
        }
    ],
    "INFJ": [
        {
            "name": "상담심리사",
            "major": "심리학과, 상담학과",
            "personality": "공감 능력이 좋고 다른 사람의 이야기를 잘 들어 주는 사람",
            "salary": "약 2,800만~4,500만 원",
            "description": "사람들이 고민을 이해하고 해결하도록 도와요."
        },
        {
            "name": "작가",
            "major": "문예창작학과, 국어국문학과",
            "personality": "상상력이 풍부하고 생각을 글로 표현하는 사람",
            "salary": "약 2,500
