import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =========================
# 1. 페이지 설정
# =========================

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 전체 연도의 최고기온과 최저기온을 비교할 수 있습니다.")

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
except Exception:
    try:
        df = pd.read_csv(file_path, encoding="euc-kr")
    except Exception as e:
        st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
        st.stop()

# =========================
# 3. 날짜 데이터 처리
# =========================

df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df = df.dropna(subset=["일시"])

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

# 기온 데이터 숫자 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# =========================
# 4. 월 선택
# =========================

st.subheader("📅 분석할 월 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# =========================
# 5. 선택한 월 데이터 분석
# =========================

month_df = df[df["월"] == selected_month].copy()

if month_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# 연도별 최고기온과 최저기온 정리
result = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

# =========================
# 6. 기온 그래프
# =========================

st.divider()

fig = go.Figure()

# 최고기온 - 빨간색
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="red", width=3),
        marker=dict(size=8)
    )
)

# 최저기온 - 파란색
fig.add_trace(
    go.Scatter(
        x=result["연도"],
        y=result["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="blue", width=3),
        marker=dict(size=8)
    )
)

# 그래프 제목 및 설정
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

fig.update_xaxes(
    dtick=1
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 7. 데이터 표
# =========================

st.divider()

st.subheader(f"📊 {month_names[selected_month]} 연도별 기온 데이터")

display_df = result.rename(columns={
    "연도": "연도",
    "최고기온(℃)": "최고기온(℃)",
    "최저기온(℃)": "최저기온(℃)"
})

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =========================
# 8. 요약 분석
# =========================

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
