
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.linear_model import LinearRegression

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")
st.write("선형회귀 알고리즘을 활용하여 과거 기온을 분석하고 미래 기온을 예측합니다.")

st.divider()


# =====================================
# 2. CSV 파일 불러오기
# =====================================

@st.cache_data
def load_data():

    base_path = Path(__file__).resolve().parent

    possible_paths = [
        base_path / "temperature.csv",
        base_path / "temperature (1).csv",
        base_path.parent / "temperature.csv",
        base_path.parent / "temperature (1).csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 또는 temperature (1).csv 파일을 찾을 수 없습니다."
        )

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
    st.info(
        "GitHub 저장소에서 CSV 파일이 app.py와 같은 폴더에 있는지 확인해 주세요."
    )
    st.stop()


# =====================================
# 3. 데이터 전처리
# =====================================

df.columns = df.columns.astype(str).str.strip()

required_columns = ["일시", "평균기온(℃)"]

for col in required_columns:
    if col not in df.columns:
        st.error(f"CSV 파일에 {col} 열이 없습니다.")
        st.stop()

# 날짜 데이터 처리
month_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
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
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["일시", "평균기온(℃)"]
).copy()

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

df = df.sort_values("일시")

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()


# =====================================
# 4. 데이터 정보
# =====================================

st.subheader("📊 기온 데이터 정보")

info1, info2, info3 = st.columns(3)

with info1:
    st.metric("전체 데이터 수", f"{len(df):,}개")

with info2:
    st.metric("시작 연도", f"{df['연도'].min()}년")

with info3:
    st.metric("마지막 연도", f"{df['연도'].max()}년")


# =====================================
# 5. 사용자 입력
# =====================================

st.divider()

st.subheader("🔍 예측 조건 선택")

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

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        options=list(month_names.keys()),
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


# =====================================
# 6. 선택한 월의 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 2개 이상 필요합니다.")
    st.stop()


# =====================================
# 7. 선형회귀 모델 학습
# =====================================

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

model = LinearRegression()

model.fit(X, y)

prediction_data = pd.DataFrame({
    "연도": [prediction_year]
})

predicted_temperature = model.predict(
    prediction_data
)[0]


# =====================================
# 8. 회귀 추세선 계산
# =====================================

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


# =====================================
# 9. 예측 결과
# =====================================

st.divider()

st.subheader("🌡️ 기온 예측 결과")

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
    "※ 예측값은 과거 평균기온의 선형적인 변화 추세를 이용한 통계적 추정값입니다."
)


# =====================================
# 10. 실제 기온과 예측 기온 그래프
# =====================================

st.divider()

st.subheader(
    f"📈 {month_names[selected_month]} 연도별 평균기온 예측 그래프"
)

fig = go.Figure()

# 실제 평균기온
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
        "연도: %{x:.0f}년<br>추세선: %{y:.2f}℃<extra></extra>"
    )
)

# 예측 평균기온
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
    yaxis_title="평균기온(℃)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    showgrid=True,
    dtick=1
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 11. 그래프 읽는 방법
# =====================================

st.subheader("🎨 그래프 읽는 방법")

st.markdown(
    """
    - 🔵 **파란색 점:** 과거에 실제로 측정한 평균기온
    - 🔴 **빨간색 선:** 과거 데이터로 학습한 선형회귀 추세선
    - ⭐ **노란색 별:** 사용자가 입력한 연도의 예측 평균기온

    파란색 점들이 빨간색 선을 기준으로 얼마나 흩어져 있는지 살펴보세요.
    빨간색 선은 전체적인 기온 변화 방향을 보여주며,
    노란색 별은 이 추세를 미래 연도까지 연장했을 때의 예측 결과입니다.
    """
)


# =====================================
# 12. 선형회귀 알고리즘 설명
# =====================================

st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.write(
    """
    선형회귀는 과거에 수집한 데이터를 분석하여
    변수 사이의 관계를 직선으로 나타내고,
    그 관계를 이용해 새로운 값을 예측하는 머신러닝 알고리즘입니다.

    이번 프로그램에서는 연도와 평균기온 사이의 관계를 분석합니다.
    """
)

st.markdown("### ① 과거 데이터 학습")

st.write(
    f"""
    먼저 선택한 {month_names[selected_month]}의 과거 평균기온 데이터를 모읍니다.

    - 입력 변수 X: 연도
    - 예측 변수 Y: 평균기온

    예를 들어 과거 여러 해의 1월 평균기온을 모으면
    연도가 변할 때 기온이 어떤 방향으로 변하는지 분석할 수 있습니다.
    """
)

st.markdown("### ② 가장 적합한 직선 찾기")

st.write(
    """
    선형회귀는 실제 측정된 기온과 직선이 예측한 기온 사이의
    차이를 오차라고 생각합니다.

    이 오차들을 제곱해서 모두 더한 값이 가장 작아지도록
    직선의 기울기와 절편을 결정합니다.

    따라서 빨간색 선은 과거 기온의 전체적인 변화 경향을 나타냅니다.
    """
)

st.latex(r"\hat{y} = b_0 + b_1x")

st.write(
    """
    - X: 연도
    - ŷ: 예측한 평균기온
    - b₀: 직선의 절편
    - b₁: 직선의 기울기

    기울기가 양수이면 시간이 지날수록 기온이 높아지는 경향이고,
    음수이면 낮아지는 경향입니다.
    """
)

st.markdown("### ③ 미래 기온 예측")

st.write(
    f"""
    과거 데이터를 학습한 모델에 {prediction_year}년을 입력하면
    해당 연도의 {month_names[selected_month]} 예상 평균기온을 계산합니다.

    그래프에서 노란색 별표가 예측된 기온입니다.
    """
)

st.markdown("### ④ 실제 분석에 사용된 회귀식")

st.code(
    f"예측 평균기온 = {model.intercept_:.4f} "
    f"+ ({model.coef_[0]:.4f} × 연도)"
)

if model.coef_[0] > 0:

    st.success(
        f"분석 결과, 연도가 1년 증가할 때 "
        f"평균기온은 약 {model.coef_[0]:.3f}℃ "
        "높아지는 선형적 경향이 나타납니다."
    )

elif model.coef_[0] < 0:

    st.info(
        f"분석 결과, 연도가 1년 증가할 때 "
        f"평균기온은 약 {abs(model.coef_[0]):.3f}℃ "
        "낮아지는 선형적 경향이 나타납니다."
    )

else:

    st.info(
        "분석 결과, 연도에 따른 선형적인 기온 변화가 나타나지 않습니다."
    )


# =====================================
# 13. 예측 시 주의사항
# =====================================

st.divider()

st.subheader("⚠️ 예측 결과를 해석할 때 주의할 점")

st.write(
    """
    1. 선형회귀는 과거 데이터의 변화 경향을 바탕으로 예측합니다.
    2. 실제 기온은 기후 변화, 계절적 특성, 기상 현상 등에 따라 달라질 수 있습니다.
    3. 예측 연도가 과거 데이터 범위에서 멀어질수록 예측 오차가 커질 수 있습니다.
    4. 따라서 이 결과는 실제 기상 예보가 아닌 통계적인 예상 기온입니다.
    """
)

st.divider()

st.caption(
    "🌡️ 월별 평균기온 분석 및 선형회귀 예측 프로그램"
)
