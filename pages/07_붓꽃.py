
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


# =====================================
# 1. 화면 설정
# =====================================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")

st.write(
    "꽃잎의 길이와 너비를 입력하고 "
    "분류 알고리즘을 선택하면 붓꽃의 품종을 예측합니다."
)

st.divider()


# =====================================
# 2. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더
    base_path = Path(__file__).resolve().parent.parent

    file_path = base_path / "Iris.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Iris.csv 파일을 찾을 수 없습니다.\n"
            f"검색 위치: {file_path}"
        )

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:

        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            return data

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일 인코딩을 확인해주세요.")


try:
    df = load_data()

except Exception as e:
    st.error(str(e))
    st.stop()


# =====================================
# 3. 데이터 전처리
# =====================================

required_columns = [
    "꽃잎길이",
    "꽃잎너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):

    st.error("CSV 파일의 컬럼명을 확인해주세요.")

    st.write("현재 컬럼:", df.columns.tolist())

    st.stop()


df["꽃잎길이"] = pd.to_numeric(
    df["꽃잎길이"],
    errors="coerce"
)

df["꽃잎너비"] = pd.to_numeric(
    df["꽃잎너비"],
    errors="coerce"
)

df = df.dropna(
    subset=required_columns
).copy()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# =====================================
# 4. 입력 가능한 범위
# =====================================

length_min = float(df["꽃잎길이"].min())
length_max = float(df["꽃잎길이"].max())

width_min = float(df["꽃잎너비"].min())
width_max = float(df["꽃잎너비"].max())

st.subheader("📌 입력 가능한 꽃잎 크기")

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
    "입력 범위는 Iris.csv 데이터의 실제 최솟값과 최댓값입니다."
)

st.divider()


# =====================================
# 5. 알고리즘 선택
# =====================================

st.subheader("🤖 분류 알고리즘 선택")

algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요.",
    [
        "랜덤 포레스트 (Random Forest)",
        "K-최근접 이웃 (KNN)",
        "서포트 벡터 머신 (SVM)"
    ]
)


# =====================================
# 6. 알고리즘 설명
# =====================================

st.subheader("📚 알고리즘 설명")

if algorithm == "랜덤 포레스트 (Random Forest)":

    st.info(
        """
        🌳 랜덤 포레스트 (Random Forest)

        여러 개의 결정트리를 만들어 각각 예측한 결과를
        종합하여 최종 품종을 결정하는 알고리즘입니다.

        • 여러 결정트리의 투표를 활용합니다.
        • 복잡한 데이터도 분류할 수 있습니다.
        • 이번 프로그램에서는 300개의 결정트리를 사용합니다.
        """
    )

elif algorithm == "K-최근접 이웃 (KNN)":

    st.info(
        """
        📍 K-최근접 이웃 (KNN)

        새로운 데이터와 가장 가까운 기존 데이터 5개를 찾아
        주변 데이터의 품종을 기준으로 분류하는 알고리즘입니다.

        • 데이터 사이의 거리를 이용합니다.
        • 가까운 데이터의 영향을 많이 받습니다.
        • 이해하기 쉽고 직관적인 알고리즘입니다.
        """
    )

else:

    st.info(
        """
        📐 서포트 벡터 머신 (SVM)

        데이터 사이에 적절한 분류 경계를 만들어
        새로운 데이터의 품종을 구분하는 알고리즘입니다.

        • 품종을 구분하는 경계를 학습합니다.
        • RBF 커널을 사용하여 복잡한 경계도 학습할 수 있습니다.
        • 데이터의 크기 차이를 줄이기 위해 표준화를 적용합니다.
        """
    )


# =====================================
# 7. 알고리즘별 모델 생성
# =====================================

X = df[["꽃잎길이", "꽃잎너비"]]

y = df["품종"]

if algorithm == "랜덤 포레스트 (Random Forest)":

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42
    )

elif algorithm == "K-최근접 이웃 (KNN)":

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(
            n_neighbors=min(5, len(df))
        ))
    ])

else:

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(
            kernel="rbf",
            probability=True,
            random_state=42
        ))
    ])


# 선택한 알고리즘으로 학습
model.fit(X, y)

classes = model.classes_


# =====================================
# 8. 사용자 입력
# =====================================

st.divider()

st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=4.3,
        step=0.1,
        format="%.1f"
    )

with col2:

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


# =====================================
# 9. 품종 예측
# =====================================

if predict_button:

    input_data = pd.DataFrame({
        "꽃잎길이": [petal_length],
        "꽃잎너비": [petal_width]
    })

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    st.divider()

    st.subheader("🔍 붓꽃 품종 예측 결과")

    st.success(
        f"예측된 붓꽃 품종: {prediction}"
    )

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.metric(
            "꽃잎 길이",
            f"{petal_length:.1f} cm"
        )

    with result_col2:

        st.metric(
            "꽃잎 너비",
            f"{petal_width:.1f} cm"
        )

    st.caption(
        f"사용한 알고리즘: {algorithm}"
    )


    # =====================================
    # 10. 품종별 예측 확률
    # =====================================

    st.subheader("📊 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": classes,
        "예측 확률": probabilities * 100
    })

    fig_probability = go.Figure()

    fig_probability.add_trace(
        go.Bar(
            x=probability_df["품종"],
            y=probability_df["예측 확률"],
            text=[
                f"{v:.2f}%"
                for v in probability_df["예측 확률"]
            ],
            textposition="outside",
            marker_color=[
                "#F4A6B8",
                "#91C8E4",
                "#B8A1D9"
            ]
        )
    )

    fig_probability.update_layout(
        title="품종별 예측 확률 비교",
        xaxis_title="붓꽃 품종",
        yaxis_title="예측 확률 (%)",
        yaxis=dict(range=[0, 115]),
        height=400
    )

    st.plotly_chart(
        fig_probability,
        use_container_width=True
    )


    # =====================================
    # 11. 분류 영역 시각화
    # =====================================

    st.subheader("🌈 꽃잎 크기에 따른 품종 분류 그래프")

    st.write(
        "배경색은 선택한 알고리즘이 학습한 품종별 분류 영역입니다."
    )

    st.write(
        "파란색 별은 사용자가 입력한 꽃잎 크기를 나타냅니다."
    )

    x_min = length_min - 0.3
    x_max = length_max + 0.3

    y_min = width_min - 0.2
    y_max = width_max + 0.2

    # 그래프 격자 생성
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 180),
        np.linspace(y_min, y_max, 180)
    )

    grid_data = pd.DataFrame({
        "꽃잎길이": xx.ravel(),
        "꽃잎너비": yy.ravel()
    })

    # 선택한 알고리즘으로 격자별 품종 예측
    grid_predictions = model.predict(grid_data)

    class_mapping = {
        name: i
        for i, name in enumerate(classes)
    }

    zz = np.array([
        class_mapping[name]
        for name in grid_predictions
    ]).reshape(xx.shape)

    colors = [
        "#F4A6B8",
        "#91C8E4",
        "#B8A1D9"
    ]

    fig = go.Figure()


    # 품종별 배경 분류 영역
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
            opacity=0.4,
            hoverinfo="skip"
        )
    )


    # 기존 붓꽃 데이터 표시
    for i, species in enumerate(classes):

        species_data = df[
            df["품종"] == species
        ]

        fig.add_trace(
            go.Scatter(
                x=species_data["꽃잎길이"],
                y=species_data["꽃잎너비"],
                mode="markers",
                name=str(species),
                marker=dict(
                    size=8,
                    color=colors[i],
                    line=dict(
                        width=0.5,
                        color="black"
                    )
                ),
                hovertemplate=(
                    "품종: " + str(species) +
                    "<br>꽃잎 길이: %{x}cm" +
                    "<br>꽃잎 너비: %{y}cm" +
                    "<extra></extra>"
                )
            )
        )


    # =====================================
    # 사용자 입력값 파란색 별 표시
    # =====================================

    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers",
            name="사용자 입력값",
            marker=dict(
                symbol="star",
                size=25,
                color="#0066FF",
                line=dict(
                    width=2,
                    color="darkblue"
                )
            ),
            hovertemplate=(
                "사용자 입력값" +
                "<br>꽃잎 길이: %{x}cm" +
                "<br>꽃잎 너비: %{y}cm" +
                "<extra></extra>"
            )
        )
    )


    # 그래프 설정
    fig.update_layout(
        title="꽃잎 길이와 너비에 따른 붓꽃 품종 분류",
        xaxis_title="꽃잎 길이 (cm)",
        yaxis_title="꽃잎 너비 (cm)",
        height=650,
        legend_title="품종",
        hovermode="closest"
    )

    fig.update_xaxes(
        range=[x_min, x_max]
    )

    fig.update_yaxes(
        range=[y_min, y_max]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # =====================================
    # 12. 예측 이유 설명
    # =====================================

    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎 길이는 {petal_length:.1f}cm이고 "
        f"꽃잎 너비는 {petal_width:.1f}cm입니다."
    )

    st.write(
        f"그래프에서 파란색 별의 위치가 "
        f"**{prediction}의 분류 영역**에 해당하기 때문에 "
        f"이 품종으로 예측되었습니다."
    )

    st.write(
        f"선택한 {algorithm} 알고리즘은 "
        "기존 붓꽃 데이터를 학습한 후 "
        "입력값과 가장 잘 맞는 품종을 분류했습니다."
    )

    best_probability = max(probabilities) * 100

    st.info(
        f"가장 높은 예측 확률: {best_probability:.2f}%"
    )

    st.caption(
        "예측 확률은 모델이 계산한 값이며 "
        "실제 품종일 확률을 보장하지는 않습니다."
    )


else:

    st.info(
        "꽃잎 길이와 너비를 입력하고 "
        "'품종 예측하기' 버튼을 눌러주세요."
    )


# =====================================
# 13. 데이터 정보
# =====================================

with st.expander("📚 Iris 데이터 확인"):

    st.write(
        "전체 데이터 개수:",
        len(df)
    )

    st.write("품종별 데이터 개수")

    st.write(
        df["품종"].value_counts()
    )

    st.write("데이터 미리보기")

    st.dataframe(
        df,
        use_container_width=True
    )
