```python
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import html

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🐆",
    layout="wide"
)

# ----------------------------------
# 2. 화면 디자인
# ----------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #fffaf2,
        #f3e6d5
    );
}

h1, h2, h3 {
    color: #593d2b;
}

div[data-testid="stMetric"] {
    background-color: #fffaf2;
    border: 1px solid #ddc5a8;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐆 세계 국가별 MBTI 분석")
st.write(
    "국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 "
    "호피 무늬와 갈색 그라데이션 그래프로 확인할 수 있습니다."
)

# ----------------------------------
# 3. CSV 파일 불러오기
# ----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    df.columns = df.columns.str.strip()

    if "Country" not in df.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            "MBTI 유형 열이 16개인지 확인해 주세요."
        )

    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    if df[mbti_columns].isna().any().any():
        raise ValueError(
            "MBTI 데이터에 비어 있거나 잘못된 값이 있습니다."
        )

    return df, mbti_columns


try:
    df, mbti_columns = load_data()

except FileNotFoundError:
    st.error(
        "countriesMBTI_16types.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 GitHub 저장소에 업로드해 주세요."
    )
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

# ----------------------------------
# 4. 국가 선택
# ----------------------------------
countries = sorted(df["Country"].unique())

selected_country = st.selectbox(
    "🌍 국가를 선택하세요",
    countries
)

country_data = df[
    df["Country"] == selected_country
].iloc[0]

values = country_data[mbti_columns].astype(float)

# 원본 값이 0~1 사이의 비율이면 백분율로 변환
if values.max() <= 1:
    values = values * 100

# 비율이 높은 순서대로 정렬
ranking = values.sort_values(
    ascending=False
)

# ----------------------------------
# 5. 국가 분석 결과
# ----------------------------------
top_mbti = ranking.index[0]
top_value = ranking.iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택한 국가",
    selected_country
)

col2.metric(
    "비율 1위 MBTI",
    top_mbti
)

col3.metric(
    "1위 비율",
    f"{top_value:.2f}%"
)

# ----------------------------------
# 6. 색상 그라데이션 함수
# ----------------------------------
def hex_to_rgb(color):
    color = color.lstrip("#")

    return tuple(
        int(color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        *rgb
    )


def blend(color1, color2, ratio):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    result = tuple(
        round(
            a * (1 - ratio) + b * ratio
        )
        for a, b in zip(rgb1, rgb2)
    )

    return rgb_to_hex(result)


# 1위는 호피색
# 2위부터는 연갈색 -> 크림색
colors = ["#c99a55"]

for i in range(15):
    ratio = i / 14

    colors.append(
        blend(
            "#c5a17a",
            "#f5eadb",
            ratio
        )
    )

# ----------------------------------
# 7. 호피 무늬 막대그래프 생성
# ----------------------------------
def create_chart(labels, values, colors):
    width = 1000
    left = 150
    right = 100
    top = 25

    bar_height = 25
    gap = 14
    row_height = bar_height + gap

    height = (
        top * 2
        + len(labels) * row_height
    )

    chart_width = width - left - right

    max_value = max(values)
    scale_max = max_value * 1.2

    parts = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="100%" role="img">'
    )

    # 호피 무늬 패턴
    parts.append("""
    <defs>
        <pattern
            id="leopard"
            width="46"
            height="34"
            patternUnits="userSpaceOnUse">

            <rect
                width="46"
                height="34"
                fill="#c99a55"/>

            <path
                d="M4 5 C8 0 16 2 17 7
                   C18 12 11 15 7 12
                   C3 10 2 8 4 5 Z"
                fill="#352318"/>

            <path
                d="M6 6 C9 3 13 5 13 8
                   C13 10 10 12 7 10"
                fill="none"
                stroke="#f4d59c"
                stroke-width="2.2"/>

            <ellipse
                cx="31"
                cy="7"
                rx="5.5"
                ry="3.8"
                transform="rotate(-25 31 7)"
                fill="#352318"/>

            <ellipse
                cx="31"
                cy="7"
                rx="2.5"
                ry="1.8"
                transform="rotate(-25 31 7)"
                fill="#e8bd78"/>

            <path
                d="M19 23 C22 17 30 18 32 23
                   C34 28 27 32 22 29
                   C19 28 18 25 19 23 Z"
                fill="#352318"/>

            <path
                d="M22 23 C25 20 29 22 28 25
                   C27 28 23 28 22 25"
                fill="none"
                stroke="#f4d59c"
                stroke-width="2"/>

            <circle
                cx="41"
                cy="27"
                r="2.8"
                fill="#352318"/>

            <circle
                cx="9"
                cy="27"
                r="2.2"
                fill="#352318"/>

            <ellipse
                cx="40"
                cy="16"
                rx="2.1"
                ry="3.2"
                fill="#352318"/>
        </pattern>
    </defs>
    """)

    parts.append(
        f'<rect width="{width}" height="{height}" '
        f'rx="12" fill="#fffaf2"/>'
    )

    # 눈금선
    for tick in range(5):
        value = scale_max * tick / 4

        x = (
            left
            + chart_width * tick / 4
        )

        parts.append(
            f'<line x1="{x}" y1="{top-5}" '
            f'x2="{x}" y2="{height-25}" '
            f'stroke="#ddcbb7" '
            f'stroke-dasharray="3 5"/>'
        )

        parts.append(
            f'<text x="{x}" y="{height-7}" '
            f'text-anchor="middle" '
            f'font-size="12" fill="#765c45">'
            f'{value:.1f}%</text>'
        )

    # MBTI 막대
    for i, (label, value) in enumerate(
        zip(labels, values)
    ):
        y = top + i * row_height

        bar_width = (
            chart_width
            * float(value)
            / scale_max
        )

        safe_label = html.escape(str(label))

        parts.append(
            f'<text x="{left-15}" '
            f'y="{y + bar_height/2 + 5}" '
            f'text-anchor="end" '
            f'font-size="14" '
            f'font-weight="600" '
            f'fill="#593d2b">'
            f'{safe_label}</text>'
        )

        # 1위만 호피 무늬 적용
        if i == 0:
            fill_color = "url(#leopard)"
            border_color = "#6b4326"
        else:
            fill_color = colors[i]
            border_color = "#ddc5a8"

        parts.append(
            f'<rect x="{left}" y="{y}" '
            f'width="{bar_width:.2f}" '
            f'height="{bar_height}" '
            f'rx="4" '
            f'fill="{fill_color}" '
            f'stroke="{border_color}" '
            f'stroke-width="0.8"/>'
        )

        text_x = min(
            left + bar_width + 8,
            width - 60
        )

        parts.append(
            f'<text x="{text_x}" '
            f'y="{y + bar_height/2 + 4}" '
            f'font-size="12" '
            f'font-weight="600" '
            f'fill="#593d2b">'
            f'{value:.2f}%'
            f'</text>'
        )

    parts.append("</svg>")

    return "".join(parts)


# ----------------------------------
# 8. 그래프 표시
# ----------------------------------
st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)

st.caption(
    "1위는 호피 무늬이며, 나머지는 연한 갈색에서 "
    "크림색으로 점차 옅어집니다."
)

chart_html = create_chart(
    ranking.index.tolist(),
    ranking.values.tolist(),
    colors
)

components.html(
    chart_html,
    height=680,
    scrolling=False
)

# ----------------------------------
# 9. 순위표
# ----------------------------------
with st.expander("📋 MBTI 순위표 보기"):

    result = pd.DataFrame({
        "순위": range(1, len(ranking) + 1),
        "MBTI 유형": ranking.index,
        "비율(%)": ranking.values.round(2)
    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------
# 10. 안내
# ----------------------------------
st.divider()

st.caption(
    "본 결과는 제공된 CSV 데이터의 수치를 바탕으로 합니다. "
    "조사 대상과 수집 방법은 별도로 확인해야 하며, "
    "국가별 수치만으로 모든 국민의 성격을 단정할 수 없습니다."
)
```
