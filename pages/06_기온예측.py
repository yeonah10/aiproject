
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")

st.write(
    "다양한 회귀 알고리즘을 활용하여 과거 기온을 분석하고 "
    "미래의 평균기온을 예측합니다."
)

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


# =====================================
# 3. 데이터 전처리
# =====================================

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
        value = str(value).strip()

        # Jan-07 형식 처리
        try:
            return pd.to_datetime(
                value,
                format="%b-%y"
            )
        except ValueError:
            pass

        # 그 외 날짜 형식 처리
        return pd.to_datetime(value, errors="coerce")

    except Exception:
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
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# =====================================
# 4. 데이터 정보
# =====================================

st.subheader("📊 기온 데이터 정보")

col1, col2, col3 = st.columns(3)

col1.metric(
    "전체 데이터 수",
    f"{len(df):,}개"
)

col2.metric(
    "시작 연도",
    f"{df['연도'].min()}년"
)

col3.metric(
    "마지막 연도",
    f"{df['연도'].max()}년"
)


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


# =====================================
# 6. 회귀 알고리즘 선택
# =====================================

st.divider()

st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = {
    "선형회귀": "Linear Regression",
    "다항회귀": "Polynomial Regression",
    "랜덤 포레스트 회귀": "Random Forest Regression"
}

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    list(algorithm_names.keys())
)

st.caption(
    "알고리즘을 변경하면 같은 기온 데이터에서도 "
    "서로 다른 예측 결과를 확인할 수 있습니다."
)


# =====================================
# 7. 선택한 월의 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("예측을 위해 선택한 월의 데이터가 3개 이상 필요합니다.")
    st.stop()


X = month_df[["연도"]]
y = month_df["평균기온(℃)"]


# =====================================
# 8. 세 가지 회귀 모델 생성
# =====================================

models = {

    "선형회귀": LinearRegression(),

    "다항회귀": make_pipeline(
        PolynomialFeatures(degree=2),
        LinearRegression()
    ),

    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42
    )

}


# =====================================
# 9. 모든 알고리즘 학습 및 예측
# =====================================

prediction_data = pd.DataFrame({
    "연도": [prediction_year]
})

results = {}

for name, model in models.items():

    model.fit(X, y)

    predicted_value = model.predict(
        prediction_data
    )[0]

    results[name] = float(predicted_value)


# 선택한 알고리즘의 예측값
predicted_temperature = results[selected_algorithm]

selected_model = models[selected_algorithm]


# =====================================
# 10. 추세선 데이터 생성
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

line_data = pd.DataFrame({
    "연도": line_years
})


# =====================================
# 11. 예측 결과 출력
# =====================================

st.divider()

st.subheader("🌡️ 선택한 알고리즘의 예측 결과")

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택한 월",
    month_names[selected_month]
)

col2.metric(
    "예측 연도",
    f"{prediction_year}년"
)

col3.metric(
    "예측 평균기온",
    f"{predicted_temperature:.2f} ℃"
)

st.success(
    f"{selected_algorithm}을 사용한 "
    f"{prediction_year}년 {month_names[selected_month]} "
    f"예상 평균기온은 {predicted_temperature:.2f}℃입니다."
)


# =====================================
# 12. 알고리즘별 예측값 비교
# =====================================

st.divider()

st.subheader("📊 알고리즘별 예측 결과 비교")

st.write(
    "같은 월과 같은 연도를 기준으로 "
    "세 가지 알고리즘이 예측한 결과를 비교합니다."
)

comparison_df = pd.DataFrame({
    "회귀 알고리즘": list(results.keys()),
    "예측 평균기온(℃)": [
        round(value, 2)
        for value in results.values()
    ]
})

comparison_df["선택 여부"] = comparison_df[
    "회귀 알고리즘"
].apply(
    lambda x: "⭐ 선택한 알고리즘" if x == selected_algorithm else ""
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

# 가장 높은 값과 낮은 값의 차이
temperature_difference = (
    max(results.values()) - min(results.values())
)

st.metric(
    "알고리즘별 예측값 차이",
    f"{temperature_difference:.2f} ℃"
)


# =====================================
# 13. 세 가지 알고리즘 비교 그래프
# =====================================

st.divider()

st.subheader(
    f"📈 {month_names[selected_month]} 회귀 알고리즘 비교 그래프"
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
        )
    )
)


# 알고리즘별 색상
algorithm_colors = {
    "선형회귀": "#E74C3C",
    "다항회귀": "#2ECC71",
    "랜덤 포레스트 회귀": "#9B59B6"
}


# 세 가지 추세선
for name, model in models.items():

    line_temperatures = model.predict(line_data)

    is_selected = name == selected_algorithm

    fig.add_trace(
        go.Scatter(
            x=line_years,
            y=line_temperatures,
            mode="lines",
            name=f"{name} 추세선",
            line=dict(
                color=algorithm_colors[name],
                width=4 if is_selected else 2,
                dash="solid" if is_selected else "dash"
            ),
            opacity=1.0 if is_selected else 0.65
        )
    )


# 알고리즘별 예측 지점
for name, value in results.items():

    is_selected = name == selected_algorithm

    fig.add_trace(
        go.Scatter(
            x=[prediction_year],
            y=[value],
            mode="markers+text",
            name=f"{name} 예측값",
            marker=dict(
                color=algorithm_colors[name],
                size=16 if is_selected else 10,
                symbol="star" if is_selected else "circle",
                line=dict(
                    color="black",
                    width=1 if is_selected else 0
                )
            ),
            text=[
                f"{value:.2f}℃" if is_selected else ""
            ],
            textposition="top center"
        )
    )


# 5년 단위 연도 표시
tick_years = list(
    range(start_year, end_year + 1, 5)
)

if end_year not in tick_years:
    tick_years.append(end_year)


fig.update_layout(
    height=600,
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

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 14. 그래프 읽는 방법
# =====================================

st.subheader("🎨 그래프 읽는 방법")

st.markdown("""
- 🔵 **파란색 점:** 과거 실제 평균기온
- 🔴 **빨간색 선:** 선형회귀 추세선
- 🟢 **초록색 선:** 다항회귀 추세선
- 🟣 **보라색 선:** 랜덤 포레스트 회귀 추세선
- ⭐ **별표:** 현재 선택한 알고리즘의 예측값

선의 모양과 별표의 위치를 비교하면
알고리즘에 따라 예측 결과가 어떻게 달라지는지 확인할 수 있습니다.
""")


# =====================================
# 15. 알고리즘별 작동 원리 설명
# =====================================

st.divider()

st.subheader("📚 회귀 알고리즘 작동 원리")


# 1. 선형회귀

with st.expander("① 선형회귀 (Linear Regression)", expanded=True):

    st.write("""
    선형회귀는 과거 데이터의 전체적인 변화 경향을
    직선으로 나타내는 알고리즘입니다.

    실제 측정값과 직선이 예측한 값 사이의 오차 제곱합이
    가장 작아지도록 직선을 결정합니다.
    """)

    st.latex(r"\hat{y} = b_0 + b_1x")

    st.write("""
    - X: 연도
    - ŷ: 예측 평균기온
    - b₀: 절편
    - b₁: 기울기

    직선의 기울기를 통해 기온이 장기적으로
    높아지는지 낮아지는지 확인할 수 있습니다.
    """)


# 2. 다항회귀

with st.expander("② 다항회귀 (Polynomial Regression)"):

    st.write("""
    다항회귀는 직선만으로 표현하기 어려운
    데이터의 곡선 형태 변화를 분석하는 알고리즘입니다.

    이번 프로그램에서는 2차 다항회귀를 사용합니다.
    연도뿐 아니라 연도의 제곱 항까지 활용하여
    곡선 형태의 추세선을 만듭니다.
    """)

    st.latex(r"\hat{y} = b_0 + b_1x + b_2x^2")

    st.write("""
    - X: 연도
    - X²: 연도의 제곱
    - b₀, b₁, b₂: 모델이 학습한 계수

    따라서 선형회귀와 달리 기온 변화가
    휘어지는 형태로 나타날 수 있습니다.
    """)


# 3. 랜덤 포레스트

with st.expander("③ 랜덤 포레스트 회귀 (Random Forest Regression)"):

    st.write("""
    랜덤 포레스트는 여러 개의 의사결정나무를 만들어
    각각 예측한 결과를 평균하여 최종 값을 결정하는 알고리즘입니다.

    하나의 나무에만 의존하지 않고 여러 나무의 결과를
    결합한다는 특징이 있습니다.
    """)

    st.latex(
        r"\hat{y} = \frac{1}{N}\sum_{i=1}^{N} T_i(x)"
    )

    st.write("""
    - N: 의사결정나무의 개수
    - Tᵢ(x): 각각의 나무가 예측한 값
    - ŷ: 모든 나무의 예측값 평균

    이번 프로그램에서는 300개의 의사결정나무를
    결합하여 예측합니다.
    """)


# =====================================
# 16. 알고리즘 비교 설명
# =====================================

st.divider()

st.subheader("🔎 세 가지 알고리즘의 차이점")

difference_df = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트 회귀"
    ],
    "분석 방식": [
        "직선 형태",
        "곡선 형태",
        "여러 의사결정나무 결합"
    ],
    "특징": [
        "전체적인 변화 추세 분석",
        "비선형적인 변화 분석",
        "복잡한 데이터 패턴 분석"
    ]
})

st.dataframe(
    difference_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "세 알고리즘은 데이터를 분석하는 방식이 서로 다르기 때문에 "
    "같은 연도와 월을 입력해도 예측값이 달라질 수 있습니다."
)


# =====================================
# 17. 예측 결과 해석 시 주의사항
# =====================================

st.divider()

st.subheader("⚠️ 예측 결과 해석 시 주의사항")

st.write("""
1. 모든 예측 결과는 과거 기온 데이터에 기반한 통계적 추정값입니다.
2. 실제 기온은 기후 변화와 기상 현상 등에 따라 달라질 수 있습니다.
3. 선형회귀와 다항회귀는 과거 추세를 미래로 연장하므로 장기 예측에 오차가 발생할 수 있습니다.
4. 랜덤 포레스트는 학습 데이터 범위를 벗어난 미래 값을 예측할 때 과거 기온 범위 안에서만 결과가 나타나는 특성이 있습니다.
5. 따라서 예측값이 가장 높거나 낮다고 해서 해당 알고리즘이 가장 정확하다는 의미는 아닙니다.
""")

st.divider()

st.caption(
    "🌡️ 월별 평균기온 분석 및 3가지 회귀 알고리즘 비교 프로그램"
)
