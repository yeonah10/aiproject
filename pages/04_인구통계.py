
# 남녀 인구 비율 원형 그래프
st.divider()
st.subheader("🥧 남녀 인구 비율")

male_column = f"{year}년_남_거주자_총인구수"
female_column = f"{year}년_여_거주자_총인구수"

male_population = pd.to_numeric(
    str(selected[male_column]).replace(",", ""),
    errors="coerce"
)

female_population = pd.to_numeric(
    str(selected[female_column]).replace(",", ""),
    errors="coerce"
)

gender_df = pd.DataFrame({
    "성별": ["남성", "여성"],
    "인구수": [male_population, female_population]
})

gender_df["인구수"] = gender_df["인구수"].fillna(0)

fig_gender = go.Figure(
    data=[
        go.Pie(
            labels=gender_df["성별"],
            values=gender_df["인구수"],
            hole=0.35,
            marker=dict(
                colors=["#87CEEB", "#FFB6C1"]
            ),
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>"
                "인구수: %{value:,.0f}명<br>"
                "비율: %{percent}"
                "<extra></extra>"
            )
        )
    ]
)

fig_gender.update_layout(
    title={
        "text": f"{region} {year}년 남녀 인구 비율",
        "x": 0.5
    },
    height=450,
    showlegend=True,
    paper_bgcolor="white",
    font=dict(
        family="sans-serif",
        size=14,
        color="#333333"
    )
)

st.plotly_chart(
    fig_gender,
    use_container_width=True
)
