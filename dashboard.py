#import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px

#load and clean data
@st.cache_data
def load_data():
    dataset = pd.read_csv('us-population-2010-2019.csv')
    dataset.columns = dataset.columns.str.strip() 
    dataset['states'] = dataset['states'].str.strip() #clean state names
    for year in range(2010, 2020):
        dataset[str(year)] = dataset[str(year)].replace({",": ""}, regex=True).astype(int)
    return dataset

dataset = load_data()

#map full state names to abbreviations
states_abbreviations = {
    'Alabama'        : 'AL',
    'Alaska'         : 'AK',
    'Arizona'        : 'AZ',
    'Arkansas'       : 'AR',
    'California'     : 'CA',
    'Colorado'       : 'CO',
    'Connecticut'    : 'CT',
    'Delaware'       : 'DE',
    'Florida'        : 'FL',
    'Georgia'        : 'GA',
    'Hawaii'         : 'HI',
    'Idaho'          : 'ID',
    'Illinois'       : 'IL',
    'Indiana'        : 'IN',
    'Iowa'           : 'IA',
    'Kansas'         : 'KS',
    'Kentucky'       : 'KY',
    'Louisiana'      : 'LA',
    'Maine'          : 'ME',
    'Maryland'       : 'MD',
    'Massachusetts'  : 'MA',
    'Michigan'       : 'MI',
    'Minnesota'      : 'MN',
    'Mississippi'    : 'MS',
    'Missouri'       : 'MO',
    'Montana'        : 'MT',
    'Nebraska'       : 'NE',
    'Nevada'         : 'NV',
    'New Hampshire'  : 'NH',
    'New Jersey'     : 'NJ',
    'New Mexico'     : 'NM',
    'New York'       : 'NY',
    'North Carolina' : 'NC',
    'North Dakota'   : 'ND',
    'Ohio'           : 'OH',
    'Oklahoma'       : 'OK',
    'Oregon'         : 'OR',
    'Pennsylvania'   : 'PA',
    'Rhode Island'   : 'RI',
    'South Carolina' : 'SC',
    'South Dakota'   : 'SD',
    'Tennessee'      : 'TN',
    'Texas'          : 'TX',
    'Utah'           : 'UT',
    'Vermont'        : 'VT',
    'Virginia'       : 'VA',
    'Washington'     : 'WA',
    'West Virginia'  : 'WV',
    'Wisconsin'      : 'WI',
    'Wyoming'        : 'WY'
}


#filter only valid states
dataset = dataset[dataset['states'].isin(states_abbreviations.keys())].copy()
dataset['states_abbreviations'] = dataset['states'].map(states_abbreviations)

#sidebar filters
st.sidebar.header("Filter Options")
selected_states = st.sidebar.multiselect(
    "Select states to visualize:",
    options=dataset["states"].tolist(),
    default=['California', 'Texas', 'Florida']
)

#filter dataset based on selected states
year_range = st.sidebar.slider("Select year range:", 2010, 2019, (2010, 2019))
normalize = st.sidebar.checkbox("Normalize population (2010 = 100%)")

#tabbed layout
tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Top States", "Growth", "Map"])

#Population Trends Tab
with tab1:
    st.header("📉 Population Trends in United States")
    if selected_states:
        dataset_filtered = dataset[dataset['states'].isin(selected_states)].set_index('states')
        dataset_plot = dataset_filtered.loc[:, str(year_range[0]):str(year_range[1])].T
        dataset_plot.index = dataset_plot.index.astype(int)
        if normalize:
            dataset_plot = dataset_plot/dataset.iloc[0]*100
            st.caption("Population normalized to 2010 = 100%")

        st.line_chart(dataset_plot)

#visualize top ten states by population
with tab2:
    st.header("Top 10 States by Population")
    latest_year = str(year_range[1])
    top_states = dataset.nlargest(10, latest_year)[['states', latest_year]]
    fig = px.bar(top_states, x='states', y=latest_year, labels={latest_year: 'Population', 'states': 'State'}, title=f'Top 10 States by Population in {latest_year}')
    st.plotly_chart(fig)

#population growth tab
with tab3:
    st.header("📈 Population Growth Analysis")
    dataset['Growth (%)'] = ((dataset[str(year_range[1])] - dataset[str(year_range[0])]) / dataset[str(year_range[0])]) * 100
    growth_sorted = dataset[['states', 'Growth (%)']].sort_values(by='Growth (%)', ascending=False)
    fig_growth = px.bar(growth_sorted, x='states', y='Growth (%)', labels={'Growth (%)': 'Population Growth (%)', 'states': 'State'}, title=f'Population Growth from {year_range[0]} to {year_range[1]}')
    st.plotly_chart(fig_growth)

#population map tab
with tab4:
    st.header("🗺️ Population Distribution of United State (2019)")
    latest_year = str(year_range[1])
    fig_map = px.choropleth(
        dataset,
        locations='states_abbreviations',
        locationmode="USA-states",
        color= latest_year,
         hover_name='states',
        hover_data={
            latest_year: True,
            'Growth (%)': True
        },
        color_continuous_scale="Turbo",
        scope="usa",
        labels={latest_year: 'Population'},
        title=f'Population Distribution in {latest_year}'
    )
    st.plotly_chart(fig_map)

    #download dataset
st.markdown("---")
st.download_button("📥 Download Data Set", dataset.to_csv(index=False), "us_population_cleaned.csv")
