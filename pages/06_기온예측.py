
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

# =========================
# 1. 페이지 설정
# =========================

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")
st.write("선형회귀 알고리즘을 활용하여 미래의 평균기온을 예측합니다.")

st.divider()

# =========================
# 2. CSV 파일 불러오기
# =========================

@st.cache_data
def load_data():
    file_path = Path(__file__).resolve().parent / "temperature.csv"

    if not file_path.exists():
        raise FileNotFoundError("temperature.csv 파일을 찾을 수 없습니다.")

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            return data
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

try:
    df = load_data()

except Exception as e:
    st.error(str(e))
    st.info("temperature.csv 파일을 app.py와 같은 폴더에 넣어 주세요.")
    st.stop()

# =========================
# 3. 데이터 전처리
# =========================

df.columns = df.columns.str.strip()

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일에 '일시', '평균기온(℃)' 열이 필요합니다.")
    st.stop()

df["일시"] = pd.to_datetime(
    df["일시"].astype(str).str.strip(),
    format="%b-%y",
    errors="coerce"
)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(subset=["일시", "평균기온(℃)"]).copy()

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()

# =========================
# 4. 사용자 입력
# =========================

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
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    latest_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=int(df["연도"].min()),
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

prediction_year = int(prediction_year)

# =========================
# 5. 선택한 월의 데이터 추출
# =========================

month_df = df[df["월"] == selected_month].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 2개 이상 있어야 예측할 수 있습니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# =========================
# 6. 선형회귀 모델 학습
# =========================

model = LinearRegression()

model.fit(X, y)

# 예측기온 계산
predicted_temperature = model.predict(
    pd.DataFrame({"연도": [prediction_year]})
)[0]

# =========================
# 7. 회귀 추세선 계산
# =========================

start_year = int(month_df["연도"].min())

end_year = max(
    int(month_df["연도"].max()),
    prediction_year
)

line_years = np.linspace(
    start_year,
    end_year,
    200
)

line_temperatures = model.predict(
    pd.DataFrame({"연도": line_years})
)

# =========================
# 8. 예측 결과 출력
# =========================

st.divider()

st.subheader("📌 기온 예측 결과")

result1, result2, result3 = st.columns(3)

with result1:
    st.metric(
        "선택한 월",
        month_names[selected_month]
    )

with result2:
    st.metric(
        "예측 연도",
        f"{prediction_year}년"
    )

with result3:
    st.metric(
        "예측 평균기온",
        f"{predicted_temperature:.2f} ℃"
    )

st.caption(
    "※ 예측값은 과거 평균기온의 선형적인 변화 추세를 바탕으로 계산한 값입니다."
)

# =========================
# 9. 실제 기온 + 회귀선 + 예측값 그래프
# =========================

st.divider()

st.subheader(
    f"📈 {month_names[selected_month]} 연도별 평균기온 및 예측 그래프"
)

fig = go.Figure()

# 실제 측정 기온
fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#3498DB",
            size=9
        ),
        hovertemplate=
        "연도: %{x}년<br>실제 평균기온: %{y:.2f}℃<extra></extra>"
    )
)

# 선형회귀 추세선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temperatures,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="#E74C3C",
            width=3
        ),
        hovertemplate=
        "연도: %{x:.0f}년<br>추세선 기온: %{y:.2f}℃<extra></extra>"
    )
)

# 예측 기온
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[predicted_temperature],
        mode="markers+text",
        name="예측 평균기온",
        marker=dict(
            color="#F1C40F",
            size=17,
            symbol="star",
            line=dict(
                color="#D35400",
                width=2
            )
        ),
        text=[f"{predicted_temperature:.2f}℃"],
        textposition="top center",
        hovertemplate=
        "예측 연도: %{x}년<br>예측 평균기온: %{y:.2f}℃<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    template="plotly_white"
)

fig.update_xaxes(
    showgrid=True,
    dtick=1
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 10. 선형회귀 알고리즘 설명
# =========================

st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.write(
    """
    선형회귀는 과거에 수집한 데이터를 분석하여
    두 변수 사이의 관계를 직선으로 나타내고,
    이를 바탕으로 새로운 값을 예측하는 머신러닝 알고리즘입니다.
    """
)

st.markdown("### ① 데이터 학습")

st.write(
    f"""
    이번 프로그램에서는 **연도**를 입력 변수(X)로,
    **평균기온**을 예측 변수(Y)로 사용합니다.

    선택한 {month_names[selected_month]}의 과거 평균기온 데이터를
    선형회귀 모델에 학습시킵니다.
    """
)

st.markdown("### ② 가장 적합한 직선 찾기")

st.write(
    """
    그래프에 표시된 빨간색 직선은 과거 데이터의 전체적인
    변화 경향을 가장 잘 나타내는 회귀선입니다.

    선형회귀는 실제 측정값과 직선이 예측한 값 사이의
    차이(오차)를 제곱하여 모두 더한 값이
    가장 작아지도록 직선을 결정합니다.
    """
)

st.latex(r"\hat{y} = b_0 + b_1x")

st.write(
    """
    - X : 연도
    - ŷ : 예측한 평균기온
    - b₀ : 직선의 절편
    - b₁ : 연도가 1년 증가할 때 변하는 평균기온의 정도
    """
)

st.markdown("### ③ 미래 기온 예측")

st.write(
    f"""
    학습된 회귀선에 사용자가 입력한 {prediction_year}년을 대입하면
    해당 연도 {month_names[selected_month]}의 예상 평균기온을 계산합니다.

    그래프의 노란색 별표가 바로 예측된 기온입니다.
    """
)

st.markdown("### ④ 이번 분석의 회귀식")

st.code(
    f"예측 평균기온 = {model.intercept_:.4f} "
    f"+ ({model.coef_[0]:.4f} × 연도)"
)

if model.coef_[0] > 0:
    st.info(
        f"분석 결과, 연도가 1년 증가할 때 "
        f"평균기온은 약 {model.coef_[0]:.3f}℃ 높아지는 경향을 보입니다."
    )
elif model.coef_[0] < 0:
    st.info(
        f"분석 결과, 연도가 1년 증가할 때 "
        f"평균기온은 약 {abs(model.coef_[0]):.3f}℃ 낮아지는 경향을 보입니다."
    )
else:
    st.info("분석 결과, 연도에 따른 뚜렷한 선형 변화가 나타나지 않습니다.")

# =========================
# 11. 주의사항
# =========================

st.divider()

st.subheader("⚠️ 예측 시 주의사항")

st.write(
    """
    - 선형회귀는 과거 데이터의 경향을 바탕으로 미래를 예측합니다.
    - 실제 기온은 계절 변화, 기후 변화, 기상 현상 등에 따라 달라질 수 있습니다.
    - 예측 연도가 과거 데이터의 범위를 크게 벗어날수록 예측의 신뢰도가 낮아질 수 있습니다.
    - 따라서 예측 결과는 실제 기온이 아닌 통계적인 추정값입니다.
    """
)

st.caption("기온 데이터 기반 선형회귀 예측 프로그램")
