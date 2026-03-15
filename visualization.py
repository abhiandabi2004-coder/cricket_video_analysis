import streamlit as st
import pandas as pd
import plotly.express as px

def show_results(angles, result):

    st.subheader("Technique Analysis")

    st.metric("Average Angle", round(result["average_angle"],2))

    st.write("Feedback:", result["feedback"])

    df = pd.DataFrame({
        "frame": list(range(len(angles))),
        "angle": angles
    })

    fig = px.line(df, x="frame", y="angle", title="Backlift Angle Trend")

    st.plotly_chart(fig)