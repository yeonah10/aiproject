
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# =========================
# 1. 기본 화면 설정
# =========================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 머신러닝이 붓꽃의 품종을 예측합니다.")

st.divider()

# =========================
# 2. 데이터 불러오기
# =========================

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Iris.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "Iris.csv 파일을 app.py와 같은 폴더에 넣어주세요."
        )

    encodings = ["cp949", "euc-kr", "utf-8-sig", "latin1"]

    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            return data
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

try:
    df = load_data()

except Exception as e:
    st.error(str(e))
    st.stop()

# 필요한 컬럼 확인
required_columns = ["꽃잎길이", "꽃잎너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 컬럼명을 확인해주세요.")
    st.stop()

df = df.dropna(subset=required_columns).copy()

# 숫자형 데이터 변환
df["꽃잎길이"] = pd.to_numeric(df["꽃잎길이"], errors="coerce")
df["꽃잎너비"] = pd.to_numeric(df["꽃잎너비"], errors="coerce")
df = df.dropna(subset=["꽃잎길이", "꽃잎너비"])

# =========================
# 3. 입력 범위 확인
# =========================

length_min = float(df["꽃잎길이"].min())
length_max = float(df["꽃잎길이"].max())

width_min = float(df["꽃잎너비"].min())
width_max = float(df["꽃잎너비"].max())

st.subheader("📌 입력 가능한 데이터 범위")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "꽃잎 길이",
        f"{length_min:.1f} ~ {length_max:.1f} cm"
    )

with col2:
    st.metric(
        "꽃잎 너비",
        f"{width_min:.1f} ~ {width_max:.1f} cm"
    )

st.info(
    "위 범위는 업로드한 Iris.csv 데이터에서 확인한 실제 최솟값과 최댓값입니다."
)

st.divider()

# =========================
# 4. 머신러닝 학습
# =========================

X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X, y)

# =========================
# 5. 사용자 입력
# =========================

st.subheader("✏️ 꽃잎 크기 입력")

input_col1, input_col2 = st.columns(2)

with input_col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=4.3,
        step=0.1,
        format="%.1f"
    )

with input_col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=1.3,
        step=0.1,
        format="%.1f"
    )

predict_button = st.button(
    "🌸 품종 예측하기",
    type="primary",
    use_container_width=True
)

# =========================
# 6. 품종 예측
# =========================

if predict_button:

    input_data = pd.DataFrame({
        "꽃잎길이": [petal_length],
        "꽃잎너비": [petal_width]
    })

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    classes = model.classes_

    # 예측 결과
    st.divider()
    st.subheader("🔍 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.write(
        f"입력한 꽃잎 길이는 **{petal_length:.1f}cm**, "
        f"꽃잎 너비는 **{petal_width:.1f}cm**입니다."
    )

    # =========================
    # 7. 품종별 예측 확률
    # =========================

    st.subheader("📊 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": classes,
        "예측 확률 (%)": probabilities * 100
    })

    probability_df["예측 확률 (%)"] = (
        probability_df["예측 확률 (%)"].round(2)
    )

    fig_probability = go.Figure()

    fig_probability.add_trace(
        go.Bar(
            x=probability_df["품종"],
            y=probability_df["예측 확률 (%)"],
            text=probability_df["예측 확률 (%)"].apply(
                lambda x: f"{x:.2f}%"
            ),
            textposition="outside",
            marker_color=["#F4A6B8", "#91C8E4", "#B8A1D9"]
        )
    )

    fig_probability.update_layout(
        yaxis_title="예측 확률 (%)",
        xaxis_title="붓꽃 품종",
        yaxis=dict(range=[0, 115]),
        height=400
    )

    st.plotly_chart(
        fig_probability,
        use_container_width=True
    )

    # =========================
    # 8. 결정 영역 시각화
    # =========================

    st.subheader("🌈 꽃잎 크기에 따른 품종 분류 그래프")

    st.write(
        "배경색은 머신러닝이 학습한 품종별 분류 영역이며, "
        "초록색 별은 사용자가 입력한 꽃잎 크기입니다."
    )

    # 그래프 범위
    x_min = length_min - 0.3
    x_max = length_max + 0.3

    y_min = width_min - 0.2
    y_max = width_max + 0.2

    # 격자 생성
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 180),
        np.linspace(y_min, y_max, 180)
    )

    grid_data = pd.DataFrame({
        "꽃잎길이": xx.ravel(),
        "꽃잎너비": yy.ravel()
    })

    # 격자마다 품종 예측
    grid_predictions = model.predict(grid_data)

    # 품종을 숫자로 변환
    class_mapping = {
        name: i for i, name in enumerate(classes)
    }

    zz = np.array([
        class_mapping[name] for name in grid_predictions
    ]).reshape(xx.shape)

    colors = ["#F4A6B8", "#91C8E4", "#B8A1D9"]

    # 그래프 생성
    fig = go.Figure()

    # 품종별 배경 영역
    fig.add_trace(
        go.Heatmap(
            x=np.linspace(x_min, x_max, 180),
            y=np.linspace(y_min, y_max, 180),
            z=zz,
            colorscale=[
                [0.0, colors[0]],
                [0.3333, colors[0]],
                [0.3334, colors[1]],
                [0.6666, colors[1]],
                [0.6667, colors[2]],
                [1.0, colors[2]]
            ],
            showscale=False,
            opacity=0.35,
            hoverinfo="skip"
        )
    )

    # 기존 데이터 표시
    for i, species in enumerate(classes):

        species_data = df[df["품종"] == species]

        fig.add_trace(
            go.Scatter(
                x=species_data["꽃잎길이"],
                y=species_data["꽃잎너비"],
                mode="markers",
                name=species,
                marker=dict(
                    size=8,
                    color=colors[i],
                    line=dict(width=0.5, color="black")
                ),
                hovertemplate=(
                    "품종: " + species +
                    "<br>꽃잎 길이: %{x}cm" +
                    "<br>꽃잎 너비: %{y}cm"
                    "<extra></extra>"
                )
            )
        )

    # 사용자가 입력한 위치
    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers",
            name="내가 입력한 값",
            marker=dict(
                symbol="star",
                size=25,
                color="#00AA00",
                line=dict(width=2, color="darkgreen")
            ),
            hovertemplate=(
                "내가 입력한 값" +
                "<br>꽃잎 길이: %{x}cm" +
                "<br>꽃잎 너비: %{y}cm" +
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        xaxis_title="꽃잎 길이 (cm)",
        yaxis_title="꽃잎 너비 (cm)",
        height=650,
        legend_title="품종",
        hovermode="closest"
    )

    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max])

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =========================
    # 9. 예측 이유 설명
    # =========================

    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎 크기가 그래프에서 "
        f"**{prediction}의 분류 영역**에 위치하기 때문에 "
        f"해당 품종으로 예측되었습니다."
    )

    best_probability = max(probabilities) * 100

    st.info(
        f"랜덤 포레스트의 여러 결정트리가 투표한 결과, "
        f"가장 높은 예측 확률은 {best_probability:.2f}%입니다."
    )

    st.caption(
        "참고: 예측 확률은 모델의 학습 결과를 바탕으로 계산한 값이며, "
        "실제 품종일 확률을 보장하는 것은 아닙니다."
    )

else:
    st.info("꽃잎 길이와 너비를 입력한 다음 '품종 예측하기' 버튼을 눌러주세요.")
