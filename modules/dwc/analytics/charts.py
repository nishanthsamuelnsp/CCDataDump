import altair as alt
import pandas as pd
import streamlit as st

def render_metric_chart(
    df,
    metric_key,
    title,
    baseline,
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

    baseline_df = pd.DataFrame(
        {
            "Period": chart_df["Period"],
            "Baseline": baseline,
        }
    )
    
    line = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x="Period:T",
            y=alt.Y(title, title=title),
        )
    )
    
    baseline_line = (
        alt.Chart(baseline_df)
        .mark_rule(
            strokeDash=[6, 4],
        )
        .encode(
            y="Baseline:Q",
        )
    )
    
    st.altair_chart(
        line + baseline_line,
        use_container_width=True,
    )
