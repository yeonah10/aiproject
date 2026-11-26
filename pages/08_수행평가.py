
import streamlit as st
import pandas as pd
import folium
import html
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="Michelin Restaurant Explorer",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Michelin Restaurant Explorer")
st.markdown("### 미쉐린 레스토랑 데이터 분석 & 지도 시각화")
st.write(
    "미쉐린 레스토랑 데이터를 탐색하고 지역, 음식 종류, "
    "등급별 분포를 분석하는 인터랙티브 대시보드입니다."
)

# ==========================================
# 2. 지역별 대표 좌표
# 정확한 식당 위치가 없을 때 지역 단위로 표시
# ==========================================
REGION_COORDS = {
    "서울": [37.5665, 126.9780],
    "서울특별시": [37.5665, 126.9780],
    "부산": [35.1796, 129.0756],
    "부산광역시": [35.1796, 129.0756],
    "대구": [35.8714, 128.6014],
    "대구광역시": [35.8714, 128.6014],
    "인천": [37.4563, 126.7052],
    "인천광역시": [37.4563, 126.7052],
    "대전": [36.3504, 127.3845],
    "대전광역시": [36.3504, 127.3845],
    "광주": [35.1595, 126.8526],
    "광주광역시": [35.1595, 126.8526],
    "울산": [35.5384, 129.3114],
    "울산광역시": [35.5384, 129.3114],
    "세종": [36.4800, 127.2890],
    "세종특별자치시": [36.4800, 127.2890],
    "경기": [37.4138, 127.5183],
    "경기도": [37.4138, 127.5183],
    "강원": [37.8228, 128.1555],
    "강원도": [37.8228, 128.1555],
    "충북": [36.6357, 127.4914],
    "충청북도": [36.6357, 127.4914],
    "충남": [36.6588, 126.6728],
    "충청남도": [36.6588, 126.6728],
    "전북": [35.7175, 127.1530],
    "전라북도": [35.7175, 127.1530],
    "전남": [34.8679, 126.9910],
    "전라남도": [34.8679, 126.9910],
    "경북": [36.4919, 128.8889],
    "경상북도": [36.4919, 128.8889],
    "경남": [35.4606, 128.2132],
    "경상남도": [35.4606, 128.2132],
    "제주": [33.4996, 126.5312],
    "제주도": [33.4996, 126.5312],
    "제주특별자치도": [33.4996, 126.5312],
}

# ==========================================
# 3. 데이터 업로드
# ==========================================
st.sidebar.header("📂 데이터 관리")

uploaded_file = st.sidebar.file_uploader(
    "레스토랑 CSV 파일 업로드",
    type=["csv"]
)

# CSV 템플릿 다운로드
template = pd.DataFrame({
    "식당명": ["예시 식당"],
    "지역": ["서울"],
    "음식 종류": ["한식"],
    "미쉐린 등급": ["빕 구르망"],
    "가격": [15000],
    "주소": ["서울 예시 주소"],
    "위도": [37.5665],
    "경도": [126.9780]
})

st.sidebar.download_button(
    label="📥 CSV 양식 다운로드",
    data=template.to_csv(index=False).encode("utf-8-sig"),
    file_name="restaurant_template.csv",
    mime="text/csv"
)

if uploaded_file is None:
    st.warning("왼쪽 사이드바에서 미쉐린 레스토랑 CSV 파일을 업로드하세요.")
    st.subheader("📄 CSV 데이터 형식")

    st.dataframe(template, use_container_width=True)

    st.info(
        "식당명은 필수입니다. 지역, 음식 종류, 등급, 가격, 주소, "
        "위도, 경도는 없어도 프로그램이 자동으로 빈 열을 생성합니다."
    )
    st.stop()

# ==========================================
# 4. CSV 읽기
# ==========================================
try:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="cp949")
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 컬럼 이름 공백 제거
df.columns = df.columns.astype(str).str.strip()

# 식당 이름 컬럼 자동 인식
name_candidates = ["식당명", "레스토랑명", "Restaurant", "Name", "name"]

if "식당명" not in df.columns:
    found_name = None

    for candidate in name_candidates:
        if candidate in df.columns:
            found_name = candidate
            break

    if found_name:
        df = df.rename(columns={found_name: "식당명"})

if "식당명" not in df.columns:
    st.error("CSV에 '식당명' 컬럼이 없습니다. 식당 이름이 포함된 파일을 업로드하세요.")
    st.stop()

# ==========================================
# 5. 누락 컬럼 자동 생성
# ==========================================
optional_columns = {
    "지역": "정보 없음",
    "음식 종류": "정보 없음",
    "미쉐린 등급": "정보 없음",
    "가격": None,
    "주소": None,
    "위도": None,
    "경도": None,
}

for col, default_value in optional_columns.items():
    if col not in df.columns:
        df[col] = default_value

# 문자열 정리
text_columns = [
    "식당명", "지역", "음식 종류", "미쉐린 등급", "주소"
]

for col in text_columns:
    df[col] = df[col].fillna("").astype(str).str.strip()

# 숫자 데이터 정리
for col in ["가격", "위도", "경도"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 식당명이 비어 있는 행 삭제
df = df[df["식당명"] != ""].copy()

# 중복 식당 정리
df = df.drop_duplicates(subset=["식당명"], keep="first")

# ==========================================
# 6. 좌표 유효성 확인
# ==========================================
df["좌표 유효"] = (
    df["위도"].between(33, 39)
    & df["경도"].between(124, 132)
)

# ==========================================
# 7. 사이드바 필터
# ==========================================
st.sidebar.divider()
st.sidebar.header("🔎 검색 및 필터")

search_text = st.sidebar.text_input(
    "식당 이름 검색",
    placeholder="검색어 입력"
)

region_options = sorted(
    x for x in df["지역"].unique() if x.strip()
)

food_options = sorted(
    x for x in df["음식 종류"].unique() if x.strip()
)

grade_options = sorted(
    x for x in df["미쉐린 등급"].unique() if x.strip()
)

selected_regions = st.sidebar.multiselect(
    "지역",
    options=region_options,
    default=region_options
)

selected_foods = st.sidebar.multiselect(
    "음식 종류",
    options=food_options,
    default=food_options
)

selected_grades = st.sidebar.multiselect(
    "미쉐린 등급",
    options=grade_options,
    default=grade_options
)

# 가격 필터: 가격이 있는 경우에만 생성
valid_prices = df["가격"].dropna()
price_range = None

if not valid_prices.empty:
    min_price = int(valid_prices.min())
    max_price = int(valid_prices.max())

    if min_price < max_price:
        step = max(1000, ((max_price - min_price) // 100) or 1000)

        price_range = st.sidebar.slider(
            "가격 범위 (원)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=step
        )
    else:
        price_range = (min_price, max_price)

else:
    st.sidebar.caption("가격 데이터가 없어 가격 필터는 비활성화됩니다.")

# ==========================================
# 8. 필터 적용
# ==========================================
filtered = df.copy()

if search_text:
    filtered = filtered[
        filtered["식당명"].str.contains(
            search_text,
            case=False,
            na=False,
            regex=False
        )
    ]

if region_options:
    if selected_regions:
        filtered = filtered[filtered["지역"].isin(selected_regions)]
    else:
        filtered = filtered.iloc[0:0]

if food_options:
    if selected_foods:
        filtered = filtered[filtered["음식 종류"].isin(selected_foods)]
    else:
        filtered = filtered.iloc[0:0]

if grade_options:
    if selected_grades:
        filtered = filtered[filtered["미쉐린 등급"].isin(selected_grades)]
    else:
        filtered = filtered.iloc[0:0]

if price_range is not None:
    filtered = filtered[
        filtered["가격"].between(
            price_range[0], price_range[1]
        )
        | filtered["가격"].isna()
    ]

# ==========================================
# 9. KPI 카드
# ==========================================
st.divider()
st.subheader("📊 데이터 핵심 지표")

col1, col2, col3, col4 = st.columns(4)

col1.metric("전체 식당", f"{len(df):,}곳")
col2.metric("검색 결과", f"{len(filtered):,}곳")
col3.metric("지역 수", f"{filtered['지역'].nunique():,}개")

if filtered["가격"].notna().any():
    average_price = filtered["가격"].mean()
    col4.metric("평균 가격", f"{average_price:,.0f}원")
else:
    col4.metric("평균 가격", "가격 데이터 없음")

# ==========================================
# 10. 탭 구성
# ==========================================
tab_map, tab_analysis, tab_data = st.tabs(
    ["🗺️ 레스토랑 지도", "📈 통계 분석", "📋 전체 데이터"]
)

# ==========================================
# 11. 지도
# ==========================================
with tab_map:
    st.subheader("🗺️ 레스토랑 위치 시각화")

    exact_map_data = filtered[filtered["좌표 유효"]].copy()

    if not exact_map_data.empty:
        # 실제 좌표가 있는 식당
        center_lat = exact_map_data["위도"].mean()
        center_lon = exact_map_data["경도"].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles="CartoDB positron"
        )

        cluster = MarkerCluster().add_to(m)

        for _, row in exact_map_data.iterrows():
            restaurant_name = html.escape(row["식당명"])
            region = html.escape(row["지역"])
            food = html.escape(row["음식 종류"])
            grade = html.escape(row["미쉐린 등급"])
            address = html.escape(row["주소"])

            price_text = (
                f"{row['가격']:,.0f}원"
                if pd.notna(row["가격"])
                else "정보 없음"
            )

            popup_html = f"""
            <div style="width:230px">
                <h4>{restaurant_name}</h4>
                <b>지역:</b> {region}<br>
                <b>음식:</b> {food}<br>
                <b>등급:</b> {grade}<br>
                <b>가격:</b> {price_text}<br>
                <b>주소:</b> {address}
            </div>
            """

            folium.Marker(
                location=[row["위도"], row["경도"]],
                tooltip=restaurant_name,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
            ).add_to(cluster)

        st_folium(m, width=None, height=620, key="exact_restaurant_map")

        st.success(
            f"정확한 좌표가 입력된 식당 {len(exact_map_data)}곳을 표시했습니다."
        )

    else:
        # 정확한 좌표가 없으면 지역 단위 집계 지도 표시
        st.warning(
            "식당별 위도·경도 데이터가 없어 개별 식당 위치는 표시할 수 없습니다. "
            "대신 지역별 식당 수를 대표 좌표에 표시합니다."
        )

        regional_data = filtered[
            filtered["지역"].str.strip() != ""
        ].copy()

        if not regional_data.empty:
            regional_counts = (
                regional_data.groupby("지역")
                .size()
                .reset_index(name="식당 수")
            )

            map_points = []

            for _, row in regional_counts.iterrows():
                region_name = row["지역"]
                count = int(row["식당 수"])

                coords = REGION_COORDS.get(region_name)

                if coords:
                    map_points.append({
                        "지역": region_name,
                        "식당 수": count,
                        "위도": coords[0],
                        "경도": coords[1]
                    })

            if map_points:
                point_df = pd.DataFrame(map_points)

                m = folium.Map(
                    location=[
                        point_df["위도"].mean(),
                        point_df["경도"].mean()
                    ],
                    zoom_start=6,
                    tiles="CartoDB positron"
                )

                for _, row in point_df.iterrows():
                    region_name = html.escape(row["지역"])
                    count = int(row["식당 수"])

                    folium.CircleMarker(
                        location=[row["위도"], row["경도"]],
                        radius=max(8, min(30, count * 2)),
                        color="#2563eb",
                        fill=True,
                        fill_color="#60a5fa",
                        fill_opacity=0.65,
                        tooltip=f"{region_name}: {count}개",
                        popup=f"<b>{region_name}</b><br>식당 수: {count}개"
                    ).add_to(m)

                    folium.Marker(
                        location=[row["위도"], row["경도"]],
                        icon=folium.DivIcon(
                            html=f"""
                            <div style="
                                font-size:14px;
                                font-weight:bold;
                                color:#1e3a8a;
                                text-align:center;
                                width:100px;
                                ">
                                {region_name}<br>{count}곳
                            </div>
                            """
                        )
                    ).add_to(m)

                st_folium(m, width=None, height=620, key="regional_map")

                st.caption(
                    "이 지도는 지역 대표 좌표를 이용한 집계 지도이며 "
                    "각 식당의 정확한 위치를 나타내지 않습니다."
                )
            else:
                st.info(
                    "지역 이름을 좌표와 연결하지 못했습니다. "
                    "서울, 부산 등 지역 이름을 확인해 주세요."
                )
        else:
            st.info("지역 데이터가 없어 지도를 표시할 수 없습니다.")

# ==========================================
# 12. 통계 분석
# ==========================================
with tab_analysis:
    st.subheader("📈 지역별 레스토랑 분포")

    region_count = (
        filtered["지역"]
        .value_counts()
        .rename_axis("지역")
        .reset_index(name="식당 수")
    )

    if not region_count.empty:
        st.bar_chart(
            region_count.set_index("지역")["식당 수"]
        )
    else:
        st.info("지역 데이터가 없습니다.")

    st.divider()
    st.subheader("🍜 음식 종류별 분포")

    food_count = (
        filtered["음식 종류"]
        .value_counts()
        .rename_axis("음식 종류")
        .reset_index(name="식당 수")
    )

    if not food_count.empty:
        st.bar_chart(
            food_count.set_index("음식 종류")["식당 수"]
        )
    else:
        st.info("음식 종류 데이터가 없습니다.")

    st.divider()
    st.subheader("⭐ 미쉐린 등급별 분포")

    grade_count = (
        filtered["미쉐린 등급"]
        .value_counts()
        .rename_axis("등급")
        .reset_index(name="식당 수")
    )

    if not grade_count.empty:
        st.bar_chart(
            grade_count.set_index("등급")["식당 수"]
        )
    else:
        st.info("등급 데이터가 없습니다.")

    st.divider()
    st.subheader("💰 가격 분석")

    price_data = filtered["가격"].dropna()

    if not price_data.empty:
        price_col1, price_col2, price_col3 = st.columns(3)

        price_col1.metric("최저 가격", f"{price_data.min():,.0f}원")
        price_col2.metric("최고 가격", f"{price_data.max():,.0f}원")
        price_col3.metric("중앙값", f"{price_data.median():,.0f}원")

        st.write("가격 데이터 분포")
        st.bar_chart(price_data.reset_index(drop=True))
    else:
        st.warning(
            "가격 정보가 없어 가격 분석을 할 수 없습니다. "
            "CSV에 숫자 형태의 가격 데이터를 추가하세요."
        )

# ==========================================
# 13. 데이터 테이블
# ==========================================
with tab_data:
    st.subheader("📋 레스토랑 데이터")

    display_df = filtered.drop(
        columns=["좌표 유효"],
        errors="ignore"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.write(f"현재 표시 데이터: {len(filtered)}개")

    csv_download = display_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 현재 검색 결과 다운로드",
        data=csv_download,
        file_name="michelin_filtered_data.csv",
        mime="text/csv"
    )

# ==========================================
# 14. 프로젝트 설명
# ==========================================
st.divider()

with st.expander("📖 프로젝트 설명 및 분석 방법"):
    st.markdown("""
    ### 프로젝트 주제
    미쉐린 레스토랑 신규 목록을 활용한 공간 분포 및 데이터 시각화

    ### 프로젝트 목적
    레스토랑 데이터를 지도와 통계 차트로 표현하여
    지역별 분포, 음식 종류, 미쉐린 등급의 특징을 분석한다.

    ### 활용 기술
    - Python: 데이터 처리 및 프로그램 구현
    - Streamlit: 웹 대시보드 제작
    - Pandas: CSV 데이터 분석 및 정제
    - Folium: 지도 시각화
    - MarkerCluster: 지도 마커 그룹화

    ### 분석 항목
    1. 지역별 레스토랑 수 비교
    2. 음식 종류별 레스토랑 분포
    3. 미쉐린 등급별 구성
    4. 가격 데이터 분석
    5. 지도 기반 공간 분포 탐색

    ### 데이터 한계
    주소 및 좌표가 없는 경우 정확한 위치를 표시할 수 없다.
    지역 단위 지도는 대표 좌표를 사용하므로 식당의 실제 위치와 다를 수 있다.
    가격 데이터가 없으면 가격 분석 결과에 반영되지 않는다.
    """)

st.caption(
    "Michelin Restaurant Explorer | Python · Streamlit · Pandas · Folium"
)
