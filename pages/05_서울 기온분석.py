import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요.")

# CSV 파일 불러오기
file_path = Path(__file__).parent / "temperature.csv"

if not file_path.exists():
    file_path = Path(__file__).parent.parent / "temperature.csv"

if not file_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

# 한글 인코딩 처리
try:
    df = pd.read_csv(file_path, encoding="cp949")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_path, encoding="euc-kr")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

# 날짜 처리
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df = df.dropna(subset=["일시"])

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

# 기온 숫자 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# 월 선택
st.subheader("📅 분석할 월 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "월을 선택하세요.",
    list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# 선택한 월 데이터
month_df = df[df["월"] == selected_month].copy()

if month_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# 연도별 최고기온과 최저기온
result = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

# 그래프
st.divider()

fig = go.Figure()

# 최고기온 - 연핑크
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="#FFB6C1", width=3),
        marker=dict(size=8, color="#FFB6C1")
    )
)

# 최저기온 - 연하늘
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="#ADD8E6", width=3),
        marker=dict(size=8, color="#ADD8E6")
    )
)

fig.update_layout(
    title={
        "text": "월별 기온분석",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="연도",
    yaxis_title="온도(℃)",
    legend_title="기온 구분",
    hovermode="x unified",
    height=550,
    template="plotly_white"
)

fig.update_xaxes(dtick=1)

st.plotly_chart(fig, use_container_width=True)

# 데이터 표
st.divider()

st.subheader(
    f"📊 {month_names[selected_month]} 연도별 기온 데이터"
)

st.dataframe(
    result,
    use_container_width=True,
    hide_index=True
)

# 요약 분석
st.divider()

col1, col2 = st.columns(2)

with col1:
    max_row = result.loc[result["최고기온(℃)"].idxmax()]

    st.metric(
        "🔥 역대 가장 높은 최고기온",
        f"{max_row['최고기온(℃)']}℃",
        f"{int(max_row['연도'])}년"
    )

with col2:
    min_row = result.loc[result["최저기온(℃)"].idxmin()]

    st.metric(
        "❄️ 역대 가장 낮은 최저기온",
        f"{min_row['최저기온(℃)']}℃",
        f"{int(min_row['연도'])}년"
    )
