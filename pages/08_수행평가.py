import streamlit as st
import pandas as pd
import folium
import html
import time
import os

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="미쉐린 식당 지도", layout="wide")

st.title("🍽️ 미쉐린 식당 지도")
st.write("CSV에 있는 식당을 찾아 지도에 표시하는 프로그램")

# CSV 업로드
file = st.file_uploader("CSV 파일 업로드", type=["csv"])

if file is not None:

    # CSV 읽기
    try:
        df = pd.read_csv(file, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(file, encoding="cp949")

    df.columns = df.columns.str.strip()

    # 네 CSV 컬럼 확인
    required_columns = [
        "식당명",
        "지역",
        "미쉐린 등급",
        "음식 종류",
        "가격 기준",
        "공식 링크",
        "출처/확인 상태"
    ]

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        st.error(f"CSV에 없는 컬럼: {missing}")
        st.write("현재 CSV 컬럼:", df.columns.tolist())
        st.stop()

    st.success(f"CSV에서 {len(df)}개 식당을 불러왔습니다.")

    st.dataframe(df, use_container_width=True)

    # 위치 찾기 버튼
    if st.button("📍 식당 전체 위치 찾기", type="primary"):

        geolocator = Nominatim(
            user_agent="michelin_restaurant_school_map"
        )

        results = []

        progress = st.progress(0)
        status = st.empty()

        for i, row in df.iterrows():

            name = str(row["식당명"])
            region = str(row["지역"])

            status.write(f"위치 검색 중: {name}")

            # 지역 + 식당명으로 검색
            query = f"{name}, {region}, 대한민국"

            try:
                location = geolocator.geocode(
                    query,
                    timeout=15,
                    country_codes="kr"
                )

                # 검색 실패 시 식당명 + 한국으로 재검색
                if location is None:
                    location = geolocator.geocode(
                        f"{name}, South Korea",
                        timeout=15,
                        country_codes="kr"
                    )

                if location:
                    results.append({
                        "식당명": name,
                        "지역": region,
                        "미쉐린 등급": row["미쉐린 등급"],
                        "음식 종류": row["음식 종류"],
                        "가격 기준": row["가격 기준"],
                        "공식 링크": row["공식 링크"],
                        "출처/확인 상태": row["출처/확인 상태"],
                        "위도": location.latitude,
                        "경도": location.longitude,
                        "검색된 주소": location.address
                    })

                else:
                    results.append({
                        "식당명": name,
                        "지역": region,
                        "미쉐린 등급": row["미쉐린 등급"],
                        "음식 종류": row["음식 종류"],
                        "가격 기준": row["가격 기준"],
                        "공식 링크": row["공식 링크"],
                        "출처/확인 상태": row["출처/확인 상태"],
                        "위도": None,
                        "경도": None,
                        "검색된 주소": "위치 검색 실패"
                    })

            except Exception as e:
                results.append({
                    "식당명": name,
                    "지역": region,
                    "미쉐린 등급": row["미쉐린 등급"],
                    "음식 종류": row["음식 종류"],
                    "가격 기준": row["가격 기준"],
                    "공식 링크": row["공식 링크"],
                    "출처/확인 상태": row["출처/확인 상태"],
                    "위도": None,
                    "경도": None,
                    "검색된 주소": f"오류: {e}"
                })

            progress.progress((i + 1) / len(df))

            # 무료 지오코딩 서버 요청 간격 준수
            time.sleep(1.1)

        # 검색 결과 저장
        result_df = pd.DataFrame(results)

        st.session_state["restaurant_locations"] = result_df

        status.write("위치 검색 완료!")

# 검색된 데이터가 있을 때 지도 표시
if "restaurant_locations" in st.session_state:

    result_df = st.session_state["restaurant_locations"]

    # 좌표가 존재하는 식당
    map_df = result_df.dropna(subset=["위도", "경도"]).copy()

    st.divider()
    st.subheader("📊 검색 결과")

    c1, c2, c3 = st.columns(3)

    c1.metric("CSV 전체 식당", len(result_df))
    c2.metric("지도 표시 가능", len(map_df))
    c3.metric("위치 검색 실패", len(result_df) - len(map_df))

    # 실패한 식당 표시
    failed_df = result_df[result_df["위도"].isna()]

    if not failed_df.empty:
        st.warning("일부 식당의 위치를 찾지 못했습니다.")
        st.dataframe(failed_df[["식당명", "지역", "검색된 주소"]])

    if not map_df.empty:

        # 지도 중심
        center_lat = map_df["위도"].mean()
        center_lon = map_df["경도"].mean()

        # API KEY 없는 OpenStreetMap
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles="OpenStreetMap"
        )

        # 식당 마커
        for _, row in map_df.iterrows():

            name = html.escape(str(row["식당명"]))
            region = html.escape(str(row["지역"]))
            grade = html.escape(str(row["미쉐린 등급"]))
            cuisine = html.escape(str(row["음식 종류"]))
            price = html.escape(str(row["가격 기준"]))
            address = html.escape(str(row["검색된 주소"]))
            link = str(row["공식 링크"]).strip()

            popup_content = f"""
            <div style="width:260px; font-family:sans-serif;">
                <h3>{name}</h3>
                <b>지역:</b> {region}<br>
                <b>미쉐린 등급:</b> {grade}<br>
                <b>음식 종류:</b> {cuisine}<br>
                <b>가격 기준:</b> {price}<br>
                <b>주소:</b> {address}<br>
            """

            if link.startswith("https://") or link.startswith("http://"):
                safe_link = html.escape(link, quote=True)
                popup_content += f"""
                <br><a href="{safe_link}" target="_blank">
                공식 식당 정보 보기</a>
                """

            popup_content += "</div>"

            folium.Marker(
                location=[row["위도"], row["경도"]],
                tooltip=name,
                popup=folium.Popup(
                    popup_content,
                    max_width=350
                ),
                icon=folium.Icon(color="red", icon="cutlery")
            ).add_to(m)

        # 지도 출력
        st.subheader("🗺️ 미쉐린 식당 전체 지도")

        st_html(
            m.get_root().render(),
            height=600,
            scrolling=True
        )

    # 전체 결과
    st.subheader("📋 전체 식당 위치 데이터")
    st.dataframe(result_df, use_container_width=True)

    # 결과 CSV 다운로드
    csv = result_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        "📥 좌표 포함 CSV 다운로드",
        data=csv,
        file_name="미쉐린_식당_좌표.csv",
        mime="text/csv"
    )

else:
    st.info("CSV를 업로드한 뒤 '식당 전체 위치 찾기'를 누르세요.")
