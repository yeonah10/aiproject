
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =========================
# 1. 페이지 설정
# =========================

st.set_page_config(
    page_title="인천 인구통계",
    page_icon="📊",
    layout="wide"
)

st.title("📊 인천광역시 인구통계 분석")
st.write("인천광역시의 지역별, 연도별, 성별 인구를 분석합니다.")


# =========================
# 2. CSV 파일 불러오기
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

file_paths = [
    BASE_DIR / "population_utf8.csv",
    BASE_DIR / "population.csv"
]

CSV_PATH = next(
    (path for path in file_paths if path.is_file()),
    None
)

if CSV_PATH is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("저장소 최상위 폴더에 population_utf8.csv 파일을 넣어 주세요.")
    st.stop()


@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    return data


df = load_data(str(CSV_PATH))


# =========================
# 3. 행정구역 정리
# =========================

df["행정구역"] = df["행정구역"].astype(str).str.strip()


def clean_region(name):
    name = name.split("(")[0].strip()

    if name == "인천광역시":
        return name

    return name.replace("인천광역시 ", "")


df["지역명"] = df["행정구역"].apply(clean_region)


# =========================
# 4. 연령대 설정
# =========================

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


# =========================
# 5. 분석 조건 선택
# =========================

st.subheader("🔎 분석 조건")

col1, col2, col3 = st.columns(3)

with col1:
    region = st.selectbox(
        "행정구역 선택",
        df["지역명"].tolist()
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


# =========================
# 6. 선택 지역 데이터
# =========================

selected_data = df[df["지역명"] == region]

if selected_data.empty:
    st.error("선택한 지역의 데이터가 없습니다.")
    st.stop()

selected = selected_data.iloc[0]


# =========================
# 7. 성별에 따른 색상
# =========================

if gender == "여성":
    graph_color = "#FFB6C1"

elif gender == "남성":
    graph_color = "#87CEEB"

else:
    graph_color = "#B39DDB"


gender_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[gender]


# =========================
# 8. 연령별 인구 데이터
# =========================

values = []

for age in ages:

    column_name = f"{year}년_{gender_prefix}거주자_{age}"

    if column_name not in df.columns:
        st.error(f"데이터 열이 없습니다: {column_name}")
        st.stop()

    value = pd.to_numeric(
        str(selected[column_name]).replace(",", ""),
        errors="coerce"
    )

    values.append(value)


chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": values
})

chart_df["인구수"] = chart_df["인구수"].fillna(0)


# =========================
# 9. 연령별 꺾은선 그래프
# =========================

st.divider()
st.subheader("📈 연령별 인구 그래프")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",

        line=dict(
            color=graph_color,
            width=4
        ),

        marker=dict(
            color=graph_color,
            size=9
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

y_max = max(
    100000,
    (int(chart_df["인구수"].max()) // 100000 + 1) * 100000
)

fig.update_layout(
    title=f"{region} {year}년 {gender} 연령별 인구",

    xaxis=dict(
        title="연령대",
        tickmode="array",
        tickvals=ages,
        ticktext=ages
    ),

    yaxis=dict(
        title="인구수 (명)",
        range=[0, y_max],
        dtick=100000,
        tickformat=","
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================
# 10. 남녀 인구 비율 원형 그래프
# =========================

st.divider()
st.subheader("🥧 남녀 인구 비율")

male_column = f"{year}년_남_거주자_총인구수"
female_column = f"{year}년_여_거주자_총인구수"

male_population = pd.to_numeric(
    str(selected[male_column]).replace(",", ""),
    errors="coerce"
)

female_population = pd.to_numeric(
    str(selected[female_column]).replace(",", ""),
    errors="coerce"
)

male_population = 0 if pd.isna(male_population) else male_population
female_population = 0 if pd.isna(female_population) else female_population

fig_gender = go.Figure(
    data=[
        go.Pie(
            labels=["남성", "여성"],

            values=[
                male_population,
                female_population
            ],

            hole=0.35,

            marker=dict(
                colors=[
                    "#87CEEB",
                    "#FFB6C1"
                ]
            ),

            textinfo="label+percent",

            hovertemplate=(
                "%{label}<br>"
                "인구수: %{value:,.0f}명<br>"
                "비율: %{percent}"
                "<extra></extra>"
            )
        )
    ]
)

fig_gender.update_layout(
    title={
        "text": f"{region} {year}년 남녀 인구 비율",
        "x": 0.5
    },

    height=450,
    paper_bgcolor="white",
    showlegend=True
)

st.plotly_chart(
    fig_gender,
    use_container_width=True
)


# =========================
# 11. 연령대별 행정구역 TOP 10
# =========================

st.divider()
st.subheader("🏆 연령대별 인구가 많은 행정구역 TOP 10")

rank_col1, rank_col2 = st.columns(2)

with rank_col1:
    selected_age = st.selectbox(
        "비교할 연령대",
        ages,
        index=2
    )

with rank_col2:
    rank_gender = st.selectbox(
        "비교할 성별",
        ["전체", "남성", "여성"],
        key="rank_gender"
    )


rank_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[rank_gender]

rank_column = f"{year}년_{rank_prefix}거주자_{selected_age}"

if rank_column not in df.columns:
    st.error(f"데이터 열이 없습니다: {rank_column}")
    st.stop()


# 인천광역시 전체 행 제외
rank_df = df[
    df["지역명"] != "인천광역시"
].copy()

rank_df["인구수"] = pd.to_numeric(
    rank_df[rank_column].astype(str).str.replace(",", ""),
    errors="coerce"
)

rank_df = rank_df.dropna(subset=["인구수"])

rank_df = rank_df.sort_values(
    by="인구수",
    ascending=False
).head(10)


fig_rank = go.Figure()

fig_rank.add_trace(
    go.Bar(
        x=rank_df["지역명"],
        y=rank_df["인구수"],

        marker_color="#B39DDB",

        text=rank_df["인구수"].apply(
            lambda x: f"{x:,.0f}명"
        ),

        textposition="outside",

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

fig_rank.update_layout(
    title=f"{year}년 {selected_age} {rank_gender} 인구 TOP 10",

    xaxis_title="행정구역",
    yaxis_title="인구수 (명)",

    yaxis=dict(
        tickformat=","
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500
)

st.plotly_chart(
    fig_rank,
    use_container_width=True
)


# =========================
# 12. 인구 분석 결과
# =========================

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


# =========================
# 13. 상세 데이터
# =========================

st.divider()
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
