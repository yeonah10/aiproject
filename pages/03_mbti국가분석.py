from pathlib import Path
import html

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="나라별 MBTI 분포",
    page_icon="🌍",
    layout="wide"
)


# --------------------------------------------------
# CSV 파일 불러오기
# app.py는 pages 폴더 안에 있고 CSV는 상위 폴더에 있음
# --------------------------------------------------
csv_path = Path(__file__).resolve().parent.parent / "countriesMBTI_16types.csv"

if not csv_path.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("확인한 경로:", str(csv_path))
    st.info(
        "countriesMBTI_16types.csv 파일이 app.py의 상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()

try:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="cp949")
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 정리
# --------------------------------------------------
df.columns = df.columns.astype(str).str.strip()

# 첫 번째 열을 국가명 열로 사용
country_column = df.columns[0]

# MBTI 16가지 유형
mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

# CSV에 실제로 존재하는 MBTI 열만 사용
available_types = [
    mbti for mbti in mbti_types
    if mbti in df.columns
]

if not available_types:
    st.error("CSV 파일에서 MBTI 열을 찾을 수 없습니다.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()

# 국가명 정리
df[country_column] = df[country_column].astype(str).str.strip()
df = df[df[country_column].notna()]
df = df[df[country_column] != ""]

# MBTI 값 숫자로 변환
for mbti in available_types:
    df[mbti] = pd.to_numeric(df[mbti], errors="coerce")

df[available_types] = df[available_types].fillna(0)


# --------------------------------------------------
# 디자인
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F7F1E8;
    }

    h1, h2, h3, p, label {
        color: #594638;
    }

    .main-title {
        text-align: center;
        color: #594638;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .sub-title {
        text-align: center;
        color: #927B67;
        font-size: 16px;
        margin-bottom: 30px;
    }

    div[data-baseweb="select"] {
        background-color: #FFFDF9;
        border-radius: 10px;
    }

    .result-box {
        background-color: #FFFDF9;
        border: 1px solid #E5D7C7;
        border-radius: 15px;
        padding: 22px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🌍 나라별 MBTI 분포</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">나라를 선택하고 MBTI 유형별 비율을 확인해 보세요.</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 국가 선택
# --------------------------------------------------
countries = sorted(df[country_column].dropna().unique().tolist())

if not countries:
    st.error("CSV 파일에 국가 데이터가 없습니다.")
    st.stop()

selected_country = st.selectbox(
    "🌏 국가를 선택하세요",
    countries
)


# --------------------------------------------------
# 선택한 국가 데이터
# --------------------------------------------------
country_data = df[df[country_column] == selected_country]

if country_data.empty:
    st.warning("선택한 국가의 데이터가 없습니다.")
    st.stop()

values = country_data.iloc[0][available_types]

chart_data = pd.DataFrame({
    "MBTI": available_types,
    "비율": values.values
})

chart_data["비율"] = pd.to_numeric(
    chart_data["비율"], errors="coerce"
).fillna(0)

chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)


# --------------------------------------------------
# 결과 표시
# --------------------------------------------------
st.markdown(
    f'<div class="result-box"><h3>📊 {html.escape(str(selected_country))}의 MBTI 분포</h3></div>',
    unsafe_allow_html=True
)

# 최고 비율 MBTI
top_mbti = chart_data.iloc[0]["MBTI"]
top_value = chart_data.iloc[0]["비율"]

st.markdown(
    f"""
    <div style="
        background: #E9D8C5;
        border-radius: 12px;
        padding: 18px;
        margin-top: 15px;
        text-align: center;
    ">
        <div style="color:#80664F; font-size:15px;">
            가장 높은 비율의 MBTI
        </div>
        <div style="color:#594638; font-size:30px; font-weight:800;">
            {html.escape(str(top_mbti))}
        </div>
        <div style="color:#80664F; font-size:18px;">
            {top_value:.2f}%
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 막대그래프
# 1위는 호피 무늬, 나머지는 연한 갈색 그라데이션
# --------------------------------------------------
max_value = max(float(chart_data["비율"].max()), 1)

bars_html = ""

for index, row in chart_data.iterrows():
    mbti = html.escape(str(row["MBTI"]))
    value = float(row["비율"])

    width = max((value / max_value) * 100, 0)

    if index == 0:
        bar_style = """
            background-color: #B58B62;
            background-image:
                radial-gradient(ellipse at 25% 35%, #4B3528 0 5%, transparent 6%),
                radial-gradient(ellipse at 70% 65%, #4B3528 0 7%, transparent 8%),
                radial-gradient(ellipse at 45% 85%, #4B3528 0 4%, transparent 5%),
                radial-gradient(ellipse at 85% 20%, #4B3528 0 5%, transparent 6%);
            background-size: 38px 28px;
        """
    else:
        # 순위가 높을수록 진하고 낮을수록 연한 갈색
        shade = 180 + min(index * 4, 65)
        bar_style = f"background-color: rgb({shade}, {shade-25}, {shade-48});"

    bars_html += f"""
    <div style="margin: 17px 0;">
        <div style="
            display:flex;
            justify-content:space-between;
            margin-bottom:6px;
            color:#594638;
            font-weight:600;
            font-size:15px;
        ">
            <span>{mbti}</span>
            <span>{value:.2f}%</span>
        </div>

        <div style="
            width:100%;
            height:25px;
            background:#E9DFD3;
            border-radius:6px;
            overflow:hidden;
        ">
            <div style="
                width:{width:.2f}%;
                height:25px;
                border-radius:6px;
                {bar_style}
            "></div>
        </div>
    </div>
    """

components.html(
    f"""
    <div style="
        background:#FFFDF9;
        padding:25px;
        border-radius:15px;
        font-family:Arial, sans-serif;
    ">
        {bars_html}
    </div>
    """,
    height=900,
    scrolling=True
)


# --------------------------------------------------
# 데이터 표
# --------------------------------------------------
st.markdown("### 📋 MBTI 비율 순위")

display_data = chart_data.copy()
display_data.index = range(1, len(display_data) + 1)
display_data.index.name = "순위"
display_data["비율"] = display_data["비율"].map(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    display_data,
    use_container_width=True
)

st.caption("※ 그래프와 순위는 CSV 파일에 저장된 데이터를 기준으로 표시합니다.")
