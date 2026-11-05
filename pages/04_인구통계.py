
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 연령별 인구 분석")

# CSV 파일 경로 자동 확인
BASE_DIR = Path(__file__).resolve().parent.parent

possible_paths = [
    BASE_DIR / "population_utf8.csv",
    BASE_DIR / "population.csv"
]

CSV_PATH = next(
    (p for p in possible_paths if p.is_file()),
    None
)

if CSV_PATH is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("현재 폴더:", str(BASE_DIR))
    st.write("저장소 최상위 폴더에 CSV 파일이 있는지 확인해 주세요.")
    st.stop()


# 데이터 불러오기
@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    return data


df = load_data(str(CSV_PATH))

# 행정구역 정리
df["행정구역"] = df["행정구역"].astype(str).str.strip()

def clean_region(name):
    name = name.split("(")[0].strip()

    if name == "인천광역시":
        return name

    return name.replace("인천광역시 ", "")

df["지역명"] = df["행정구역"].apply(clean_region)

# 선택 항목
st.subheader("🔎 분석 조건")

col1, col2, col3 = st.columns(3)

regions = df["지역명"].tolist()

with col1:
    region = st.selectbox(
        "행정구역 선택",
        regions
    )

with col2:
    gender = st.selectbox(
        "성별 선택",
        ["전체", "남성", "여성"]
    )

with col3:
    year = st.selectbox(
        "연도 선택",
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

# 지역 데이터 찾기
selected = df[df["지역명"] == region]

if selected.empty:
    st.error("선택한 지역의 데이터가 없습니다.")
    st.stop()

selected = selected.iloc[0]

# 성별에 따른 열 이름
gender_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[gender]

# 연령별 인구 추출
values = []

for age in ages:
    col_name = f"{year}년_{gender_prefix}거주자_{age}"

    if col_name not in df.columns:
        st.error(f"데이터 열이 없습니다: {col_name}")
        st.stop()

    value = pd.to_numeric(
        str(selected[col_name]).replace(",", ""),
        errors="coerce"
    )

    values.append(value)

chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": values
})

chart_df["인구수"] = chart_df["인구수"].fillna(0)

# 세로축 10만 단위
max_value = chart_df["인구수"].max()

y_max = max(
    100000,
    (int(max_value) // 100000 + 1) * 100000
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

fig.update_layout(
    title={
        "text": f"{region} {year}년 {gender} 연령별 인구",
        "x": 0.5
    },

    xaxis=dict(
        title="나이",
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        showgrid=True,
        gridcolor="#D6EAF5"
    ),

    yaxis=dict(
        title="인구수 (명)",
        range=[0, y_max],
        tick0=0,
        dtick=100000,
        tickformat=",",
        showgrid=True,
        gridcolor="#D6EAF5"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="sans-serif",
        size=13,
        color="#333333"
    ),

    hovermode="x unified",
    height=550
)

st.subheader("📈 연령별 인구 그래프")

st.plotly_chart(
    fig,
    use_container_width=True
)

# 분석 결과
st.divider()
st.subheader("📌 인구 분석 결과")

col1, col2 = st.columns(2)

total = chart_df["인구수"].sum()

max_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "나이"
]

with col1:
    st.metric(
        "연령별 인구 합계",
        f"{total:,.0f}명"
    )

with col2:
    st.metric(
        "인구가 가장 많은 연령대",
        max_age
    )

# 데이터 표
st.subheader("📋 연령별 상세 데이터")

display_df = chart_df.copy()
display_df["인구수"] = display_df["인구수"].apply(
    lambda x: f"{x:,.0f}명"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.caption("자료: 제공된 인천광역시 인구 데이터")

