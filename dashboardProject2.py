import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")


st.title("ATP Tour Leaderboard Dashboard")

# Load data
@st.cache_data
def load_data():
    serve = pd.read_csv("serve_leaderboard_cleaned.csv")
    return_ = pd.read_csv("return_leaderboard_cleaned.csv")
    return serve, return_

serve_df, return_df = load_data()

# Tabs: Serve vs Return
tab1, tab2 = st.tabs(["Serve Leaderboard", "Return Leaderboard"])

with tab1:
    st.header("Serve Leaderboard")

    col1, col2, col3 = st.columns([2, 1, 1.5])  # Wider text, narrower image

    with col1:
        st.markdown("""
        The Serve Leaderboard highlights the most effective servers on the ATP Tour.  
        It measures stats like "first serve percentage", "aces per match", and "service games won".  
        These serve metrics give insight into which players dominate with their serve, which has become
        one of the most critical shots in modern tennis. 
        These statistics do not show the official ATP Ranking of the players but only the Serve Ranking. 
        So just the top 50 servers for each season.
        This leaderboard updates yearly and can reveal how playing styles or surfaces influence serve effectiveness.
                    

        The Line Chart Graphic gives an overview over the statistics of the best 50 servers for the selected year. 
        The best fit line gives the average of the stats and shows the user how close the players lie together.
                    
        The Bar Chart at the bottom left lets the user compare individual players with each other regarding the selected statistic.
        The user can chose an unlitimted amount of players to compare.
                    
        The Scatterplot at the bottom right lets the user compare to differnt statistics with each other to give more context to each one.
        This way the user can see how effective the players shots are and in which way the player performs better/worse.
        """)

    with col2:
        st.markdown("<div style='margin-left: 30px'>", unsafe_allow_html=True)
        st.image("https://alignbodyclinic.co.uk/wp-content/uploads/2018/05/federer.png.webp", caption="Roger Federers Serve", width=300, )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div style='margin-right: 900px'>", unsafe_allow_html=True)
        st.image("https://static.independent.co.uk/s3fs-public/thumbnails/image/2014/08/28/21/isner.jpg?quality=75&width=1250&crop=3%3A2%2Csmart&auto=webp", caption = "John Isner's Serve", width=600)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Year slider ---
    min_year = int(serve_df["Year"].min())
    max_year = int(serve_df["Year"].max())
    selected_year = st.slider("Select Year", min_year, max_year, value=max_year)

    stat_options = [
    "% 1st Serve", "% 1st Serve Points Won", "% 2st Serve Points Won", "% Service Games Won", "Avg. Aces/ Match", "Avg. Double Faults/Match"
    ]
    selected_stat = st.selectbox("Select Statistic", stat_options)

    st.subheader("Line Chart: Player by Standing vs Selected Stat")

    # Filter and sort data by Standing
    filtered_serve = serve_df[serve_df["Year"] == selected_year].sort_values("Standing")

    # Filter and sort data by Standing
    filtered_serve = serve_df[serve_df["Year"] == selected_year].sort_values("Standing")

    # Extract X and Y
    x = filtered_serve["Standing"]
    y = filtered_serve[selected_stat]

    # Fit linear regression line
    coeffs = np.polyfit(x, y, deg=1)
    regression_line = np.poly1d(coeffs)

    # Create figure
    fig = go.Figure()

    # Add data line
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers", name=selected_stat,
        hovertext=filtered_serve["Player"]
    ))

    # Add regression line
    fig.add_trace(go.Scatter(
        x=x, y=regression_line(x),
        mode="lines",
        name="Best Fit Line",
        line=dict(dash="dash", color="red")
    ))

    # Layout
    fig.update_layout(
        title=f"{selected_stat} by Standing – {selected_year}",
        xaxis_title="Standing",
        yaxis_title=selected_stat,
        height=600
    )

    # Show chart
    st.plotly_chart(fig, use_container_width=True, key="serve_line_chart")

    col1, col2 = st.columns(2)

    # --- Column 1: Bar Chart ---
    with col1:
        st.subheader("Bar Chart: Player vs Selected Stat")
        selected_players_bar = st.multiselect(
            "Select Players for Bar Chart",
            options=filtered_serve["Player"].tolist(),
            default=filtered_serve["Player"].head(5),
            key="bar_players"
        )

        bar_df = filtered_serve[filtered_serve["Player"].isin(selected_players_bar)]

        fig_bar = px.bar(
            bar_df,
            x="Player",
            y=selected_stat,
            title=f"{selected_stat} - {selected_year}",
            labels={selected_stat: "%"},
            color="Player",  # enables coloring per player
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="serve_bar_chart")


    # --- Column 2: Scatter Plot ---
    with col2:
        st.subheader("Scatter Plot: Compare Two Serve Stats")
        x_stat = st.selectbox("X-Axis Stat", stat_options, index=0, key="x_stat")
        y_stat = st.selectbox("Y-Axis Stat", stat_options, index=1, key="y_stat")

        if x_stat == y_stat:
            st.warning("Please select different statistics for X and Y axes.")
        else:
           # Scatter with colored dots by player
            fig = px.scatter(
                filtered_serve,
                x=x_stat,
                y=y_stat,
                color="Player",
                hover_name="Player",
                hover_data={x_stat: True, y_stat: True},
                title=f"{y_stat} vs {x_stat} – {selected_year}",
                labels={x_stat: "%", y_stat: "%"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            # Add global best-fit line using numpy
            x_vals = filtered_serve[x_stat]
            y_vals = filtered_serve[y_stat]
            coeffs = np.polyfit(x_vals, y_vals, deg=1)
            regression_line = np.poly1d(coeffs)

            # Overlay the best fit line
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=regression_line(x_vals),
                mode="lines",
                name="Best Fit Line",
                line=dict(color="black", dash="dash")
            ))

            st.plotly_chart(fig, use_container_width=True, key="serve_scatter")



with tab2:
    st.header("Return Leaderboard")
    col1, col2, col3 = st.columns([2, 1, 1])  # Wider text, narrower image

    with col1:
        st.markdown("""
        The Return Leaderboard highlights the most effective returners on the ATP Tour.  
        It measures stats like "return games won", "percentage of return points won", and "break points converted".  
        These return metrics give insight into which players has a good return game and is able to adapt to the opponents serve.
        These statistics do not show the official ATP Ranking of the players but only the Return Ranking. 
        So just the top 50 servers for each season.
        This leaderboard updates yearly and can reveal how playing styles or surfaces influence return effectiveness.
                    

        The Line Chart Graphic gives an overview over the statistics of the best 50 returners for the selected year. 
        The best fit line gives the average of the stats and shows the user how close the players lie together.
                    
        The Bar Chart at the bottom left lets the user compare individual players with each other regarding the selected statistic.
        The user can chose an unlitimted amount of players to compare.
                    
        The Scatterplot at the bottom right lets the user compare to differnt statistics with each other to give more context to each one.
        This way the user can see how effective the players shots are and in which way the player performs better/worse.
        """)

    with col2:
        st.markdown("<div style='margin-left: 30px'>", unsafe_allow_html=True)
        st.image("https://www.atptour.com/-/media/2024-images/news/2024/04/12/15/39/barcelona-2024-viernes-nadal-previa.jpg", caption="Rafael Nadal Return", width=500, )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div style='margin-right: 900px'>", unsafe_allow_html=True)
        st.image("https://img-s-msn-com.akamaized.net/tenant/amp/entityid/AA1xpGdH.img?w=768&h=512&m=6", caption = "Novak Djokovic Return", width=425)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Return stat options ---
    return_stat_options = [
        "% 1st Serve Return Points Won",
        "% 2nd Serve Return Points Won",
        "% Return Games Won",
        "% Break Points Converted",
        "Return Rating"
    ]

    # --- Stat dropdown ---
    selected_return_stat = st.selectbox("Select Return Statistic", return_stat_options)

    # --- Year slider ---
    min_year_r = int(return_df["Year"].min())
    max_year_r = int(return_df["Year"].max())
    selected_year_r = st.slider("Select Year (Return)", min_year_r, max_year_r, value=max_year_r)

    # --- Filter and sort ---
    filtered_return = return_df[return_df["Year"] == selected_year_r].sort_values("Standing")

    # --- Line Chart ---
    st.subheader("Line Chart: Selected Return Stat by Standing")
    fig_return_line = px.line(
        filtered_return,
        x="Standing",
        y=selected_return_stat,
        hover_name="Player",
        markers=True,
        title=f"{selected_return_stat} by Standing – {selected_year_r}",
        labels={"Standing": "Standing", selected_return_stat: "%"}
    )
    st.plotly_chart(fig_return_line, use_container_width=True, key="return_line_chart")

    # --- Two-column layout for bar + scatter ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Bar Chart: Player vs Selected Return Stat")
        selected_players_return = st.multiselect(
            "Select Players (Return)",
            options=filtered_return["Player"].tolist(),
            default=filtered_return["Player"].head(5),
            key="return_bar_players"
        )
        bar_df_return = filtered_return[filtered_return["Player"].isin(selected_players_return)]

        fig_return_bar = px.bar(
            bar_df_return,
            x="Player",
            y=selected_return_stat,
            title=f"{selected_return_stat} – {selected_year_r}",
            labels={selected_return_stat: "%"},
            color="Player",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_return_bar, use_container_width=True, key="return_bar_chart")

    with col2:
        st.subheader("Scatter Plot: Compare Two Return Stats")
        x_stat_r = st.selectbox("X-Axis Stat", return_stat_options, index=0, key="x_stat_r")
        y_stat_r = st.selectbox("Y-Axis Stat", return_stat_options, index=1, key="y_stat_r")

        if x_stat_r == y_stat_r:
            st.warning("Please select different statistics for X and Y axes.")
        else:
            # Scatter with color by player
            fig_return = px.scatter(
                filtered_return,
                x=x_stat_r,
                y=y_stat_r,
                color="Player",
                hover_name="Player",
                hover_data={x_stat_r: True, y_stat_r: True},
                title=f"{y_stat_r} vs {x_stat_r} – {selected_year_r}",
                labels={x_stat_r: "%", y_stat_r: "%"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            # Compute global best-fit line
            x_vals_r = filtered_return[x_stat_r]
            y_vals_r = filtered_return[y_stat_r]
            coeffs_r = np.polyfit(x_vals_r, y_vals_r, deg=1)
            regression_line_r = np.poly1d(coeffs_r)

            # Add best-fit line as dashed black overlay
            fig_return.add_trace(go.Scatter(
                x=x_vals_r,
                y=regression_line_r(x_vals_r),
                mode="lines",
                name="Best Fit Line",
                line=dict(color="black", dash="dash")
            ))

            # Display chart
            st.plotly_chart(fig_return, use_container_width=True, key="return_scatter")



