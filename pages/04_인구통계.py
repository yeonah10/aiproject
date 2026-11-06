
# =========================
# 9-1. 구별 전년도 대비 인구 증감률 그래프
# =========================

st.divider()
st.subheader("📊 구별 전년도 대비 인구 증감률")

if year == 2020:
    st.info("2020년은 전년도 데이터가 없어 증감률을 계산할 수 없습니다.")

else:
    import plotly.express as px

    previous_year = year - 1

    change_data = []

    # 인천광역시 전체 제외
    district_df = df[df["지역명"] != "인천광역시"]

    for _, row in district_df.iterrows():
        current_population = get_population(row, year, "")
        previous_population = get_population(row, previous_year, "")

        if previous_population == 0:
            continue

        difference = current_population - previous_population
        change_rate = (difference / previous_population) * 100

        change_data.append({
            "지역명": row["지역명"],
            "증감률": change_rate,
            "증감 인구": difference
        })

    change_df = pd.DataFrame(change_data)

    if not change_df.empty:
        change_df = change_df.sort_values(
            "증감률", ascending=False
        )

        fig = px.bar(
            change_df,
            x="지역명",
            y="증감률",
            color="증감률",
            color_continuous_scale=[
                "#F4A6B8",
                "#FCE4EC",
                "#D9EAF7",
                "#87CEEB"
            ],
            text=change_df["증감률"].apply(
                lambda x: f"{x:+.2f}%"
            ),
            hover_data={
                "증감 인구": ":,.0f",
                "증감률": ":.2f"
            }
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="행정구역",
            yaxis_title="인구 증감률 (%)",
            coloraxis_showscale=False,
            yaxis=dict(zeroline=True),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            change_df.rename(columns={
                "증감률": "인구 증감률(%)",
                "증감 인구": "인구 증감 수(명)"
            }).style.format({
                "인구 증감률(%)": "{:+.2f}%",
                "인구 증감 수(명)": "{:+,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("증감률을 계산할 데이터가 없습니다.")
