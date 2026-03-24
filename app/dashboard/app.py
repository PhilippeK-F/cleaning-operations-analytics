import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER", "cleaning")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cleaning")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5436")
DB_NAME = os.getenv("DB_NAME", "cleaning_analytics")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# Color maps
COLOR_MAP_STATUS = {
    "completed": "#2ECC71",
    "in_progress": "#3498DB",
    "planned": "#F1C40F",
    "delayed": "#E74C3C",
}

COLOR_MAP_METHOD = {
    "manual": "#3498DB",
    "machine": "#9B59B6",
    "disinfection": "#E74C3C",
}

st.set_page_config(page_title="Cleaning Operations Analytics", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM cleaning_tasks", engine)
    df["scheduled_date"] = pd.to_datetime(df["scheduled_date"])
    df["completed_date"] = pd.to_datetime(df["completed_date"], errors="coerce")
    return df


df = load_data()

# Sidebar
st.sidebar.title("🧹 Cleaning Analytics")
page = st.sidebar.radio("Navigation", ["Overview", "Team Performance"])

st.sidebar.header("Filters")

selected_site = st.sidebar.multiselect(
    "Site",
    options=sorted(df["site_name"].dropna().unique()),
    default=sorted(df["site_name"].dropna().unique()),
)

selected_zone = st.sidebar.multiselect(
    "Zone Type",
    options=sorted(df["zone_type"].dropna().unique()),
    default=sorted(df["zone_type"].dropna().unique()),
)

selected_team = st.sidebar.multiselect(
    "Team",
    options=sorted(df["cleaning_team"].dropna().unique()),
    default=sorted(df["cleaning_team"].dropna().unique()),
)

filtered_df = df[
    df["site_name"].isin(selected_site)
    & df["zone_type"].isin(selected_zone)
    & df["cleaning_team"].isin(selected_team)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


if page == "Overview":
    st.title("🧹 Industrial Cleaning Operations Analytics")
    st.caption("Operational dashboard to monitor cleaning tasks, quality and priority levels.")

    # KPIs
    total_tasks = len(filtered_df)
    delayed_tasks = int((filtered_df["status"] == "delayed").sum())
    avg_quality = round(filtered_df["quality_score"].mean(), 1) if total_tasks > 0 else 0
    priority_total = int(filtered_df["priority_score"].sum()) if total_tasks > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total_tasks)
    col2.metric("Delayed Tasks", delayed_tasks)
    col3.metric("Avg Quality Score", avg_quality)
    col4.metric("Global Priority Score", priority_total)

    st.divider()

    # Tasks over time
    tasks_over_time = (
        filtered_df.groupby(filtered_df["scheduled_date"].dt.date)
        .size()
        .reset_index(name="tasks")
    )

    fig_time = px.line(
        tasks_over_time,
        x="scheduled_date",
        y="tasks",
        title="Tasks Over Time",
        markers=True,
    )
    fig_time.update_traces(line=dict(color="#3498DB", width=3))
    st.plotly_chart(fig_time, use_container_width=True)

    # Two charts
    col_left_1, col_right_1 = st.columns(2)

    with col_left_1:
        zone_counts = filtered_df["zone_type"].value_counts().reset_index()
        zone_counts.columns = ["zone_type", "count"]

        fig_zone = px.bar(
            zone_counts,
            x="zone_type",
            y="count",
            title="Tasks by Zone Type",
            color="zone_type",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig_zone, use_container_width=True)

    with col_right_1:
        team_counts = filtered_df["cleaning_team"].value_counts().reset_index()
        team_counts.columns = ["cleaning_team", "count"]

        fig_team = px.bar(
            team_counts,
            x="cleaning_team",
            y="count",
            title="Tasks by Team",
            color="cleaning_team",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig_team, use_container_width=True)

    # Two charts
    col_left_2, col_right_2 = st.columns(2)

    with col_left_2:
        status_counts = filtered_df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]

        fig_status = px.pie(
            status_counts,
            names="status",
            values="count",
            title="Task Status Distribution",
            color="status",
            color_discrete_map=COLOR_MAP_STATUS,
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right_2:
        task_counts = filtered_df["task_type"].value_counts().reset_index()
        task_counts.columns = ["task_type", "count"]

        fig_task = px.bar(
            task_counts,
            x="task_type",
            y="count",
            title="Tasks by Task Type",
            color="task_type",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        st.plotly_chart(fig_task, use_container_width=True)

    # Two charts
    col_left_3, col_right_3 = st.columns(2)

    with col_left_3:
        method_counts = filtered_df["cleaning_method"].value_counts().reset_index()
        method_counts.columns = ["cleaning_method", "count"]

        fig_method = px.pie(
            method_counts,
            names="cleaning_method",
            values="count",
            title="Cleaning Methods",
            color="cleaning_method",
            color_discrete_map=COLOR_MAP_METHOD,
        )
        st.plotly_chart(fig_method, use_container_width=True)

    with col_right_3:
        site_quality = (
            filtered_df.groupby("site_name", as_index=False)["quality_score"]
            .mean()
            .sort_values("quality_score", ascending=False)
        )

        fig_quality = px.bar(
            site_quality,
            x="site_name",
            y="quality_score",
            title="Average Quality Score by Site",
            color="site_name",
        )
        st.plotly_chart(fig_quality, use_container_width=True)

    # Map
    st.divider()
    st.subheader("📍 Cleaning Activity Map")

    map_df = (
        filtered_df.groupby(["site_name", "latitude", "longitude"], as_index=False)
        .agg(
            task_count=("task_id", "count"),
            total_priority=("priority_score", "sum"),
            avg_quality=("quality_score", "mean"),
            delayed_tasks=("status", lambda x: (x == "delayed").sum()),
        )
    )

    if not map_df.empty:
        fig_map = px.scatter_mapbox(
            map_df,
            lat="latitude",
            lon="longitude",
            size="task_count",
            color="total_priority",
            hover_name="site_name",
            hover_data={
                "task_count": True,
                "total_priority": True,
                "avg_quality": ":.1f",
                "delayed_tasks": True,
                "latitude": False,
                "longitude": False,
            },
            zoom=4.5,
            height=500,
            color_continuous_scale="YlOrRd",
            title="Cleaning Activity by Site",
        )

        fig_map.update_traces(marker=dict(opacity=0.8))
        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
        )

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No map data available for the selected filters.")

    # Critical tasks
    st.subheader("🔥 Top Critical Tasks")

    critical_df = filtered_df.sort_values(
        by=["priority_score", "dirt_level"],
        ascending=False,
    ).head(20)

    st.dataframe(
        critical_df,
        use_container_width=True,
        column_config={
            "priority_score": st.column_config.ProgressColumn(
                "Priority Score",
                min_value=0,
                max_value=10,
            ),
            "quality_score": st.column_config.ProgressColumn(
                "Quality Score",
                min_value=0,
                max_value=100,
            ),
        },
    )


if page == "Team Performance":
    st.title("👷 Team Performance Dashboard")
    st.caption("Analyze workload, delays and quality performance by cleaning team.")

    team_df = (
        filtered_df.groupby("cleaning_team", as_index=False)
        .agg(
            total_tasks=("task_id", "count"),
            total_duration=("estimated_duration_min", "sum"),
            delayed_tasks=("status", lambda x: (x == "delayed").sum()),
            avg_quality=("quality_score", "mean"),
            total_priority=("priority_score", "sum"),
        )
    )

    team_df["delay_rate"] = (
        team_df["delayed_tasks"] / team_df["total_tasks"]
    ).round(2)

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Workload (min)", int(team_df["total_duration"].sum()))
    col2.metric("Total Tasks", int(team_df["total_tasks"].sum()))
    col3.metric("Avg Quality", round(team_df["avg_quality"].mean(), 1))

    st.divider()

    # Workload
    fig_workload = px.bar(
        team_df,
        x="cleaning_team",
        y="total_duration",
        title="Total Workload (minutes) by Team",
        color="cleaning_team",
    )
    st.plotly_chart(fig_workload, use_container_width=True)

    # Delayed tasks
    fig_delay = px.bar(
        team_df,
        x="cleaning_team",
        y="delayed_tasks",
        title="Delayed Tasks by Team",
        color="cleaning_team",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    st.plotly_chart(fig_delay, use_container_width=True)

    # Average quality
    fig_quality_team = px.bar(
        team_df,
        x="cleaning_team",
        y="avg_quality",
        title="Average Quality Score by Team",
        color="cleaning_team",
    )
    st.plotly_chart(fig_quality_team, use_container_width=True)

    st.divider()
    st.subheader("🏆 Team Ranking")

    ranking_df = team_df.sort_values(
        by=["total_priority", "delay_rate"],
        ascending=[False, True],
    )

    st.dataframe(
        ranking_df,
        use_container_width=True,
        column_config={
            "avg_quality": st.column_config.ProgressColumn(
                "Quality",
                min_value=0,
                max_value=100,
            ),
            "delay_rate": st.column_config.ProgressColumn(
                "Delay Rate",
                min_value=0,
                max_value=1,
            ),
        },
    )