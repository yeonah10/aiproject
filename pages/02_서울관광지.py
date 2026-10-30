import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울의 주요 관광지 데이터
# 위도와 경도는 지도 표시용 좌표입니다.
attractions = [
    {
        "순위": 1,
        "관광지": "경복궁",
        "유형": "역사·문화",
        "위도": 37.5796,
        "경도": 126.9770,
        "주소": "서울 종로구 사직로 161",
        "설명": "조선 왕조의 대표 궁궐로 한국의 전통문화를 경험할 수 있습니다."
    },
    {
        "순위": 2,
        "관광지": "명동",
        "유형": "쇼핑·먹거리",
        "위도": 37.5636,
        "경도": 126.9869,
        "주소": "서울 중구 명동 일대",
        "설명": "쇼핑과 화장품 매장, 다양한 길거리 음식을 즐길 수 있습니다."
    },
    {
        "순위": 3,
        "관광지": "N서울타워",
        "유형": "전망·야경",
        "위도": 37.5512,
        "경도": 126.9882,
        "주소": "서울 용산구 남산공원길 105",
        "설명": "남산에서 서울의 전경과 아름다운 야경을 감상할 수 있습니다."
    },
    {
        "순위": 4,
        "관광지": "북촌한옥마을",
        "유형": "전통·거리",
        "위도": 37.5826,
        "경도": 126.9830,
        "주소": "서울 종로구 북촌로 일대",
        "설명": "전통 한옥과 한국의 옛 거리 풍경을 볼 수 있습니다."
    },
    {
        "순위": 5,
        "관광지": "인사동",
        "유형": "전통·문화",
        "위도": 37.5740,
        "경도": 126.9855,
        "주소": "서울 종로구 인사동 일대",
        "설명": "전통 공예품과 기념품, 한국 차 문화를 경험할 수 있습니다."
    },
    {
        "순위": 6,
        "관광지": "홍대거리",
        "유형": "문화·쇼핑",
        "위도": 37.5563,
        "경도": 126.9236,
        "주소": "서울 마포구 홍익로 일대",
        "설명": "거리 공연과 패션 매장, 카페 등을 즐길 수 있습니다."
    },
    {
        "순위": 7,
        "관광지": "동대문디자인플라자",
        "유형": "건축·전시",
        "위도": 37.5670,
        "경도": 127.0095,
        "주소": "서울 중구 을지로 281",
        "설명": "독특한 건축물과 다양한 전시, 문화행사를 즐길 수 있습니다."
    },
    {
        "순위": 8,
        "관광지": "광장시장",
        "유형": "시장·먹거리",
        "위도": 37.5700,
        "경도": 126.9998,
        "주소": "서울 종로구 창경궁로 88",
        "설명": "빈대떡과 김밥 등 다양한 한국 시장 음식을 맛볼 수 있습니다."
    },
    {
        "순위": 9,
        "관광지": "청계천",
        "유형": "산책·도심",
        "위도": 37.5692,
        "경도": 126.9788,
        "주소": "서울 종로구 청계광장 일대",
        "설명": "서울 도심에서 산책과 휴식을 즐길 수 있는 하천입니다."
    },
    {
        "순위": 10,
        "관광지": "롯데월드타워·서울스카이",
        "유형": "전망·체험",
        "위도": 37.5125,
        "경도": 127.1025,
        "주소": "서울 송파구 올림픽로 300",
        "설명": "서울의 전경을 감상할 수 있는 대표적인 고층 랜드마크입니다."
    }
]

df = pd.DataFrame(attractions)

# 제목
st.title("🗺️ 서울 인기 관광지 TOP 10")
st.write(
    "외국인 여행자를 위한 서울의 주요 관광지를 "
    "지도에서 확인해 보세요!"
)

st.info(
    "이 목록은 서울의 대표적인 관광지를 바탕으로 구성한 추천 목록이며, "
    "공식 방문객 통계에 따른 순위는 아닙니다."
)

# 검색 및 필터
st.sidebar.header("관광지 검색")

category = st.sidebar.selectbox(
    "관광 유형 선택",
    ["전체"] + sorted(df["유형"].unique().tolist())
)

keyword = st.sidebar.text_input(
    "관광지 이름 검색"
)

filtered_df = df.copy()

if category != "전체":
    filtered_df = filtered_df[
        filtered_df["유형"] == category
    ]

if keyword:
    filtered_df = filtered_df[
        filtered_df["관광지"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

# 화면 구성
left, right = st.columns([1.5, 1])

with left:
    st.subheader("📍 관광지 지도")

    # 서울 중심 지도
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # 관광지 마커 표시
    for _, row in filtered_df.iterrows():

        popup_text = f"""
        <b>{row['순위']}. {row['관광지']}</b><br>
        유형: {row['유형']}<br>
        주소: {row['주소']}<br>
        <br>
        {row['설명']}
        """

        folium.Marker(
            location=[
                row["위도"],
                row["경도"]
            ],
            tooltip=row["관광지"],
            popup=folium.Popup(
                popup_text,
                max_width=300
            ),
            icon=folium.Icon(
                color="red",
                icon="info-sign"
            )
        ).add_to(m)

    # 검색 결과에 맞게 지도 확대
    if not filtered_df.empty:
        bounds = filtered_df[
            ["위도", "경도"]
        ].values.tolist()

        if len(bounds) > 1:
            m.fit_bounds(bounds, padding=(25, 25))
        else:
            m.location = bounds[0]
            m.zoom_start = 15

    st_folium(
        m,
        use_container_width=True,
        height=550,
        key="seoul_map"
    )

with right:
    st.subheader("🏙️ 관광지 목록")

    if filtered_df.empty:
        st.warning("검색 결과가 없습니다.")
    else:
        for _, row in filtered_df.iterrows():

            with st.expander(
                f"{row['순위']}. {row['관광지']}"
            ):
                st.write(
                    f"**관광 유형:** {row['유형']}"
                )
                st.write(
                    f"**주소:** {row['주소']}"
                )
                st.write(
                    f"**설명:** {row['설명']}"
                )

# 데이터 표
st.subheader("📋 관광지 정보")

st.dataframe(
    filtered_df[
        ["순위", "관광지", "유형", "주소", "위도", "경도"]
    ],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "지도: OpenStreetMap | "
    "관광지 운영시간 및 이용 정보는 방문 전 공식 안내를 확인하세요."
)
