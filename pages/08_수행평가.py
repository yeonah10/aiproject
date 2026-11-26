
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import time
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="2026 미쉐린 식당 가이드",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ 2026 MICHELIN RESTAURANT GUIDE")
st.caption("2026 미쉐린 서울·부산 식당 탐색 및 고등학생 추천")

st.markdown("""
미쉐린 선정 식당을 지역, 등급, 음식 종류별로 살펴보고
방문하기 좋은 식당을 찾아보세요.
""")

# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "michelin_2026_korea.csv"

    if not file_path.exists():
        return None

    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

    data.columns = data.columns.str.strip()

    for col in ["식당명", "지역", "미쉐린 등급", "음식 종류"]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["가격 기준"] = data["가격 기준"].fillna("")
    data["출처/확인 상태"] = data["출처/확인 상태"].fillna("")

    return data


df = load_data()

if df is None:
    st.error("michelin_2026_korea.csv 파일을 찾을 수 없습니다.")
    st.info("app.py와 CSV 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# ==========================================
# 3. 추천 순위 및 추천 이유
# ==========================================

recommendation_order = [
    "미진",
    "유림면",
    "옥동식",
    "교다이야",
    "3대 삼계장인",
    "필동면옥",
    "정면",
    "능동미나리",
    "미필담",
    "서교난면방",
    "안덕",
    "정짓간",
    "뫼밀집",
    "비비재",
    "안목",
    "나가하마 만게츠",
    "백일평냉",
    "한월관"
]

recommendation_reasons = {
    "미진": "친숙한 메밀국수 메뉴로 접근하기 좋은 식당",
    "유림면": "메밀국수를 중심으로 즐길 수 있는 식당",
    "옥동식": "한국인에게 친숙한 돼지고기 국물 요리",
    "교다이야": "대중적인 우동을 전문적으로 즐길 수 있는 곳",
    "3대 삼계장인": "익숙한 삼계탕을 전문적으로 맛볼 수 있는 곳",
    "필동면옥": "전통적인 평양냉면을 경험할 수 있는 곳",
    "정면": "다양한 국수 요리를 경험할 수 있는 곳",
    "능동미나리": "한국적인 곰탕을 맛볼 수 있는 곳",
    "미필담": "친숙한 만두 메뉴를 즐길 수 있는 곳",
    "서교난면방": "독특한 면 요리를 경험할 수 있는 곳",
    "안덕": "한식 국수와 만두를 즐길 수 있는 곳",
    "정짓간": "부산의 대표적인 돼지국밥을 경험할 수 있는 곳",
    "뫼밀집": "메밀을 활용한 면 요리를 즐길 수 있는 곳",
    "비비재": "친숙한 비빔밥 전문점",
    "안목": "부산의 돼지국밥을 현대적으로 경험할 수 있는 곳",
    "나가하마 만게츠": "대중적인 라멘 전문점",
    "백일평냉": "냉면을 중심으로 즐길 수 있는 곳",
    "한월관": "친숙한 곰탕 전문점"
}

priority = {
    name: i + 1
    for i, name in enumerate(recommendation_order)
}

# 빕 구르망 중심으로 추천
df["추천순위"] = df["식당명"].map(priority).fillna(999).astype(int)

df["추천이유"] = df["식당명"].map(
    recommendation_reasons
).fillna("등급과 음식 종류를 참고해 직접 확인해 보세요.")

def recommendation_label(row):
    if row["미쉐린 등급"] != "빕 구르망":
        return "가격 정보 확인 필요"

    if row["추천순위"] <= 18:
        return "추천 메뉴"

    return "추가 탐색 추천"

df["학생 추천 구분"] = df.apply(
    recommendation_label, axis=1
)

# ==========================================
# 4. 상단 통계
# ==========================================

total = len(df)
seoul = len(df[df["지역"] == "서울"])
busan = len(df[df["지역"] == "부산"])
bib = len(df[df["미쉐린 등급"] == "빕 구르망"])

c1, c2, c3, c4 = st.columns(4)

c1.metric("전체 식당", f"{total}곳")
c2.metric("서울", f"{seoul}곳")
c3.metric("부산", f"{busan}곳")
c4.metric("빕 구르망", f"{bib}곳")

st.divider()

# ==========================================
# 5. 사이드바
# ==========================================

st.sidebar.title("🔎 식당 검색")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "전체 식당 목록",
        "고등학생 추천 순위",
        "식당 위치 지도",
        "데이터 분석"
    ]
)

region_filter = st.sidebar.selectbox(
    "지역 선택",
    ["전체", "서울", "부산"]
)

grade_filter = st.sidebar.selectbox(
    "미쉐린 등급",
    ["전체"] + sorted(df["미쉐린 등급"].unique())
)

# ==========================================
# 6. 전체 식당 목록
# ==========================================

if menu == "전체 식당 목록":

    st.header("📋 전체 미쉐린 식당")

    search = st.text_input(
        "식당 이름 또는 음식 종류 검색",
        placeholder="예: 밍글스, 냉면, 한식"
    )

    filtered = df.copy()

    if region_filter != "전체":
        filtered = filtered[
            filtered["지역"] == region_filter
        ]

    if grade_filter != "전체":
        filtered = filtered[
            filtered["미쉐린 등급"] == grade_filter
        ]

    if search:
        filtered = filtered[
            filtered["식당명"].str.contains(
                search, case=False, na=False
            )
            |
            filtered["음식 종류"].str.contains(
                search, case=False, na=False
            )
        ]

    st.write(f"검색 결과: {len(filtered)}곳")

    st.dataframe(
        filtered[
            [
                "식당명",
                "지역",
                "미쉐린 등급",
                "음식 종류",
                "가격 기준"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("등급별 식당 목록")

    for grade in [
        "미쉐린 3스타",
        "미쉐린 2스타",
        "미쉐린 1스타",
        "빕 구르망"
    ]:

        group = filtered[
            filtered["미쉐린 등급"] == grade
        ]

        with st.expander(f"{grade} ({len(group)}곳)"):

            for _, row in group.iterrows():

                st.markdown(
                    f"**{row['식당명']}** · "
                    f"{row['지역']} · "
                    f"{row['음식 종류'] or '음식 종류 미입력'}"
                )

# ==========================================
# 7. 고등학생 추천 순위
# ==========================================

elif menu == "고등학생 추천 순위":

    st.header("🏆 고등학생 추천 미쉐린 식당")

    st.info(
        "빕 구르망을 우선으로 하고 메뉴의 친숙함과 "
        "식사 접근성을 고려한 참고용 추천 순위입니다. "
        "실제 가격과 학생 할인 여부를 의미하지는 않습니다."
    )

    city = st.selectbox(
        "추천 지역",
        ["전체", "서울", "부산"]
    )

    rec = df[
        df["미쉐린 등급"] == "빕 구르망"
    ].copy()

    if city != "전체":
        rec = rec[rec["지역"] == city]

    rec = rec.sort_values(
        ["추천순위", "식당명"]
    )

    rec["추천순위 표시"] = range(1, len(rec) + 1)

    for _, row in rec.iterrows():

        with st.container(border=True):

            a, b = st.columns([1, 5])

            with a:
                if row["추천순위"] != 999:
                    st.metric(
                        "추천",
                        f"{row['추천순위']}위"
                    )
                else:
                    st.write("추가 추천")

            with b:
                st.subheader(row["식당명"])

                st.write(
                    f"📍 {row['지역']} | "
                    f"🍜 {row['음식 종류'] or '정보 없음'}"
                )

                st.write(row["추천이유"])

                st.caption(
                    f"등급: {row['미쉐린 등급']} | "
                    f"가격 기준: {row['가격 기준'] or '정보 없음'}"
                )

# ==========================================
# 8. 식당 위치 지도
# ==========================================

elif menu == "식당 위치 지도":

    st.header("🗺️ 미쉐린 식당 위치 지도")

    st.write(
        "지역과 등급을 선택하고 지도에 표시할 식당을 골라보세요."
    )

    city = st.selectbox(
        "지도 지역",
        ["서울", "부산"]
    )

    map_data = df[df["지역"] == city].copy()

    grade = st.selectbox(
        "지도에 표시할 등급",
        ["전체", "빕 구르망", "미쉐린 1스타",
         "미쉐린 2스타", "미쉐린 3스타"]
    )

    if grade != "전체":
        map_data = map_data[
            map_data["미쉐린 등급"] == grade
        ]

    restaurant_names = map_data["식당명"].tolist()

    selected = st.multiselect(
        "지도에 표시할 식당 선택 (최대 10곳)",
        restaurant_names,
        default=restaurant_names[:5]
    )

    if len(selected) > 10:
        st.warning("한 번에 최대 10곳까지 표시할 수 있어요.")

    elif st.button("📍 지도에 식당 표시"):

        if not selected:
            st.warning("식당을 선택해주세요.")

        else:

            geolocator = Nominatim(
                user_agent="michelin_student_guide_2026"
            )

            center = (
                [37.5665, 126.9780]
                if city == "서울"
                else [35.1796, 129.0756]
            )

            restaurant_map = folium.Map(
                location=center,
                zoom_start=11,
                tiles="OpenStreetMap"
            )

            found = 0

            progress = st.progress(0)
            status = st.empty()

            for i, name in enumerate(selected):

                query = f"{name}, {city}, South Korea"

                try:
                    location = geolocator.geocode(
                        query,
                        timeout=10,
                        country_codes="kr"
                    )

                    if location:

                        row = map_data[
                            map_data["식당명"] == name
                        ].iloc[0]

                        popup_text = (
                            f"<b>{name}</b><br>"
                            f"{row['미쉐린 등급']}<br>"
                            f"{row['음식 종류']}"
                        )

                        folium.Marker(
                            location=[
                                location.latitude,
                                location.longitude
                            ],
                            popup=popup_text,
                            tooltip=name,
                            icon=folium.Icon(
                                color="red",
                                icon="cutlery",
                                prefix="fa"
                            )
                        ).add_to(restaurant_map)

                        found += 1

                    else:
                        st.warning(
                            f"{name}: 위치를 찾지 못했습니다."
                        )

                except Exception as e:
                    st.warning(
                        f"{name}: 위치 검색에 실패했습니다."
                    )

                progress.progress((i + 1) / len(selected))
                status.write(
                    f"{i + 1}/{len(selected)}곳 위치 검색 중"
                )

                time.sleep(1.1)

            if found > 0:

                st.success(
                    f"총 {found}곳의 위치를 찾았습니다."
                )

                st_folium(
                    restaurant_map,
                    width=None,
                    height=600,
                    returned_objects=[]
                )

            else:
                st.error(
                    "식당 위치를 찾지 못했습니다. "
                    "인터넷 연결과 식당명을 확인해주세요."
                )

# ==========================================
# 9. 데이터 분석
# ==========================================

elif menu == "데이터 분석":

    st.header("📊 미쉐린 데이터 분석")

    chart_df = df.copy()

    if region_filter != "전체":
        chart_df = chart_df[
            chart_df["지역"] == region_filter
        ]

    if grade_filter != "전체":
        chart_df = chart_df[
            chart_df["미쉐린 등급"] == grade_filter
        ]

    st.subheader("① 미쉐린 등급별 식당 수")

    grade_count = chart_df[
        "미쉐린 등급"
    ].value_counts().reset_index()

    grade_count.columns = ["등급", "식당 수"]

    fig1 = px.bar(
        grade_count,
        x="등급",
        y="식당 수",
        text="식당 수",
        color="등급",
        title="등급별 식당 수"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("② 지역별 식당 수")

    region_count = chart_df[
        "지역"
    ].value_counts().reset_index()

    region_count.columns = ["지역", "식당 수"]

    fig2 = px.pie(
        region_count,
        names="지역",
        values="식당 수",
        hole=0.35,
        title="지역별 식당 비율"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("③ 음식 종류별 식당 수")

    food_df = chart_df[
        chart_df["음식 종류"] != ""
    ]

    food_count = (
        food_df["음식 종류"]
        .value_counts()
        .head(15)
        .reset_index()
    )

    food_count.columns = ["음식 종류", "식당 수"]

    fig3 = px.bar(
        food_count,
        x="음식 종류",
        y="식당 수",
        text="식당 수",
        title="음식 종류 TOP 15"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("④ 지역별 등급 교차 분석")

    cross = pd.crosstab(
        chart_df["지역"],
        chart_df["미쉐린 등급"]
    )

    st.dataframe(
        cross,
        use_container_width=True
    )

    st.subheader("⑤ 데이터 결측치 분석")

    missing = df.isnull().sum().reset_index()

    missing.columns = ["컬럼", "결측치"]

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("⑥ 데이터 요약")

    st.write("전체 데이터 크기:", df.shape)

    st.write("중복 행 개수:", df.duplicated().sum())

    st.write("음식 종류 입력 개수:",
             (df["음식 종류"] != "").sum())

    st.write("가격 기준 입력 개수:",
             (df["가격 기준"] != "").sum())

# ==========================================
# 10. 하단 안내
# ==========================================

st.divider()

st.caption(
    "자료 출처: 사용자가 제공한 michelin_2026_korea.csv"
)

st.caption(
    "추천 순위는 학생의 메뉴 접근성을 고려한 자체 기준이며 "
    "공식 미쉐린 순위가 아닙니다."
)
