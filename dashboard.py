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
st.sidebar.info("Filter Benua akan mempengaruhi: Metrics, Top 10 Negara, Tren Populasi, dan Growth Rate vs Kepadatan")

continents = ["Semua"] + sorted(df["Continent"].unique().tolist())
selected_continent = st.sidebar.selectbox("Benua", continents)

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
col3.metric("Rata-rata Growth Rate", f"{avg_growth_rate:.4f}")
col4.metric("Rata-rata Kepadatan 2022", f"{avg_density:.2f}/km²")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Negara dengan Populasi Terbesar (2022)")
    top_countries = filtered_df.nlargest(10, "2022 Population")[["Rank", "Country/Territory", "2022 Population", "Continent", "Density (per km²)"]]
    top_countries["2022 Population"] = top_countries["2022 Population"].apply(lambda x: f"{x:,.0f}")
    top_countries["Density (per km²)"] = top_countries["Density (per km²)"].apply(lambda x: f"{x:.2f}")
    top_countries = top_countries.reset_index(drop=True)
    top_countries.index = top_countries.index + 1
    st.dataframe(top_countries, use_container_width=True, height=400)

with col_right:
    st.subheader("Distribusi Populasi Dunia per Benua (2022)")
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

st.subheader("Tren Populasi dari Tahun 1970-2022")

available_countries = filtered_df["Country/Territory"].tolist()
selected_countries = st.multiselect(
    "Pilih Negara untuk Membandingkan Tren Populasi",
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

st.subheader("Peta Distribusi Populasi Dunia (2022)")

fig_map = px.choropleth(
    df,
    locations="CCA3",
    color="2022 Population",
    hover_name="Country/Territory",
    hover_data={"2022 Population": ":,.0f", "CCA3": False},
    color_continuous_scale="Blues",
    labels={"2022 Population": "Populasi 2022"}
)
fig_map.update_layout(height=600, geo=dict(showframe=False, projection_type="natural earth"))
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Hubungan Growth Rate dan Kepadatan Populasi per Negara (2022)")

# Filter outliers untuk visualisasi yang lebih baik
scatter_df = filtered_df[filtered_df["Density (per km²)"] < 2000].copy()

fig_scatter = px.scatter(
    scatter_df,
    x="Density (per km²)",
    y="Growth Rate",
    size="2022 Population",
    color="Continent",
    hover_name="Country/Territory",
    hover_data={"2022 Population": ":,.0f", "Density (per km²)": ":.2f", "Growth Rate": ":.4f"},
    size_max=50,
    labels={"Density (per km²)": "Kepadatan (per km²)", "Growth Rate": "Tingkat Pertumbuhan"}
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download Data (CSV)", csv, "world_population_data.csv", "text/csv")