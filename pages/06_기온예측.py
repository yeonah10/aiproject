
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")
st.write("선형회귀 알고리즘을 활용하여 과거 기온을 분석하고 미래 기온을 예측합니다.")

st.divider()


# 1. CSV 파일 불러오기

@st.cache_data
def load_data():

    base_path = Path(__file__).resolve().parent

    possible_paths = [
        base_path / "temperature.csv",
        base_path / "temperature (1).csv",
        base_path.parent / "temperature.csv",
        base_path.parent / "temperature (1).csv"
    ]

    file_path = next(
        (path for path in possible_paths if path.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일 인코딩을 확인해 주세요.")


try:
    df = load_data()

except Exception as e:
    st.error(str(e))
    st.stop()


# 2. 데이터 전처리

df.columns = df.columns.astype(str).str.strip()

if "일시" not in df.columns or "평균기온(℃)" not in df.columns:
    st.error("CSV 파일에 일시와 평균기온(℃) 열이 필요합니다.")
    st.stop()

month_dict = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def convert_date(value):
    try:
        month_text, year_text = str(value).strip().split("-")
        month = month_dict[month_text.title()]
        year = 2000 + int(year_text)
        return pd.Timestamp(year=year, month=month, day=1)
    except (ValueError, KeyError, TypeError):
        return pd.NaT


df["일시"] = df["일시"].apply(convert_date)
df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"], errors="coerce"
)

df = df.dropna(
    subset=["일시", "평균기온(℃)"]
).copy()

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month
df = df.sort_values("일시")

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# 3. 데이터 정보

st.subheader("📊 기온 데이터 정보")

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터 수", f"{len(df):,}개")
col2.metric("시작 연도", f"{df['연도'].min()}년")
col3.metric("마지막 연도", f"{df['연도'].max()}년")


# 4. 사용자 입력

st.divider()
st.subheader("🔍 예측 조건 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=int(df["연도"].min()),
        max_value=2100,
        value=int(df["연도"].max()) + 1,
        step=1
    )

prediction_year = int(prediction_year)


# 5. 선택한 월 데이터

month_df = df[df["월"] == selected_month].copy()
month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 2개 이상 필요합니다.")
    st.stop()


# 6. 선형회귀 학습

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

model = LinearRegression()
model.fit(X, y)

predicted_temperature = model.predict(
    pd.DataFrame({"연도": [prediction_year]})
)[0]


# 7. 추세선 계산

start_year = int(month_df["연도"].min())
end_year = max(int(month_df["연도"].max()), prediction_year)

line_years = np.linspace(start_year, end_year, 200)

line_temperatures = model.predict(
    pd.DataFrame({"연도": line_years})
)


# 8. 예측 결과

st.divider()
st.subheader("🌡️ 기온 예측 결과")

col1, col2, col3 = st.columns(3)

col1.metric("선택한 월", month_names[selected_month])
col2.metric("예측 연도", f"{prediction_year}년")
col3.metric("예측 평균기온", f"{predicted_temperature:.2f} ℃")

st.caption("※ 과거 평균기온의 선형적인 변화 추세를 이용한 통계적 예측값입니다.")


# 9. 그래프

st.divider()

st.subheader(
    f"📈 {month_names[selected_month]} 연도별 평균기온 예측 그래프"
)

fig = go.Figure()

# 실제 평균기온
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(color="#3498DB", size=9)
))

# 선형회귀 추세선
fig.add_trace(go.Scatter(
    x=line_years,
    y=line_temperatures,
    mode="lines",
    name="선형회귀 추세선",
    line=dict(color="#E74C3C", width=3)
))

# 예측 기온
fig.add_trace(go.Scatter(
    x=[prediction_year],
    y=[predicted_temperature],
    mode="markers+text",
    name="예측 평균기온",
    marker=dict(
        color="#F1C40F",
        size=17,
        symbol="star",
        line=dict(color="#D35400", width=2)
    ),
    text=[f"{predicted_temperature:.2f}℃"],
    textposition="top center"
))

# ★ 연도 표시 수정: 5년 단위로 가로 표시
tick_years = list(
    range(start_year, end_year + 1, 5)
)

if end_year not in tick_years:
    tick_years.append(end_year)

fig.update_layout(
    height=550,
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(b=70)
)

fig.update_xaxes(
    showgrid=True,
    tickmode="array",
    tickvals=tick_years,
    ticktext=[str(year) for year in tick_years],
    tickangle=0,
    automargin=True
)

fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)


# 10. 그래프 읽는 방법

st.subheader("🎨 그래프 읽는 방법")

st.markdown("""
- 🔵 **파란색 점:** 과거 실제 평균기온
- 🔴 **빨간색 선:** 선형회귀 추세선
- ⭐ **노란색 별:** 예측 평균기온

파란색 점들의 전체적인 흐름을 빨간색 선이 나타내며,
노란색 별은 해당 추세를 이용해 계산한 미래 기온입니다.
""")


# 11. 선형회귀 설명

st.divider()
st.subheader("📚 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거에 수집한 데이터를 분석하여 변수 사이의 관계를
직선으로 나타내고, 그 관계를 이용해 새로운 값을 예측하는
머신러닝 알고리즘입니다.

이번 프로그램에서는 연도와 평균기온 사이의 관계를 분석합니다.
""")

st.markdown("### ① 과거 데이터 학습")

st.write(f"""
선택한 {month_names[selected_month]}의 과거 평균기온 데이터를 모읍니다.

- 입력 변수 X: 연도
- 예측 변수 Y: 평균기온

과거 여러 해의 같은 월 데이터를 비교하여 기온의 변화 경향을 분석합니다.
""")

st.markdown("### ② 가장 적합한 직선 찾기")

st.write("""
선형회귀는 실제 측정된 기온과 직선이 예측한 기온 사이의
오차를 제곱하여 모두 더한 값이 가장 작아지도록
직선의 기울기와 절편을 결정합니다.

빨간색 선이 바로 이러한 과정을 통해 만들어진 회귀선입니다.
""")

st.latex(r"\hat{y} = b_0 + b_1x")

st.write("""
- X: 연도
- ŷ: 예측 평균기온
- b₀: 직선의 절편
- b₁: 직선의 기울기
""")

st.markdown("### ③ 미래 기온 예측")

st.write(f"""
학습된 모델에 {prediction_year}년을 입력하면
해당 연도 {month_names[selected_month]}의 예상 평균기온을 계산합니다.

그래프의 노란색 별표가 예측 결과입니다.
""")

st.markdown("### ④ 실제 분석에 사용된 회귀식")

st.code(
    f"예측 평균기온 = {model.intercept_:.4f} "
    f"+ ({model.coef_[0]:.4f} × 연도)"
)

if model.coef_[0] > 0:
    st.info(
        f"연도가 1년 증가할 때 평균기온은 약 "
        f"{model.coef_[0]:.3f}℃ 높아지는 경향입니다."
    )
elif model.coef_[0] < 0:
    st.info(
        f"연도가 1년 증가할 때 평균기온은 약 "
        f"{abs(model.coef_[0]):.3f}℃ 낮아지는 경향입니다."
    )
else:
    st.info("연도에 따른 선형적인 기온 변화가 나타나지 않습니다.")


# 12. 주의사항

st.divider()
st.subheader("⚠️ 예측 결과 해석 시 주의사항")

st.write("""
1. 선형회귀는 과거 데이터의 변화 경향을 바탕으로 예측합니다.
2. 실제 기온은 기후 변화와 기상 현상 등에 따라 달라질 수 있습니다.
3. 과거 데이터 범위에서 멀리 떨어진 연도를 예측할수록 오차가 커질 수 있습니다.
4. 따라서 예측 결과는 실제 기상 예보가 아닌 통계적인 추정값입니다.
""")

st.divider()
st.caption("🌡️ 월별 평균기온 분석 및 선형회귀 예측 프로그램")
