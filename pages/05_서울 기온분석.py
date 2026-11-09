import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =========================
# 1. 페이지 설정
# =========================

st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석")
st.write("서울의 월별 평균기온과 연도별 최고·최저기온을 분석합니다.")

PINK = "#FFB6C1"
SKY = "#ADD8E6"
PURPLE = "#B9A0D9"

# =========================
# 2. CSV 파일 불러오기
# =========================

file_path = Path(__file__).resolve().parent / "temperature.csv"

if not file_path.exists():
    file_path = Path(__file__).resolve().parent.parent / "temperature.csv"

if not file_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    df = pd.read_csv(file_path, encoding="cp949")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_path, encoding="euc-kr")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

df.columns = df.columns.str.strip()

# =========================
# 3. 데이터 전처리
# =========================

required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("CSV 파일에 필요한 열이 없습니다: " + ", ".join(missing_columns))
    st.stop()

# 날짜의 영어 월 이름을 숫자로 변환
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

date_parts = df["일시"].astype(str).str.strip().str.extract(
    r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{2})$"
)

df["월"] = date_parts[0].map(month_map)

year_suffix = pd.to_numeric(date_parts[1], errors="coerce")

df["연도"] = year_suffix.apply(
    lambda x: 1900 + int(x) if pd.notna(x) and x >= 69
    else (2000 + int(x) if pd.notna(x) else None)
)

df = df.dropna(subset=["월", "연도"]).copy()

df["월"] = df["월"].astype(int)
df["연도"] = df["연도"].astype(int)

# 기온 숫자 변환
for col in ["평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 월 이름
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

month_ticks = list(range(1, 13))
month_labels = [month_names[m] for m in month_ticks]

# =========================
# 4. 서울 월별 평균기온
# =========================

st.divider()
st.header("📊 1. 서울 월별 평균기온")

st.write("전체 연도의 데이터를 바탕으로 각 월의 평균기온을 계산합니다.")

monthly_average = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(month_ticks)
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_ticks,
        y=monthly_average.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(color=PURPLE, width=3),
        marker=dict(size=9, color=PURPLE),
        connectgaps=False
    )
)

fig1.update_layout(
    title=dict(
        text="서울 월별 평균기온",
        x=0.5,
        xanchor="center"
    ),
    xaxis_title="월",
    yaxis_title="평균기온(℃)",
    height=480,
    template="plotly_white",
    hovermode="x unified"
)

fig1.update_xaxes(
    tickmode="array",
    tickvals=month_ticks,
    ticktext=month_labels
)

st.plotly_chart(fig1, use_container_width=True)

with st.expander("월별 평균기온 데이터 보기"):
    average_table = pd.DataFrame({
        "월": month_labels,
        "평균기온(℃)": monthly_average.round(1).values
    })

    st.dataframe(
        average_table,
        use_container_width=True,
        hide_index=True
    )

# =========================
# 5. 연도 선택
# =========================

st.divider()
st.header("📈 2. 연도별 최고기온 및 최저기온")

st.write("연도를 1개 선택하면 해당 연도를 분석하고, 2개 선택하면 두 연도를 비교합니다.")

years = sorted(df["연도"].unique().tolist())

if not years:
    st.error("분석할 연도 데이터가 없습니다.")
    st.stop()

selected_years = st.multiselect(
    "비교할 연도를 선택하세요. (최대 2개)",
    options=years,
    default=[years[-1]],
    max_selections=2,
    format_func=lambda year: str(year) + "년"
)

# =========================
# 6. 연도별 기온 그래프
# =========================

if len(selected_years) == 0:

    st.info("분석할 연도를 선택해 주세요.")

else:

    selected_years = sorted(selected_years)

    fig2 = go.Figure()

    line_styles = ["solid", "dash"]
    marker_symbols = ["circle", "diamond"]

    for index, year in enumerate(selected_years):

        year_df = df[df["연도"] == year]

        year_result = (
            year_df.groupby("월")
            .agg({
                "최고기온(℃)": "max",
                "최저기온(℃)": "min"
            })
            .reindex(month_ticks)
        )

        # 최고기온 - 연핑크
        fig2.add_trace(
            go.Scatter(
                x=month_ticks,
                y=year_result["최고기온(℃)"].values,
                mode="lines+markers",
                name=str(year) + "년 최고기온",
                line=dict(
                    color=PINK,
                    width=3,
                    dash=line_styles[index]
                ),
                marker=dict(
                    size=8,
                    color=PINK,
                    symbol=marker_symbols[index]
                ),
                connectgaps=False
            )
        )

        # 최저기온 - 연하늘
        fig2.add_trace(
            go.Scatter(
                x=month_ticks,
                y=year_result["최저기온(℃)"].values,
                mode="lines+markers",
                name=str(year) + "년 최저기온",
                line=dict(
                    color=SKY,
                    width=3,
                    dash=line_styles[index]
                ),
                marker=dict(
                    size=8,
                    color=SKY,
                    symbol=marker_symbols[index]
                ),
                connectgaps=False
            )
        )

    # 그래프 제목
    if len(selected_years) == 1:
        graph_title = str(selected_years[0]) + "년 월별 최고기온과 최저기온"
    else:
        graph_title = (
            str(selected_years[0]) + "년과 "
            + str(selected_years[1]) + "년 기온 비교"
        )

    fig2.update_layout(
        title=dict(
            text=graph_title,
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="월",
        yaxis_title="온도(℃)",
        legend_title="연도 및 기온 구분",
        height=560,
        template="plotly_white",
        hovermode="x unified"
    )

    fig2.update_xaxes(
        tickmode="array",
        tickvals=month_ticks,
        ticktext=month_labels
    )

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 7. 데이터 표
    # =========================

    st.subheader("📋 선택한 연도의 기온 데이터")

    table_list = []

    for year in selected_years:

        year_result = (
            df[df["연도"] == year]
            .groupby("월")
            .agg({
                "최고기온(℃)": "max",
                "최저기온(℃)": "min"
            })
            .reset_index()
        )

        year_result["연도"] = year
        year_result["월"] = year_result["월"].map(month_names)

        table_list.append(year_result)

    final_table = pd.concat(
        table_list,
        ignore_index=True
    )

    final_table = final_table[
        ["연도", "월", "최고기온(℃)", "최저기온(℃)"]
    ]

    st.dataframe(
        final_table,
        use_container_width=True,
        hide_index=True
    )

# =========================
# 8. 데이터 정보
# =========================

st.divider()
st.subheader("📌 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터 개수", str(len(df)) + "개")

with col2:
    st.metric(
        "분석 시작 연도",
        str(int(df["연도"].min())) + "년"
    )

with col3:
    st.metric(
        "분석 마지막 연도",
        str(int(df["연도"].max())) + "년"
    )

st.caption("자료: 업로드된 서울 기온 데이터")
