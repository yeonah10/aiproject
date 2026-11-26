
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(
    page_title="미쉐린 학생 추천 TOP 10",
    page_icon="🍜",
    layout="wide"
)

st.title("🍜 미쉐린 가이드 학생 추천 TOP 10")
st.caption("2026 미쉐린 데이터 기반 식당 추천")

@st.cache_data
def load_data():
    df = pd.read_csv(
        "michelin_2026_korea.csv",
        encoding="utf-8-sig"
    )
    df["음식 종류"] = df["음식 종류"].fillna("음식 종류 미확인")
    df["가격 기준"] = df["가격 기준"].fillna("가격 정보 미확인")
    df["지역"] = df["지역"].fillna("지역 미확인")
    return df

df = load_data()

# 학생 추천 순서
preferred_order = [
    "정짓간",
    "옥동식",
    "나가하마 만게츠",
    "니시무라멘",
    "교다이야",
    "미진",
    "서령",
    "정면",
    "능동미나리",
    "황금콩밭"
]

reasons = {
    "정짓간": "돼지국밥 - 익숙한 한 끼 메뉴",
    "옥동식": "돼지국밥 - 식사 메뉴 선택이 쉬움",
    "나가하마 만게츠": "라멘 - 친숙한 면 요리",
    "니시무라멘": "라멘 - 친숙한 면 요리",
    "교다이야": "우동 - 익숙한 면 요리",
    "미진": "메밀국수 - 면 메뉴 중심",
    "서령": "메밀국수 - 면 메뉴 중심",
    "정면": "국수 - 친숙한 식사 메뉴",
    "능동미나리": "곰탕 - 국물 식사",
    "황금콩밭": "두부 요리 - 친숙한 메뉴"
}

# 빕 구르망 식당만 추출
bib = df[
    df["미쉐린 등급"].astype(str).str.contains("빕 구르망", na=False)
].copy()

# TOP 10 선정
top10 = bib[
    bib["식당명"].isin(preferred_order)
].copy()

top10["순위"] = top10["식당명"].map(
    {name: i + 1 for i, name in enumerate(preferred_order)}
)

top10["추천 이유"] = top10["식당명"].map(reasons)

top10 = top10.sort_values("순위")

st.info(
    "추천 순위는 메뉴 친숙도와 식사 접근성을 고려한 "
    "참고용입니다. 실제 메뉴 가격과 영업 여부는 방문 전에 확인하세요."
)

# 상단 통계
col1, col2, col3 = st.columns(3)

col1.metric("추천 식당", f"{len(top10)}곳")
col2.metric("추천 지역", f"{top10['지역'].nunique()}개")
col3.metric("추천 기준", "빕 구르망")

st.divider()

# TOP 10 목록
st.subheader("🏆 고등학생 추천 식당 TOP 10")

st.dataframe(
    top10[
        [
            "순위",
            "식당명",
            "지역",
            "음식 종류",
            "가격 기준",
            "추천 이유"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()

# Folium 지도
st.subheader("🗺️ 추천 식당 지도")

st.warning(
    "현재 데이터에는 개별 식당 주소와 좌표가 없습니다. "
    "아래 지도는 서울과 부산의 도시 중심 위치를 표시하며, "
    "식당의 실제 위치를 나타내지는 않습니다."
)

city_coords = {
    "서울": [37.5665, 126.9780],
    "부산": [35.1796, 129.0756]
}

map_obj = folium.Map(
    location=[36.2, 127.8],
    zoom_start=7,
    tiles="OpenStreetMap"
)

marker_cluster = MarkerCluster().add_to(map_obj)

for _, row in top10.iterrows():

    city = row["지역"]

    if city not in city_coords:
        continue

    coords = city_coords[city]

    popup_text = f"""
    <b>{int(row['순위'])}위 - {row['식당명']}</b><br>
    지역: {city}<br>
    음식: {row['음식 종류']}<br>
    추천 이유: {row['추천 이유']}<br>
    <hr>
    실제 식당 좌표가 아닌 도시 중심 좌표입니다.
    """

    folium.Marker(
        location=coords,
        tooltip=f"{int(row['순위'])}위 {row['식당명']}",
        popup=folium.Popup(
            popup_text,
            max_width=300
        ),
        icon=folium.Icon(
            color="blue",
            icon="cutlery"
        )
    ).add_to(marker_cluster)

st_folium(
    map_obj,
    use_container_width=True,
    height=550
)

st.divider()

# 지역별 식당 통계
st.subheader("📊 지역별 추천 식당")

city_count = top10["지역"].value_counts()

st.bar_chart(city_count)

# 가격 기준 안내
st.subheader("💰 가격 정보")

st.write(
    "현재 데이터에서 빕 구르망은 가이드 기준 "
    "4만 5천 원 이하로 소개되어 있습니다."
)

st.write(
    "이는 개별 메뉴의 실제 가격을 보장하는 것이 아니므로 "
    "방문 전에 식당 메뉴를 확인하는 것이 좋습니다."
)

# CSV 다운로드
st.subheader("📥 TOP 10 CSV 다운로드")

csv_data = top10.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="추천 식당 CSV 다운로드",
    data=csv_data,
    file_name="student_michelin_top10.csv",
    mime="text/csv"
)

st.success("미쉐린 학생 추천 식당 분석 완료!")
