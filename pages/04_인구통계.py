# 꺾은선 그래프
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",

        line=dict(
            color=graph_color,
            width=4
        ),

        marker=dict(
            color=graph_color,
            size=9
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)
