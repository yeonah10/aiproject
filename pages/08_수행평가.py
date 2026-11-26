
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ----------------------------
# 기본 설정
# ----------------------------
st.set_page_config(
    page_title="Michelin Restaurant Explorer",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Michelin New Restaurants Explorer")
st.markdown(
    "### 미쉐린 가이드 신규 레스토랑 데이터 탐색 및 공간 분석"
)
st.caption(
    "지역별 분포, 음식 종류, 등급을 필터링하고 지도에서 레스토랑 위치를 탐색합니다."
)

# ----------------------------
# 데이터 입력 안내
# ----------------------------
st.sidebar.header("📂 데이터")
uploaded_file = st.sidebar.file_uploader(
    "레스토랑 CSV 업로드",
    type=["csv"]
)

# CSV 양식
template = pd.DataFrame({
    "식당명": ["예시 식당"],
    "지역": ["서울"],
    "음식 종류": ["한식"],
    "미쉐린 등급": ["신규"],
    "가격": [20000],
    "주소": ["서울특별시 예시 주소"],
    "위도": [37.5665],
    "경도": [126.9780]
})

st.sidebar.download_button(
    "📥 CSV 입력 양식 다운로드",
    data=template.to_csv(index=False).encode("utf-8-sig"),
    file_name="restaurant_template.csv",
    mime="text/csv"
)

# ----------------------------
# 데이터 불러오기
# ----------------------------
if uploaded_file is None:
    st.info("왼쪽 메뉴에서 레스토랑 CSV 파일을 업로드하세요.")

    st.markdown("#### 필요한 데이터 형식")
    st.dataframe(template, use_container_width=True)

    st.markdown("""
    **필수 컬럼**
    - 식당명
    - 지역
    - 음식 종류
    - 미쉐린 등급
    - 가격
    - 주소
    - 위도
    - 경도

    좌표가 있어야 식당별 실제 위치를 지도에 표시할 수 있습니다.
    """)
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

required_columns = [
    "식당명", "지역", "음식 종류", "미쉐린 등급",
    "가격", "주소", "위도", "경도"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"누락된 컬럼: {', '.join(missing_columns)}")
    st.stop()

# 데이터 정리
df = df.copy()

for col in ["식당명", "지역", "음식 종류", "미쉐린 등급", "주소"]:
    df[col] = df[col].fillna("").astype(str).str.strip()

df["가격"] = pd.to_numeric(df["가격"], errors="coerce")
df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

df = df.dropna(subset=["식당명"])
df = df.drop_duplicates(subset=["식당명", "주소"])

# 좌표 유효성 검사
df["좌표 유효"] = (
    df["위도"].between(33, 39)
    & df["경도"].between(124, 132)
)

# ----------------------------
# 사이드바 필터
# ----------------------------
st.sidebar.header("🔎 검색 및 필터")

search = st.sidebar.text_input(
    "식당 이름 검색",
    placeholder="식당 이름 입력"
)

regions = sorted(
    [x for x in df["지역"].unique() if x]
)

selected_regions = st.sidebar.multiselect(
    "지역 선택",
    regions,
    default=regions
)

foods = sorted(
    [x for x in df["음식 종류"].unique() if x]
)

selected_foods = st.sidebar.multiselect(
    "음식 종류 선택",
    foods,
    default=foods
)

grades = sorted(
    [x for x in df["미쉐린 등급"].unique() if x]
)

selected_grades = st.sidebar.multiselect(
    "미쉐린 분류 선택",
    grades,
    default=grades
)

# 가격 필터
valid_prices = df["가격"].dropna()

if len(valid_prices) > 0:
    min_price = int(valid_prices.min())
    max_price = int(valid_prices.max())

    if min_price < max_price:
        price_range = st.sidebar.slider(
            "가격 범위 (원)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=max(1000, ((max_price-min_price)//100 or 1000))
        )
    else:
        price_range = (min_price, max_price)
else:
    price_range = None

# ----------------------------
# 필터 적용
# ----------------------------
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["식당명"].str.contains(
            search, case=False, na=False
        )
    ]

if selected_regions:
    filtered = filtered[
        filtered["지역"].isin(selected_regions)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_foods:
    filtered = filtered[
        filtered["음식 종류"].isin(selected_foods)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_grades:
    filtered = filtered[
        filtered["미쉐린 등급"].isin(selected_grades)
    ]
else:
    filtered = filtered.iloc[0:0]

if price_range is not None:
    filtered = filtered[
        filtered["가격"].between(
            price_range[0], price_range[1]
        )
        | filtered["가격"].isna()
    ]

# ----------------------------
# KPI 카드
# ----------------------------
st.divider()
st.subheader("📊 데이터 요약")

col1, col2, col3, col4 = st.columns(4)

col1.metric("전체 식당", f"{len(df):,}개")
col2.metric("필터 결과", f"{len(filtered):,}개")
col3.metric("지역 수", f"{filtered['지역'].nunique():,}개")
col4.metric(
    "평균 가격",
    f"{filtered['가격'].mean():,.0f}원"
    if filtered["가격"].notna().any()
    else "데이터 없음"
)

# ----------------------------
# 탭
# ----------------------------
tab1, tab2, tab3 = st.tabs(
    ["🗺️ 지도", "📈 통계 분석", "📋 데이터"]
)

# ----------------------------
# 지도 탭
# ----------------------------
with tab1:
    st.subheader("레스토랑 위치 지도")

    map_data = filtered[
        filtered["좌표 유효"]
    ].copy()

    if map_data.empty:
        st.warning(
            "선택한 조건에 해당하는 유효한 좌표가 없습니다. "
            "CSV의 위도와 경도를 확인해 주세요."
        )
    else:
        center = [
            map_data["위도"].mean(),
            map_data["경도"].mean()
        ]

        m = folium.Map(
            location=center,
            zoom_start=7,
            tiles="CartoDB positron"
        )

        cluster = MarkerCluster().add_to(m)

        for _, row in map_data.iterrows():
            popup_text = f"""
            <div style='width:220px'>
                <h4>{row['식당명']}</h4>
                <b>지역:</b> {row['지역']}<br>
                <b>음식:</b> {row['음식 종류']}<br>
                <b>분류:</b> {row['미쉐린 등급']}<br>
                <b>가격:</b> {row['가격']:,.0f}원
                <br><b>주소:</b> {row['주소']}
            </div>
            """

            folium.Marker(
                location=[row["위도"], row["경도"]],
                tooltip=row["식당명"],
                popup=folium.Popup(
                    popup_text, max_width=300
                ),
                icon=folium.Icon(
                    color="red",
                    icon="cutlery",
                    prefix="fa"
                )
            ).add_to(cluster)

        folium.LayerControl().add_to(m)

        st_folium(
            m,
            width=None,
            height=600,
            key="restaurant_map"
        )

        st.caption(
            f"현재 조건에서 {len(map_data)}개 식당이 지도에 표시됩니다."
        )

# ----------------------------
# 통계 분석 탭
# ----------------------------
with tab2:
    st.subheader("지역별 식당 수")

    region_count = (
        filtered["지역"]
        .value_counts()
        .reset_index()
    )
    region_count.columns = ["지역", "식당 수"]

    if not region_count.empty:
        st.bar_chart(
            region_count.set_index("지역")["식당 수"]
        )
    else:
        st.write("표시할 데이터가 없습니다.")

    st.subheader("음식 종류별 분포")

    food_count = (
        filtered["음식 종류"]
        .value_counts()
        .reset_index()
    )
    food_count.columns = ["음식 종류", "식당 수"]

    if not food_count.empty:
        st.bar_chart(
            food_count.set_index("음식 종류")["식당 수"]
        )

    st.subheader("미쉐린 분류별 식당 수")

    grade_count = (
        filtered["미쉐린 등급"]
        .value_counts()
        .reset_index()
    )
    grade_count.columns = ["분류", "식당 수"]

    if not grade_count.empty:
        st.bar_chart(
            grade_count.set_index("분류")["식당 수"]
        )

    st.subheader("가격 분포")

    price_data = filtered["가격"].dropna()

    if not price_data.empty:
        st.bar_chart(
            price_data.reset_index(drop=True),
            y="가격"
        )
        st.write(f"최저 가격: {price_data.min():,.0f}원")
        st.write(f"최고 가격: {price_data.max():,.0f}원")
        st.write(f"중앙값: {price_data.median():,.0f}원")
    else:
        st.info("가격 데이터가 없습니다.")

# ----------------------------
# 데이터 테이블 탭
# ----------------------------
with tab3:
    st.subheader("식당 데이터 상세")

    st.dataframe(
        filtered.drop(columns=["좌표 유효"]),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("CSV 다운로드")

    csv_output = filtered.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 필터 결과 CSV 다운로드",
        data=csv_output,
        file_name="michelin_filtered_restaurants.csv",
        mime="text/csv"
    )

# ----------------------------
# 프로젝트 설명
# ----------------------------
st.divider()

with st.expander("ℹ️ 프로젝트 및 분석 방법"):
    st.markdown("""
    ### 프로젝트 목적
    미쉐린 가이드 신규 레스토랑 데이터를 지도와 통계로 시각화하여
    음식점의 지역적 분포와 음식 종류 및 가격 특성을 분석한다.

    ### 분석 방법
    - CSV 데이터를 활용한 데이터 정리
    - 지역, 음식 종류, 등급, 가격 필터링
    - Folium 기반 공간 시각화
    - 지역별·음식 종류별 빈도 분석
    - 가격 데이터의 평균 및 중앙값 비교

    ### 데이터 주의사항
    지도 위치는 입력된 위도와 경도를 사용한다.
    좌표가 정확하지 않은 경우 실제 위치와 지도 표시가 다를 수 있다.
    가격이 비어 있는 식당은 가격 필터에 의해 제외되지 않도록 처리한다.
    """)

st.caption(
    "Michelin Restaurant Explorer | Python · Streamlit · Pandas · Folium"
)
