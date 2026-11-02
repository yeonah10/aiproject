import html
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ------------------------------
# 페이지 설정과 디자인
# ------------------------------
st.set_page_config(
    page_title="국가별 MBTI 비율",
    page_icon="🐆",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fffaf2 0%, #f3e6d5 100%);
    }
    h1, h2, h3 {
        color: #593d2b;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid #ead8c3;
        padding: 15px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐆 세계 국가별 MBTI 비율")
st.write("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")
st.caption("비율이 높은 순서로 표시되며, 1위 막대는 호피 무늬로 강조됩니다.")


# ------------------------------
# CSV 데이터 불러오기
# ------------------------------
@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "countriesMBTI_16types.csv"
    if not csv_path.exists():
        raise FileNotFoundError

    data = pd.read_csv(csv_path)
    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 Country 열이 없습니다.")

    mbti_columns = [column for column in data.columns if column != "Country"]
    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 유형 열은 16개여야 하지만 현재 {len(mbti_columns)}개입니다."
        )

    data["Country"] = data["Country"].astype(str).str.strip()
    for column in mbti_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    if data["Country"].eq("").any() or data[mbti_columns].isna().any().any():
        raise ValueError("CSV 파일에 비어 있거나 숫자가 아닌 값이 있습니다.")

    return data, mbti_columns


try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error(
        "countriesMBTI_16types.csv 파일을 찾을 수 없습니다. "
        "app.py와 CSV 파일을 같은 GitHub 저장소 폴더에 올려 주세요."
    )
    st.stop()
except ValueError as error:
    st.error(f"CSV 파일을 확인해 주세요: {error}")
    st.stop()

countries = sorted(df["Country"].unique().tolist())
selected_country = st.selectbox("🌍 국가 선택", countries)

country_row = df.loc[df["Country"] == selected_country].iloc[0]
raw_values = country_row[mbti_columns].astype(float)

# 데이터가 0~1 사이의 소수이면 백분율로 변환합니다.
if raw_values.max() <= 1:
    percentages = raw_values * 100
else:
    percentages = raw_values

ranking = percentages.sort_values(ascending=False)
labels = ranking.index.tolist()
values = [float(value) for value in ranking.tolist()]

if not values:
    st.error("표시할 MBTI 데이터가 없습니다.")
    st.stop()

top_type = labels[0]
top_value = values[0]

metric1, metric2, metric3 = st.columns(3)
metric1.metric("선택한 국가", selected_country)
metric2.metric("가장 높은 유형", top_type)
metric3.metric("1위 비율", f"{top_value:.2f}%")


# ------------------------------
# 색상 처리
# ------------------------------
def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))


def blend_colors(start_color, end_color, ratio):
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)
    blended = tuple(
        round(first * (1 - ratio) + second * ratio)
        for first, second in zip(start, end)
    )
    return "#{:02x}{:02x}{:02x}".format(*blended)


def make_svg_chart(chart_labels, chart_values):
    width = 1000
    left = 145
    right = 95
    top = 24
    bar_height = 25
    gap = 14
    row_height = bar_height + gap
    height = top * 2 + len(chart_labels) * row_height
    chart_width = width - left - right

    max_value = max(chart_values) if chart_values else 1
    scale_max = max_value * 1.2 if max_value > 0 else 1

    # 1위는 호피 무늬, 나머지는 연한 갈색에서 크림색으로 변합니다.
    other_count = max(len(chart_labels) - 1, 1)
    other_colors = [
        blend_colors("#c5a17a", "#f5eadb", index / other_count)
        for index in range(len(chart_labels) - 1)
    ]
    colors = ["#c99a55"] + other_colors

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" width="100%" '
            f'role="img" aria-label="국가별 MBTI 비율 막대그래프">'
        ),
        """
        <defs>
          <pattern id="leopard" patternUnits="userSpaceOnUse"
                   width="46" height="34">
            <rect width="46" height="34" fill="#c99a55"/>
            <path d="M4 5 C8 0 16 2 17 7 C18 12 11 15 7 12 C3 10 2 8 4 5 Z"
                  fill="#3b281b"/>
            <path d="M6 6 C9 3 13 5 13 8 C13 10 10 12 7 10"
                  fill="none" stroke="#f0d29a" stroke-width="2"/>
            <ellipse cx="31" cy="7" rx="5.5" ry="3.8"
                     transform="rotate(-25 31 7)" fill="#3b281b"/>
            <ellipse cx="31" cy="7" rx="2.5" ry="1.8"
                     transform="rotate(-25 31 7)" fill="#e7bd78"/>
            <path d="M19 23 C22 17 30 18 32 23 C34 28 27 32 22 29
                     C19 28 18 25 19 23 Z" fill="#3b281b"/>
            <path d="M22 23 C25 20 29 22 28 25 C27 28 23 28 22 25"
                  fill="none" stroke="#f0d29a" stroke-width="2"/>
            <circle cx="41" cy="27" r="2.8" fill="#3b281b"/>
            <circle cx="9" cy="27" r="2.2" fill="#3b281b"/>
            <ellipse cx="40" cy="16" rx="2.1" ry="3.2" fill="#3b281b"/>
          </pattern>
        </defs>
        """,
        f'<rect width="{width}" height="{height}" rx="12" fill="#fffaf2"/>',
    ]

    # 세로 눈금선
    for tick in range(5):
        tick_value = scale_max * tick / 4
        x = left + chart_width * tick / 4
        parts.append(
            f'<line x1="{x:.1f}" y1="{top - 5}" '
            f'x2="{x:.1f}" y2="{height - 25}" '
            'stroke="#d9c8b5" stroke-width="1" stroke-dasharray="3 5"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{height - 7}" text-anchor="middle" '
            'font-size="12" fill="#765c45">'
            f'{tick_value:.1f}%</text>'
        )

    # 막대와 라벨
    for index, (label, value) in enumerate(zip(chart_labels, chart_values)):
        y = top + index * row_height
        bar_width = chart_width * value / scale_max
        safe_label = html.escape(str(label))
        fill = "url(#leopard)" if index == 0 else colors[index]
        outline = "#6b4326" if index == 0 else "#d4b99c"

        parts.append(
            f'<text x="{left - 14}" y="{y + bar_height / 2 + 4:.1f}" '
            'text-anchor="end" font-size="14" font-weight="600" '
            'fill="#593d2b">'
            f'{safe_label}</text>'
        )
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_width:.2f}" '
            f'height="{bar_height}" rx="4" fill="{fill}" '
            f'stroke="{outline}" stroke-width="0.8"/>'
        )

        value_x = min(left + bar_width + 9, width - 55)
        parts.append(
            f'<text x="{value_x:.1f}" y="{y + bar_height / 2 + 4:.1f}" '
            'font-size="12" font-weight="600" fill="#593d2b">'
            f'{value:.2f}%</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


st.subheader(f"📊 {selected_country}의 MBTI 비율")
st.caption("1위는 호피 무늬, 나머지 막대는 점점 옅어지는 갈색 계열입니다.")
chart_html = make_svg_chart(labels, values)
components.html(chart_html, height=720, scrolling=True)

with st.expander("MBTI 비율 순위표 보기"):
    result = pd.DataFrame(
        {
            "순위": range(1, len(ranking) + 1),
            "MBTI 유형": ranking.index,
            "비율(%)": ranking.values.round(2),
        }
    )
    st.dataframe(result, use_container_width=True, hide_index=True)

st.info(
    "안내: 그래프는 제공된 CSV의 수치를 백분율로 표시합니다. "
    "조사 대상과 수집 방법에 따라 결과가 달라질 수 있으므로, "
    "이 결과만으로 한 국가의 모든 사람의 성격을 단정할 수는 없습니다."
)
