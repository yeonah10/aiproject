
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================
# 1. 데이터 불러오기
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

file_paths = [
    BASE_DIR / "population_utf8.csv",
    BASE_DIR / "population.csv"
]

CSV_PATH = next((p for p in file_paths if p.is_file()), None)

if CSV_PATH is None:
    st.error("인구 데이터 CSV 파일을 찾을 수 없습니다.")
    st.stop()

try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(CSV_PATH, encoding="cp949")

# =========================
# 2. 지역명 정리
# =========================

def clean_region(name):
    name = str(name).split("(")[0].strip()

    if name == "인천광역시":
        return name

    return name.replace("인천광역시 ", "")

if "행정구역" not in df.columns:
    st.error("CSV 파일에 '행정구역' 열이 없습니다.")
    st.stop()

df["지역명"] = df["행정구역"].apply(clean_region)

# =========================
# 3. 기본 설정
# =========================

ages = [
    "0~9세", "10~19세", "20~29세",
    "30~39세", "40~49세", "50~59세",
    "60~69세", "70~79세", "80~89세",
    "90~99세", "100세 이상"
]

years = [2020, 2021, 2022, 2023, 2024, 2025]

# =========================
# 4. 인구 데이터 함수
# =========================

def get_number(value):
    return pd.to_numeric(
        str(value).replace(",", "").strip(),
        errors="coerce"
    )


def get_population(row, year, prefix, age=None):

    if age is None:
        column = f"{year}년_{prefix}거주자_총인구수"
    else:
        column = f"{year}년_{prefix}거주자_{age}"

    if column not in df.columns:
        return 0

    value = get_number(row[column])

    if pd.isna(value):
        return 0

    return value


# =========================
# 5. 제목
# =========================

st.title("📊 인천광역시 인구통계")
st.write("연도와 행정구역을 선택하여 인구 현황을 확인할 수 있습니다.")

st.divider()

# =========================
# 6. 연도 및 지역 선택
# =========================

col1, col2 = st.columns(2)

with col1:
    year = st.selectbox(
        "📅 연도 선택",
        years,
        index=5
    )

with col2:
    regions = df["지역명"].dropna().unique().tolist()

    selected_region = st.selectbox(
        "📍 행정구역 선택",
        regions
    )

selected_rows = df[df["지역명"] == selected_region]

if selected_rows.empty:
    st.error("선택한 지역의 데이터가 없습니다.")
    st.stop()

selected = selected_rows.iloc[0]

# =========================
# 7. 연령대별 남녀 인구 그래프
# =========================

st.divider()
st.subheader("👥 연령대별 남녀 인구")

age_gender_data = []

for age in ages:
    male = get_population(selected, year, "남_", age)
    female = get_population(selected, year, "여_", age)

    age_gender_data.append({
        "연령대": age,
        "성별": "남성",
        "인구수": male
    })

    age_gender_data.append({
        "연령대": age,
        "성별": "여성",
        "인구수": female
    })

age_gender_df = pd.DataFrame(age_gender_data)

fig1 = px.line(
    age_gender_df,
    x="연령대",
    y="인구수",
    color="성별",
    markers=True,
    color_discrete_map={
        "남성": "#87CEEB",
        "여성": "#FFB6C1"
    }
)

fig1.update_layout(
    xaxis_title="연령대",
    yaxis_title="인구수(명)",
    legend_title="성별"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================
# 8. 남녀 인구 비율 원형그래프
# =========================

st.divider()
st.subheader("🥧 남녀 인구 비율")

male_total = get_population(selected, year, "남_")
female_total = get_population(selected, year, "여_")

pie_df = pd.DataFrame({
    "성별": ["남성", "여성"],
    "인구수": [male_total, female_total]
})

fig2 = px.pie(
    pie_df,
    names="성별",
    values="인구수",
    color="성별",
    color_discrete_map={
        "남성": "#87CEEB",
        "여성": "#FFB6C1"
    },
    hole=0
)

fig2.update_traces(
    textinfo="label+percent",
    textposition="inside"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# 9. 연령대별 행정구역 TOP 10
# =========================

st.divider()
st.subheader("🏆 연령대별 행정구역 TOP 10")

top_col1, top_col2 = st.columns(2)

with top_col1:
    selected_age = st.selectbox(
        "연령대 선택",
        ages
    )

with top_col2:
    selected_gender = st.selectbox(
        "성별 선택",
        ["전체", "남성", "여성"]
    )

if selected_gender == "남성":
    prefix = "남_"
    bar_color = "#87CEEB"

elif selected_gender == "여성":
    prefix = "여_"
    bar_color = "#FFB6C1"

else:
    prefix = ""
    bar_color = "#B39DDB"

top_data = []

district_df = df[df["지역명"] != "인천광역시"]

for _, row in district_df.iterrows():

    if selected_gender == "전체":
        male = get_population(row, year, "남_", selected_age)
        female = get_population(row, year, "여_", selected_age)
        population = male + female

    else:
        population = get_population(
            row, year, prefix, selected_age
        )

    top_data.append({
        "지역명": row["지역명"],
        "인구수": population
    })

top_df = pd.DataFrame(top_data)

top_df = top_df.sort_values(
    "인구수",
    ascending=False
).head(10)

fig3 = px.bar(
    top_df,
    x="지역명",
    y="인구수",
    text="인구수"
)

fig3.update_traces(
    marker_color=bar_color,
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig3.update_layout(
    xaxis_title="행정구역",
    yaxis_title="인구수(명)"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================
# 10. 인구 현황 요약
# =========================

st.divider()
st.subheader("📌 인구 현황 요약")

total_population = get_population(selected, year, "")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "남성 인구",
        f"{male_total:,.0f}명"
    )

with metric2:
    st.metric(
        "여성 인구",
        f"{female_total:,.0f}명"
    )

with metric3:
    st.metric(
        "전체 인구",
        f"{total_population:,.0f}명"
    )

# =========================
# 11. 구별 전년도 대비 인구 증감률 그래프
# =========================

st.divider()
st.subheader("📊 구별 전년도 대비 인구 증감률")

if year == 2020:

    st.info(
        "2020년은 전년도 데이터가 없어 증감률을 계산할 수 없습니다."
    )

else:

    previous_year = year - 1

    change_data = []

    # 인천광역시 전체 제외
    district_df = df[
        df["지역명"] != "인천광역시"
    ]

    for _, row in district_df.iterrows():

        current_population = get_population(
            row, year, ""
        )

        previous_population = get_population(
            row, previous_year, ""
        )

        if previous_population <= 0:
            continue

        difference = (
            current_population - previous_population
        )

        change_rate = (
            difference / previous_population
        ) * 100

        change_data.append({
            "지역명": row["지역명"],
            "증감률": change_rate,
            "증감 인구": difference
        })

    change_df = pd.DataFrame(change_data)

    if not change_df.empty:

        change_df = change_df.sort_values(
            "증감률",
            ascending=False
        )

        change_df["구분"] = change_df["증감률"].apply(
            lambda x: "증가" if x >= 0 else "감소"
        )

        fig4 = px.bar(
            change_df,
            x="지역명",
            y="증감률",
            color="구분",
            color_discrete_map={
                "증가": "#87CEEB",
                "감소": "#FFB6C1"
            },
            text=change_df["증감률"].apply(
                lambda x: f"{x:+.2f}%"
            ),
            hover_data={
                "증감 인구": ":,.0f",
                "증감률": ":.2f",
                "구분": False
            }
        )

        fig4.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig4.update_layout(
            xaxis_title="행정구역",
            yaxis_title="인구 증감률(%)",
            yaxis=dict(
                zeroline=True,
                zerolinewidth=2
            ),
            showlegend=True
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

        st.subheader("📋 구별 인구 증감률 상세")

        display_df = change_df[
            ["지역명", "증감 인구", "증감률"]
        ].rename(columns={
            "지역명": "행정구역",
            "증감 인구": "인구 증감 수(명)",
            "증감률": "인구 증감률(%)"
        })

        st.dataframe(
            display_df.style.format({
                "인구 증감 수(명)": "{:+,.0f}",
                "인구 증감률(%)": "{:+.2f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning(
            "증감률을 계산할 수 있는 데이터가 없습니다."
        )

# =========================
# 12. 연령대별 상세 인구표
# =========================

st.divider()
st.subheader("📋 연령대별 남녀 인구 상세")

detail_data = []

for age in ages:

    male = get_population(
        selected, year, "남_", age
    )

    female = get_population(
        selected, year, "여_", age
    )

    detail_data.append({
        "연령대": age,
        "남성": male,
        "여성": female,
        "전체": male + female
    })

detail_df = pd.DataFrame(detail_data)

st.dataframe(
    detail_df.style.format({
        "남성": "{:,.0f}",
        "여성": "{:,.0f}",
        "전체": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)
