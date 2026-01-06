import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="World Population Dashboard",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("world_population.csv")
    return df

df = load_data()

# Sidebar
st.sidebar.title("Filter")

continents = ["Semua"] + sorted(df["Continent"].unique().tolist())
selected_continent = st.sidebar.selectbox("Benua", continents)

top_n = st.sidebar.slider("Top N Negara", min_value=5, max_value=50, value=10)

if selected_continent == "Semua":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Continent"] == selected_continent]

st.title("World Population Dashboard")

col1, col2, col3, col4 = st.columns(4)

total_pop_2022 = filtered_df["2022 Population"].sum()
total_countries = len(filtered_df)
avg_growth_rate = filtered_df["Growth Rate"].mean()
avg_density = filtered_df["Density (per km²)"].mean()

col1.metric("Total Populasi 2022", f"{total_pop_2022/1e9:.2f} Miliar")
col2.metric("Jumlah Negara", f"{total_countries}")
col3.metric("Growth Rate", f"{avg_growth_rate:.4f}")
col4.metric("Kepadatan", f"{avg_density:.2f}/km²")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"Top {top_n} Negara Populasi Terbesar")
    top_countries = filtered_df.nlargest(top_n, "2022 Population")[["Country/Territory", "2022 Population", "Continent"]]
    
    fig_bar = px.bar(
        top_countries,
        x="2022 Population",
        y="Country/Territory",
        orientation="h",
        color="Country/Territory",
        labels={"2022 Population": "Populasi", "Country/Territory": "Negara"}
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Distribusi per Benua")
    continent_pop = df.groupby("Continent")["2022 Population"].sum().reset_index()
    
    fig_pie = px.pie(
        continent_pop,
        values="2022 Population",
        names="Continent",
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Tren Populasi")

available_countries = filtered_df["Country/Territory"].tolist()
selected_countries = st.multiselect(
    "Pilih Negara",
    available_countries,
    default=available_countries[:3] if len(available_countries) >= 3 else available_countries
)

if selected_countries:
    # Tahun-tahun yang tersedia
    years = ["1970 Population", "1980 Population", "1990 Population", 
             "2000 Population", "2010 Population", "2015 Population", 
             "2020 Population", "2022 Population"]
    year_labels = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]
    
    trend_data = []
    for country in selected_countries:
        country_data = filtered_df[filtered_df["Country/Territory"] == country]
        for i, year_col in enumerate(years):
            trend_data.append({
                "Negara": country,
                "Tahun": year_labels[i],
                "Populasi": country_data[year_col].values[0]
            })
    
    trend_df = pd.DataFrame(trend_data)
    
    fig_line = px.line(
        trend_df,
        x="Tahun",
        y="Populasi",
        color="Negara",
        markers=True
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

col_scatter, col_map = st.columns(2)

with col_scatter:
    st.subheader("Growth Rate vs Kepadatan")
    
    fig_scatter = px.scatter(
        filtered_df,
        x="Density (per km²)",
        y="Growth Rate",
        size="2022 Population",
        color="Country/Territory",
        hover_name="Country/Territory",
        size_max=50
    )
    fig_scatter.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_map:
    st.subheader("Peta Populasi 2022")
    
    fig_map = px.choropleth(
        df,
        locations="CCA3",
        color="2022 Population",
        hover_name="Country/Territory",
        color_continuous_scale="Blues"
    )
    fig_map.update_layout(height=400, geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Data")

display_cols = ["Rank", "Country/Territory", "Capital", "Continent", 
                "2022 Population", "Growth Rate", "Density (per km²)"]

st.dataframe(filtered_df[display_cols].sort_values("Rank"), use_container_width=True, height=300)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download CSV", csv, "data.csv", "text/csv")