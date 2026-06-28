import streamlit as st


def render_metric_chart(
    df,
    metric_key,
    title,
):

    if metric_key not in df.columns:
        return

    chart_df = (
        df[
            ["period_key", metric_key]
        ]
        .dropna()
        .rename(
            columns={
                "period_key": "Period",
                metric_key: title,
            }
        )
    )

    if chart_df.empty:
        return

    st.markdown(f"#### {title}")

    st.line_chart(
        chart_df,
        x="Period",
        y=title,
        use_container_width=True,
    )
