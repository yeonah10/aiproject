import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------
# 페이지 설정
# ---------------------------------------
st.set_page_config(
    page_title="국가별 MBTI 비율",
    page_icon="🐆",
    layout="wide",
)

# 따뜻한 베이지 계열의 화면 디자인
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fffaf2 0%, #f5eadb 100%);
    }
    h1, h2, h3 {
        color: #593d2b;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.72);
        border: 1px solid #ead8c3;
        padding: 16px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐆 세계 국가별 MBTI 비율")
st.write("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있어요.")
st.caption("막대그래프는 비율이 높은 순서이며, 1위는 호피 무늬 스타일로 표시됩니다.")

# ---------------------------------------
# 데이터 불러오기
# ---------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("countriesMBTI_16types.csv")
    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 'Country' 열이 없습니다.")

    data["Country"] = data["Country"].astype(str).str.strip()

    mbti_cols = [col for col in data.columns if col != "Country"]
    if len(mbti_cols) != 16:
        raise ValueError(
            f"MBTI 열이 16개여야 하지만 현재 {len(mbti_cols)}개입니다."
        )

    for col in mbti_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    if data["Country"].eq("").any() or data[mbti_cols].isna().any().any():
        raise ValueError("국가 이름 또는 MBTI 값에 비어 있거나 숫자가 아닌 값이 있습니다.")

    return data, mbti_cols


try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error(
        "데이터 파일을 찾을 수 없습니다. "
        "`app.py`와 `countriesMBTI_16types.csv`를 같은 GitHub 저장소 폴더에 올려 주세요."
    )
    st.stop()
except ValueError as error:
    st.error(f"데이터를 확인해 주세요: {error}")
    st.stop()

# ---------------------------------------
# 국가 선택
# ---------------------------------------
countries = sorted(df["Country"].unique().tolist())
selected_country = st.selectbox("🌍 국가 선택", countries)

row = df.loc[df["Country"] == selected_country].iloc[0]
values = row[mbti_columns].astype(float)

# 원본 값이 0~1 비율로 저장되어 있으므로 백분율로 변환
# (데이터에 따라 이미 백분율일 경우를 고려해 자동 변환)
if values.max() <= 1.0:
    percentages = values * 100
else:
    percentages = values.copy()

ranking = percentages.sort_values(ascending=False)
top_mbti = ranking.index[0]
top_value = float(ranking.iloc[0])

# ---------------------------------------
# 요약 카드
# ---------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("선택한 국가", selected_country)
c2.metric("가장 높은 유형", top_mbti)
c3.metric("1위 비율", f"{top_value:.2f}%")

# ---------------------------------------
# 색상 그라데이션
# 1위는 호피색 + 점무늬, 나머지는 연한 갈색에서 크림색으로
# ---------------------------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def blend(color1, color2, ratio):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    mixed = tuple(
        round(a * (1 - ratio) + b * ratio)
        for a, b in zip(rgb1, rgb2)
    )
    return rgb_to_hex(mixed)

labels = ranking.index.tolist()
bar_values = ranking.values.tolist()

# 2위는 따뜻한 연갈색, 마지막 순위로 갈수록 크림색에 가까워짐
other_colors = []
other_count = max(len(labels) - 2, 1)
for i in range(max(len(labels) - 1, 0)):
    ratio = i / other_count
    other_colors.append(blend("#c5a17a", "#f3e8d8", ratio))

bar_colors = ["#c99a55"] + other_colors

# 1위 막대에만 점무늬를 적용해 호피 느낌을 표현
patterns = ["."] + ["/"] * (len(labels) - 1)

fig = go.Figure()

for i, (label, value) in enumerate(zip(labels, bar_values)):
    fig.add_trace(
        go.Bar(
            x=[value],
            y=[label],
            orientation="h",
            name=label,
            marker=dict(
                color=bar_colors[i],
                line=dict(color="#6b4b32", width=0.7),
                pattern=dict(
                    shape=patterns[i],
                    fgcolor="#3b281b" if i == 0 else bar_colors[i],
                    bgcolor=bar_colors[i],
                    solidity=0.25 if i == 0 else 0.0,
                    size=8,
                ),
            ),
            text=[f"{value:.2f}%"],
            textposition="outside",
            textfont=dict(color="#4b3526", size=11),
            hovertemplate=f"<b>{label}</b><br>비율: %{{x:.2f}}%<extra></extra>",
            showlegend=False,
        )
    )

fig.update_layout(
    height=680,
    plot_bgcolor="rgba(255,255,255,0.55)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=70, t=20, b=35),
    xaxis=dict(
        title="비율 (%)",
        showgrid=True,
        gridcolor="rgba(120,90,60,0.15)",
        zeroline=False,
        rangemode="tozero",
    ),
    yaxis=dict(
        title="MBTI 유형",
        autorange="reversed",
        showgrid=False,
        tickfont=dict(color="#593d2b", size=12),
    ),
    font=dict(family="Arial, sans-serif", color="#593d2b"),
    bargap=0.28,
)

st.subheader(f"📊 {selected_country}의 MBTI 비율")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------
# 순위표
# ---------------------------------------
with st.expander("MBTI 비율 순위표 보기"):
    result = pd.DataFrame({
        "순위": range(1, len(ranking) + 1),
        "MBTI 유형": ranking.index,
        "비율(%)": ranking.values.round(2),
    })
    st.dataframe(result, use_container_width=True, hide_index=True)

st.info(
    "안내: 그래프는 제공된 CSV 파일의 수치를 백분율로 표시한 것입니다. "
    "원본 데이터의 조사 대상과 수집 방법은 별도로 확인해야 하며, "
    "이 결과만으로 한 국가의 모든 사람의 성격을 단정할 수는 없습니다."
)
