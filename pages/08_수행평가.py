import streamlit as st
import pandas as pd
import folium
import streamlit.components.v1 as components

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="미쉐린 식당 지도",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ 미쉐린 신규 식당 지도")
st.write("서울과 부산의 미쉐린 식당 위치를 확인해 보세요.")

# -------------------------
# 식당 데이터
# -------------------------
data = [
    {
        "식당명": "모먼트 로컬",
        "지역": "부산",
        "음식 종류": "스테이크",
        "가격대": "₩₩₩",
        "주소": "부산 해운대구 달맞이길 239-16",
        "위도": 35.1585,
        "경도": 129.1770
    },
    {
        "식당명": "뜨라또리아 로마냐",
        "지역": "서울",
        "음식 종류": "이탈리안",
        "가격대": "₩₩₩₩",
        "주소": "서울 서초구 사평대로14길 11",
        "위도": 37.4930,
        "경도": 127.0160
    },
    {
        "식당명": "양경옥",
        "지역": "부산",
        "음식 종류": "냉면",
        "가격대": "₩",
        "주소": "부산 수영구 민락본동로31번길 16",
        "위도": 35.1600,
        "경도": 129.1170
    },
    {
        "식당명": "무구옥",
        "지역": "서울",
        "음식 종류": "삼계탕",
        "가격대": "₩",
        "주소": "서울 종로구 율곡로1길 7",
        "위도": 37.5765,
        "경도": 126.9705
    },
    {
        "식당명": "거대 돼지국밥",
        "지역": "부산",
        "음식 종류": "돼지국밥",
        "가격대": "₩",
        "주소": "부산 해운대구 달맞이길 16-2",
        "위도": 35.1600,
        "경도": 129.1800
    },
    {
        "식당명": "바위",
        "지역": "서울",
        "음식 종류": "컨템퍼러리",
        "가격대": "₩₩₩",
        "주소": "서울 용산구 이태원로54길 16-9",
        "위도": 37.5350,
        "경도": 127.0000
    }
]

df = pd.DataFrame(data)

# -------------------------
# 사이드바 필터
# -------------------------
st.sidebar.header("🔎 식당 검색")

search = st.sidebar.text_input("식당 이름 검색")

region_filter = st.sidebar.multiselect(
    "지역 선택",
    options=df["지역"].unique(),
    default=df["지역"].unique().tolist()
)

price_filter = st.sidebar.multiselect(
    "가격대 선택",
    options=df["가격대"].unique(),
    default=df["가격대"].unique().tolist()
)

food_filter = st.sidebar.multiselect(
    "음식 종류 선택",
    options=df["음식 종류"].unique(),
    default=df["음식 종류"].unique().tolist()
)

# -------------------------
# 필터 적용
# -------------------------
filtered_df = df[
    (df["지역"].isin(region_filter)) &
    (df["가격대"].isin(price_filter)) &
    (df["음식 종류"].isin(food_filter))
]

if search:
    filtered_df = filtered_df[
        filtered_df["식당명"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# -------------------------
# 통계
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("전체 식당 수", len(df))
col2.metric("검색된 식당 수", len(filtered_df))
col3.metric("등록 지역", "서울 · 부산")

# -------------------------
# 지도 생성
# -------------------------
st.subheader("📍 식당 위치 지도")

if len(filtered_df) == 0:

    st.warning("검색 조건에 맞는 식당이 없습니다.")

else:

    # 선택된 식당들의 평균 좌표
    center_lat = filtered_df["위도"].mean()
    center_lon = filtered_df["경도"].mean()

    # OpenStreetMap 기본 타일 사용
    map_obj = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # 식당별 개별 마커
    for _, row in filtered_df.iterrows():

        popup_html = f"""
        <div style="width:220px">
            <h4>{row['식당명']}</h4>
            <hr>
            <b>지역:</b> {row['지역']}<br>
            <b>음식 종류:</b> {row['음식 종류']}<br>
            <b>가격대:</b> {row['가격대']}<br>
            <b>주소:</b> {row['주소']}
        </div>
        """

        folium.Marker(
            location=[row["위도"], row["경도"]],
            tooltip=row["식당명"],
            popup=folium.Popup(
                popup_html,
                max_width=300
            ),
            icon=folium.Icon(
                color="red",
                icon="info-sign"
            )
        ).add_to(map_obj)

    # 마커 위치에 맞게 지도 범위 조절
    if len(filtered_df) > 1:

        map_obj.fit_bounds([
            [
                filtered_df["위도"].min(),
                filtered_df["경도"].min()
            ],
            [
                filtered_df["위도"].max(),
                filtered_df["경도"].max()
            ]
        ])

    # Streamlit 화면에 지도 출력
    map_html = map_obj.get_root().render()

    components.html(
        map_html,
        height=600,
        scrolling=False
    )

# -------------------------
# 식당 목록
# -------------------------
st.subheader("📋 식당 목록")

st.dataframe(
    filtered_df[
        ["식당명", "지역", "음식 종류", "가격대", "주소"]
    ],
    use_container_width=True,
    hide_index=True
)

# -------------------------
# CSV 다운로드
# -------------------------
csv_file = filtered_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 식당 데이터 CSV 다운로드",
    data=csv_file,
    file_name="michelin_restaurants.csv",
    mime="text/csv"
)

# -------------------------
# 안내
# -------------------------
st.caption(
    "※ 지도 좌표는 참고용 근사 위치이며 정확한 식당 입구 좌표가 아닐 수 있습니다."
)

st.caption(
    "※ 가격대는 미쉐린 가격 기호 분류이며 실제 메뉴 가격과 다를 수 있습니다."
)
