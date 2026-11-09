```python
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
st.write("원하는 월을 선택하여 전체 연도의 최고기온과 최저기온을 비교해 보세요.")

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
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
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

result = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최
