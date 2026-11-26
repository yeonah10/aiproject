import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="미쉐린 2026 식당 분석", page_icon="🍽️", layout="wide")
st.title("🍽️ 미쉐린 가이드 2026 식당 분석")
st.caption("현재 제공된 CSV 100행을 분석합니다. 전체 공식 233곳 목록이 아니며, 주소·실제 메뉴 가격은 데이터에 없습니다.")

DATA_PATH = "michelin_2026_korea.csv"
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    for col in ["식당명", "지역", "미쉐린 등급", "음식 종류", "가격 기준", "공식 링크", "출처/확인 상태"]:
        if col not in df.columns:
            df[col] = pd.NA
    return df

df = load_data()
df["음식 종류"] = df["음식 종류"].fillna("미확인")
df["가격 기준"] = df["가격 기준"].fillna("가격 정보 없음")
df["지역"] = df["지역"].fillna("지역 정보 없음")

# Sidebar filters
st.sidebar.header("검색 및 필터")
city_options = sorted(df["지역"].dropna().unique().tolist())
cities = st.sidebar.multiselect("지역", city_options, default=city_options)
grade_options = sorted(df["미쉐린 등급"].dropna().unique().tolist())
grades = st.sidebar.multiselect("등급", grade_options, default=grade_options)
food_options = sorted(df["음식 종류"].dropna().unique().tolist())
foods = st.sidebar.multiselect("음식 종류", food_options, default=food_options)
search = st.sidebar.text_input("식당명 검색")

filtered = df[df["지역"].isin(cities) & df["미쉐린 등급"].isin(grades) & df["음식 종류"].isin(foods)]
if search:
    filtered = filtered[filtered["식당명"].str.contains(search, case=False, na=False)]

# KPI
c1,c2,c3,c4 = st.columns(4)
c1.metric("현재 데이터 행", f"{len(df):,}")
c2.metric("필터 결과", f"{len(filtered):,}")
c3.metric("식당 이름 고유 수", f"{df['식당명'].nunique():,}")
c4.metric("결측 음식 종류", f"{(df['음식 종류']=='미확인').sum():,}")

st.subheader("데이터 품질 요약")
quality = pd.DataFrame({
    "항목":["행 수","열 수","중복 행","식당명 중복","음식 종류 결측","가격 정보 결측","공식 링크 결측"],
    "값":[len(df),df.shape[1],df.duplicated().sum(),df["식당명"].duplicated().sum(),
           df["음식 종류"].isna().sum(),(df["가격 기준"]=="가격 정보 없음").sum(),df["공식 링크"].isna().sum()]
})
st.dataframe(quality, use_container_width=True, hide_index=True)
st.warning("CSV에는 주소와 공식 링크가 비어 있습니다. 아래 지도는 개별 식당 위치가 아니라 서울·부산 도시 중심의 참고 마커입니다.")

# charts
left,right=st.columns(2)
with left:
    grade_count=filtered["미쉐린 등급"].value_counts().reset_index()
    grade_count.columns=["등급","식당 수"]
    st.plotly_chart(px.bar(grade_count,x="등급",y="식당 수",title="등급별 식당 수",text="식당 수"),use_container_width=True)
with right:
    city_count=filtered["지역"].value_counts().reset_index()
    city_count.columns=["지역","식당 수"]
    st.plotly_chart(px.pie(city_count,names="지역",values="식당 수",title="지역별 데이터 비중"),use_container_width=True)

food_count=filtered["음식 종류"].value_counts().head(15).reset_index()
food_count.columns=["음식 종류","식당 수"]
st.plotly_chart(px.bar(food_count,x="식당 수",y="음식 종류",orientation="h",title="음식 종류 상위 15개"),use_container_width=True)

st.subheader("식당 목록")
st.dataframe(filtered[["식당명","지역","미쉐린 등급","음식 종류","가격 기준","출처/확인 상태"]],use_container_width=True,hide_index=True)

# Student ranking: only Bib Gourmand rows are price-bounded in this CSV. Ranking is a transparent heuristic, not an objective review.
st.subheader("🎓 고등학생 추천 TOP 10 (가격·메뉴 접근성 기준)")
st.caption("빕 구르망으로 기록된 식당만 후보로 사용했습니다. 가이드의 4만 5천 원 이하 기준은 1인 메뉴가 아니라 가이드 기준이며, 실제 방문 전 메뉴 가격을 확인하세요. 점수는 데이터상 메뉴 친숙도 중심의 참고 순위입니다.")
bib = df[df["미쉐린 등급"].eq("빕 구르망")].copy()
rank_names = ["정짓간","옥동식","나가하마 만게츠","니시무라멘","교다이야","미진","서령","정면","능동미나리","황금콩밭"]
rank_reason = {
"정짓간":"돼지국밥—익숙한 메뉴, 빕 구르망 가격 기준",
"옥동식":"돼지국밥—단품 식사 메뉴로 선택하기 쉬움",
"나가하마 만게츠":"라멘—메뉴 선택이 비교적 단순하고 친숙함",
"니시무라멘":"라멘—친숙한 면 요리",
"교다이야":"우동—친숙한 면 요리",
"미진":"메밀국수—간단한 면 메뉴",
"서령":"메밀국수—면 요리 중심",
"정면":"국수—친숙한 식사 메뉴",
"능동미나리":"곰탕—한 끼 식사로 접근하기 쉬움",
"황금콩밭":"두부 요리—식사 선택지가 비교적 담백함"
}
ranked = bib[bib["식당명"].isin(rank_names)].copy()
ranked["순위"] = ranked["식당명"].map({n:i+1 for i,n in enumerate(rank_names)})
ranked["추천 이유"] = ranked["식당명"].map(rank_reason)
ranked = ranked.sort_values("순위")
st.dataframe(ranked[["순위","식당명","지역","음식 종류","가격 기준","추천 이유"]],use_container_width=True,hide_index=True)

# Price filter: data only supports Bib Gourmand price guideline; don't infer price tiers.
st.subheader("💰 가격 정보별 추천")
st.info("현재 파일에는 빕 구르망 54개에 대해서만 '4만 5천원 이하 (가이드 기준)'이 기록되어 있습니다. 별 식당의 가격은 비어 있어 가격대별 비교가 불가능합니다.")
price_rows = bib[["식당명","지역","음식 종류","가격 기준"]].drop_duplicates()
st.dataframe(price_rows,use_container_width=True,hide_index=True)

# Folium city-level map
st.subheader("🗺️ 지도")
city_coords = {"서울": (37.5665,126.9780), "부산": (35.1796,129.0756)}
city_data = filtered.groupby("지역").size().reset_index(name="현재 데이터 식당 수")
m=folium.Map(location=[36.2,127.8],zoom_start=7,tiles="OpenStreetMap")
for _,row in city_data.iterrows():
    city=row["지역"]
    if city in city_coords:
        lat,lon=city_coords[city]
        folium.Marker([lat,lon],tooltip=f"{city}: {row['현재 데이터 식당 수']}곳",
                      popup=f"<b>{city}</b><br>현재 CSV 내 식당: {row['현재 데이터 식당 수']}곳",
                      icon=folium.Icon(color="blue",icon="info-sign")).add_to(m)
st_folium(m,width=None,height=520)
st.caption("지도 마커는 도시 중심에 찍힌 지역 표시입니다. 식당별 주소/좌표가 확보되면 개별 식당 핀으로 바꿀 수 있습니다.")

st.subheader("CSV 다운로드")
csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button("현재 필터 결과 CSV 다운로드",csv_bytes,file_name="michelin_filtered_2026.csv",mime="text/csv")

with st.expander("분석 해석 시 주의"):
    st.markdown("""
- 이 데이터는 2026 공식 목록 전체가 아니라 일부 식당을 수집한 100행 파일입니다.
- 공식 링크가 전부 비어 있으며 주소도 포함하지 않습니다.
- 46행의 음식 종류와 가격 정보가 비어 있습니다.
- 가격 기반 학생 추천은 빕 구르망 가격 기준이 기록된 후보에 한해 작성했습니다.
- 추천 순위는 객관적 평점이 아니라 메뉴 친숙도와 식사 접근성을 기준으로 한 간단한 휴리스틱입니다.
- 개별 식당 좌표가 없으므로 지도는 서울·부산 도시 중심 표시입니다.

