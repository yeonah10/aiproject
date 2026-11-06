
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="인천 인구통계",
    page_icon="📊",
    layout="wide"
)

st.title("📊 인천광역시 인구통계 분석")
st.write("지역과 연도별 인구 현황을 확인할 수 있습니다.")

# 1. CSV 파일 불러오기
BASE_DIR = Path(__file__).resolve().parent.parent

file_paths = [
    BASE_DIR / "population_utf8.csv",
    BASE_DIR / "population.csv"
]

CSV_PATH = next((p for p in file_paths if p.is_file()), None)

if CSV_PATH is None:
    st.error("CSV 파일을 찾을 수 없습니다. 저장소 최상위 폴더를 확인해 주세요.")
    st.stop()


@st.cache_data
def load_data(path):
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


df = load_data(str(CSV_PATH))

# 2. 지역명 정리
if "행정구역" not in df.columns:
    st.error("CSV 파일에 '행정구역' 열이 없습니다.")
    st.stop()

df["행정구역"] = df["행정구역"].astype(str).str.strip()


def clean_region(name):
    name = name.split("(")[0].strip()
    if name == "인천광역시":
        return name
    return name.replace("인천광역시 ", "")


df["지역명"] = df["행정구역"].apply(clean_region)

# 3. 연령대 설정
ages = [
    "0~9세", "10~19세", "20~29세",
    "30~39세", "40~49세", "50~59세",
    "60~69세", "70~79세", "80~89세",
    "90~99세", "100세 이상"
]


def get_number(value):
    return pd.to_numeric(
        str(value).replace(",", "").strip(),
        errors="coerce"
    )


def get_population(row, year, prefix, age=None):
    if age is None:
        column = f"{year}년_{prefix}거주자_총인구수"
    else:
        column = f"{year}년_{prefix}거주자_{age}"

    if column not in df.columns:
        return 0

    value = get_number(row[column])
    return 0 if pd.isna(value) else value


# 4. 지역 및 연도 선택
st.subheader("🔎 분석 조건")

col1, col2 = st.columns(2)

with col1:
    region = st.selectbox(
        "행정구역 선택",
        df["지역명"].drop_duplicates().tolist()
    )

with col2:
    year = st.selectbox(
        "연도 선택",
        list(range(2020, 2026)),
        index=5
    )

selected = df[df["지역명"] == region].iloc[0]

# 5. 연령별 남녀 꺾은선그래프
st.divider()
st.subheader("📈 연령별 남녀 인구 통계")

male_values = [
    get_population(selected, year, "남_", age)
    for age in ages
]

female_values = [
    get_population(selected, year, "여_", age)
    for age in ages
]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=ages,
        y=male_values,
        mode="lines+markers",
        name="남성",
        line=dict(color="#87CEEB", width=3),
        marker=dict(color="#87CEEB", size=8),
        hovertemplate="%{x}<br>남성: %{y:,.0f}명<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=ages,
        y=female_values,
        mode="lines+markers",
        name="여성",
        line=dict(color="#FFB6C1", width=3),
        marker=dict(color="#FFB6C1", size=8),
        hovertemplate="%{x}<br>여성: %{y:,.0f}명<extra></extra>"
    )
)

max_value = max(male_values + female_values) if ages else 0
y_max = max(100000, (int(max_value) // 100000 + 1) * 100000)

fig.update_layout(
    title=f"{region} {year}년 연령별 남녀 인구 비교",
    xaxis_title="연령대",
    yaxis_title="인구수 (명)",
    xaxis=dict(
        categoryorder="array",
        categoryarray=ages
    ),
    yaxis=dict(
        range=[0, y_max],
        dtick=100000,
        tickformat=","
    ),
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=550,
    legend=dict(
        orientation="h",
        y=1.12,
        x=0.5,
        xanchor="center"
    )
)

st.plotly_chart(fig, use_container_width=True)

# 6. 남녀 인구 비율 원형그래프
st.divider()
st.subheader("🥧 남녀 인구 비율")

male_total = get_population(selected, year, "남_")
female_total = get_population(selected, year, "여_")
total_population = male_total + female_total

pie_col1, pie_col2 = st.columns([1, 1])

with pie_col1:
    pie_fig = go.Figure(
        data=[
            go.Pie(
                labels=["남성", "여성"],
                values=[male_total, female_total],
                marker=dict(
                    colors=["#87CEEB", "#FFB6C1"]
                ),
                hole=0,
                textinfo="label+percent",
                hovertemplate="%{label}<br>%{value:,.0f}명<br>%{percent}<extra></extra>"
            )
        ]
    )

    pie_fig.update_layout(
        title=f"{region} {year}년 남녀 인구 비율",
        height=400
    )

    st.plotly_chart(pie_fig, use_container_width=True)

with pie_col2:
    st.metric("남성 인구", f"{male_total:,.0f}명")
    st.metric("여성 인구", f"{female_total:,.0f}명")
    st.metric("전체 인구", f"{total_population:,.0f}명")

# 7. 연령대별 행정구역 TOP 10
st.divider()
st.subheader("🏆 연령대별 행정구역 TOP 10")

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
        ["전체", "남성", "여성"]
    )

rank_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}[rank_gender]

rank_column = f"{year}년_{rank_prefix}거주자_{selected_age}"

if rank_column not in df.columns:
    st.error(f"TOP 10 데이터 열을 찾을 수 없습니다: {rank_column}")
    st.stop()

rank_df = df[df["지역명"] != "인천광역시"].copy()
rank_df["인구수"] = rank_df[rank_column].apply(get_number)

rank_df = (
    rank_df.dropna(subset=["인구수"])
    .sort_values("인구수", ascending=False)
    .head(10)
)

rank_fig = go.Figure()

rank_fig.add_trace(
    go.Bar(
        x=rank_df["지역명"],
        y=rank_df["인구수"],
        marker_color="#B39DDB",
        text=rank_df["인구수"].apply(lambda x: f"{x:,.0f}명"),
        textposition="outside",
        hovertemplate="%{x}<br>인구수: %{y:,.0f}명<extra></extra>"
    )
)

rank_fig.update_layout(
    title=f"{year}년 {selected_age} {rank_gender} 인구 TOP 10",
    xaxis_title="행정구역",
    yaxis_title="인구수 (명)",
    yaxis=dict(tickformat=","),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500
)

st.plotly_chart(rank_fig, use_container_width=True)

# 8. 연령별 상세 데이터
st.divider()
st.subheader("📋 연령별 남녀 상세 데이터")

detail_df = pd.DataFrame({
    "연령대": ages,
    "남성 인구": male_values,
    "여성 인구": female_values,
    "전체 인구": [
        m + f for m, f in zip(male_values, female_values)
    ]
})

for column in ["남성 인구", "여성 인구", "전체 인구"]:
    detail_df[column] = detail_df[column].apply(
        lambda x: f"{x:,.0f}명"
    )

st.dataframe(
    detail_df,
    use_container_width=True,
    hide_index=True
)

st.caption("자료: 제공된 인천광역시 인구 데이터")
