
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="인천광역시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 인천광역시 연령별 인구 분석")
st.write("행정구역, 성별, 연도에 따른 연령별 인구를 분석합니다.")

# 상위 폴더의 CSV 파일 경로
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "population_utf8.csv"

# 데이터 불러오기
@st.cache_data
def load_data():

    if not CSV_PATH.exists():
        st.error(
            f"CSV 파일을 찾을 수 없습니다.\n\n"
            f"현재 확인한 경로: {CSV_PATH}"
        )
        st.stop()

    try:
        df = pd.read_csv(
            CSV_PATH,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            CSV_PATH,
            encoding="cp949"
        )

    return df


df = load_data()

# 행정구역 데이터 정리
df["행정구역"] = (
    df["행정구역"]
    .astype(str)
    .str.strip()
)

def clean_region(name):
    name = name.split("(")[0].strip()

    if name == "인천광역시":
        return name

    return name.replace("인천광역시 ", "")


df["지역명"] = df["행정구역"].apply(clean_region)

# 선택 가능한 행정구역
regions = df["지역명"].tolist()

# 선택 항목
st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_region = st.selectbox(
        "행정구역",
        regions
    )

with col2:
    selected_gender = st.selectbox(
        "성별",
        ["전체", "남성", "여성"]
    )

with col3:
    selected_year = st.selectbox(
        "연도",
        list(range(2020, 2026)),
        index=5
    )

# 연령 구간
ages = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

# 선택한 지역 찾기
region_data = df[
    df["지역명"] == selected_region
]

if region_data.empty:
    st.error("선택한 행정구역 데이터가 없습니다.")
    st.stop()

region_data = region_data.iloc[0]

# 성별에 따른 데이터 열 이름
if selected_gender == "전체":
    gender_prefix = ""
elif selected_gender == "남성":
    gender_prefix = "남_"
else:
    gender_prefix = "여_"

# 연령별 인구 추출
population = []

for age in ages:

    column_name = (
        f"{selected_year}년_"
        f"{gender_prefix}거주자_{age}"
    )

    if column_name not in df.columns:
        st.error(f"데이터 열을 찾을 수 없습니다: {column_name}")
        st.stop()

    value = pd.to_numeric(
        str(region_data[column_name]).replace(",", ""),
        errors="coerce"
    )

    population.append(value)


# 그래프용 데이터
chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": population
})

chart_df["인구수"] = chart_df["인구수"].fillna(0)

# 그래프 제목
chart_title = (
    f"{selected_region} "
    f"{selected_year}년 "
    f"{selected_gender} 연령별 인구"
)

# 세로축 최대값 설정
max_population = chart_df["인구수"].max()

y_max = max(
    100000,
    ((int(max_population) // 100000) + 1) * 100000
)

# 꺾은선 그래프
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",

        line=dict(
            color="#87CEEB",
            width=4
        ),

        marker=dict(
            color="#87CEEB",
            size=9
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

# 그래프 디자인
fig.update_layout(
    title=dict(
        text=chart_title,
        x=0.5,
        xanchor="center"
    ),

    xaxis=dict(
        title="나이",
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        showgrid=True,
        gridcolor="#DCECF4",
        gridwidth=1
    ),

    yaxis=dict(
        title="인구수 (명)",
        range=[0, y_max],
        tick0=0,
        dtick=100000,
        tickformat=",",
        showgrid=True,
        gridcolor="#DCECF4",
        gridwidth=1
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="sans-serif",
        size=13,
        color="#333333"
    ),

    hovermode="x unified",
    height=550,

    margin=dict(
        l=50,
        r=30,
        t=80,
        b=80
    )
)

# 그래프 출력
st.subheader("📈 연령별 인구 분포")

st.plotly_chart(
    fig,
    use_container_width=True
)

# 주요 분석 결과
st.subheader("📌 인구 분석 결과")

total_population = chart_df["인구수"].sum()

max_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "나이"
]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "연령별 인구 합계",
        f"{total_population:,.0f}명"
    )

with col2:
    st.metric(
        "인구가 가장 많은 연령대",
        max_age
    )

# 연령별 인구 표
st.subheader("📋 연령별 인구 데이터")

display_df = chart_df.copy()
display_df["인구수"] = display_df["인구수"].map(
    lambda x: f"{x:,.0f}명"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "자료: 제공된 인천광역시 인구 데이터"
)
