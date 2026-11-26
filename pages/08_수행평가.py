import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components

st.set_page_config(
    page_title="미쉐린 식당 지도",
    layout="wide"
)

st.title("🍽️ 미쉐린 식당 지도")
st.write("CSV에 저장된 모든 식당을 지도에 표시합니다.")

# CSV 업로드
uploaded_file = st.file_uploader(
    "식당 CSV 파일을 업로드하세요",
    type=["csv"]
)

if uploaded_file is not None:

    # CSV 읽기
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(uploaded_file, encoding="cp949")

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()

    # 필수 좌표 컬럼 확인
    if "위도" not in df.columns or "경도" not in df.columns:
        st.error("CSV에 위도와 경도 컬럼이 있어야 합니다.")
        st.write("현재 CSV 컬럼:", list(df.columns))
        st.stop()

    # 좌표 숫자로 변환
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

    # 좌표가 있는 식당 전부 추출
    map_df = df.dropna(subset=["위도", "경도"]).copy()

    # 기본값 처리
    for col in ["식당명", "지역", "음식 종류", "미쉐린 등급", "미쉐린 가격대", "가격"]:
        if col not in map_df.columns:
            map_df[col] = "정보 없음"

    # 상단 통계
    col1, col2, col3 = st.columns(3)

    col1.metric("CSV 전체 식당", len(df))
    col2.metric("지도 표시 식당", len(map_df))
    col3.metric("좌표 누락 식당", len(df) - len(map_df))

    if len(map_df) == 0:
        st.error("표시할 좌표 데이터가 없습니다.")
        st.stop()

    # 검색
    search = st.text_input("🔍 식당 이름 검색")

    if search:
        map_df = map_df[
            map_df["식당명"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    # 지역 필터
    if "지역" in map_df.columns:
        regions = map_df["지역"].dropna().unique().tolist()

        selected_regions = st.multiselect(
            "지역 선택",
            regions,
            default=regions
        )

        map_df = map_df[map_df["지역"].isin(selected_regions)]

    # 지도 중심 좌표 자동 계산
    center_lat = map_df["위도"].mean()
    center_lon = map_df["경도"].mean()

    # 지도 생성 (API KEY 없는 OpenStreetMap)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # 마커 그룹 생성
    marker_cluster = MarkerCluster().add_to(m)

    # CSV에 남아 있는 모든 식당을 반복해서 지도에 표시
    for _, row in map_df.iterrows():

        name = str(row["식당명"])
        region = str(row["지역"])
        cuisine = str(row["음식 종류"])
        grade = str(row["미쉐린 등급"])
        price = str(row["미쉐린 가격대"])

        popup_html = f"""
        <div style="width:230px">
            <h4>{name}</h4>
            <b>지역:</b> {region}<br>
            <b>음식 종류:</b> {cuisine}<br>
            <b>미쉐린 등급:</b> {grade}<br>
            <b>가격대:</b> {price}<br>
        </div>
        """

        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=folium.Popup(
                popup_html,
                max_width=300
            ),
            tooltip=name,
            icon=folium.Icon(
                color="red",
                icon="cutlery",
                prefix="fa"
            )
        ).add_to(marker_cluster)

    # 지도 출력
    st.subheader("📍 전체 식당 지도")

    map_html = m.get_root().render()

    components.html(
        map_html,
        height=650,
        scrolling=True
    )

    # 식당 목록도 전부 표시
    st.subheader("📋 지도에 표시된 전체 식당")

    st.dataframe(
        map_df,
        use_container_width=True,
        hide_index=True
    )

    # CSV 다운로드
    csv_data = map_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 식당 데이터 다운로드",
        data=csv_data,
        file_name="지도에_표시된_식당.csv",
        mime="text/csv"
    )

else:
    st.info("위에서 CSV 파일을 업로드하면 CSV 안의 모든 식당이 지도에 표시됩니다.")
