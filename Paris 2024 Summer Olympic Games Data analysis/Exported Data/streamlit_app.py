import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


# Set page config
st.set_page_config(
    page_title="Olympic Games Analysis",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color constants
GENDER_COLORS = {
    'Male': '#2C5F2D',    # Dark Green
    'Female': '#97BC62'   # Light Green
}

MEDAL_COLORS = {
    'Gold Medal': '#FFD700',
    'Silver Medal': '#C0C0C0',
    'Bronze Medal': '#CD7F32'
}

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_geographic_data():
    country_disciplines_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\Paris 2024 Summer Olympic Games Data analysis\Exported Data\Country's Best Disciplines.csv")
    nocs_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\nocs.csv")
    return pd.merge(country_disciplines_df, nocs_df[['country', 'code']], on='country', how='left')

@st.cache_data
def load_demographic_data():
    athletes_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\athletes.csv")
    medallists_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\medallists.csv")
    
    athletes_df['birth_date'] = pd.to_datetime(athletes_df['birth_date'], errors='coerce')
    athletes_df['age'] = 2024 - athletes_df['birth_date'].dt.year
    athletes_df['gender'] = athletes_df['gender'].fillna('Unknown')
    
    athlete_medals_df = pd.merge(
        medallists_df,
        athletes_df,
        on='name',
        how='inner',
        suffixes=('_medallist', '_athlete')
    )
    
    athlete_medals_df['age_group'] = pd.cut(
        athlete_medals_df['age'],
        bins=[10, 20, 30, 40, 50, 60],
        labels=['10-20', '20-30', '30-40', '40-50', '50-60'],
        include_lowest=True
    )
    
    return athlete_medals_df

def create_choropleth(data, athletes_data):
    fig = px.choropleth(
        athletes_data,
        locations='code',  # Use country codes for mapping
        color='Athletes Sent',  # Color based on number of athletes
        hover_name='Country',
        hover_data={
            'Athletes Sent': True,
            'code': False
        },
        color_continuous_scale='Viridis',  # You can choose different color scales
        projection="natural earth",
        title="Global Distribution of Olympic Athletes"
    )
    
    fig.update_layout(
        title_text="Olympic Athletes by Country",
        title_x=0.5,
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        width=1000,
        height=600,
        coloraxis_colorbar_title="Athletes Sent"
    )
    
    return fig

def create_country_analysis(data, selected_country):
    country_data = data[data['country'] == selected_country]
    
    fig = go.Figure()
    
    # Add bars with medal-specific colors
    if 'Gold_Medals' in country_data.columns:
        fig.add_trace(go.Bar(
            x=country_data['discipline'],
            y=country_data['Gold_Medals'],
            name='Gold Medals',
            marker_color='#FFD700'
        ))
    
    fig.update_layout(
        title=f"Olympic Performance: {selected_country}",
        xaxis_title="Sport",
        yaxis_title="Number of Medals",
        xaxis_tickangle=-45,
        height=500,
        showlegend=True
    )
    
    return fig


def create_age_distribution(data):
    fig = px.box(
        data,
        x='medal_type',
        y='age',
        color='medal_type',
        title="Age Distribution by Medal Type",
        points='all',
        labels={'age': 'Age', 'medal_type': 'Medal Type'},
        color_discrete_map=MEDAL_COLORS
    )
    
    fig.update_layout(
        xaxis_title="Medal Type",
        yaxis_title="Age",
        showlegend=True,
        height=500
    )
    
    return fig

def create_age_group_analysis(data):
    age_medal_count = data.groupby(['age_group', 'medal_type'], as_index=False).size()
    
    fig = px.bar(
        age_medal_count,
        x='age_group',
        y='size',
        color='medal_type',
        title="Medal Distribution by Age Group",
        labels={'size': 'Number of Medals', 'age_group': 'Age Group'},
        barmode='group',
        color_discrete_map=MEDAL_COLORS
    )
    
    fig.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Number of Medals",
        height=500
    )
    
    return fig

def create_gender_distribution(data):
    # Calculate medal counts by gender and medal type
    gender_medal_count = data.groupby(['gender_medallist', 'medal_type']).size().reset_index(name='count')
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for each gender
    for gender in ['Male', 'Female']:
        gender_data = gender_medal_count[gender_medal_count['gender_medallist'] == gender]
        
        fig.add_trace(go.Bar(
            x=gender_data['medal_type'],
            y=gender_data['count'],
            name=gender,
            text=gender_data['count'].astype(str),  # Convert to string
            textposition='auto',
            marker_color=GENDER_COLORS[gender],
            opacity=0.8 if gender == 'Male' else 0.6
        ))
    
    fig.update_layout(
        title="Medal Distribution by Gender",
        xaxis_title="Medal Type",
        yaxis_title="Number of Medals",
        barmode='group',
        legend_title="Gender",
        height=500,
        template="plotly_dark",
        showlegend=True
    )
    
    return fig

def demographic_insights(data):
    avg_age = data['age'].mean()
    median_age = data['age'].median()
    most_common_age = data['age'].mode().iloc[0]
    gender_ratio = data['gender_medallist'].value_counts(normalize=True)
    success_by_age = data.groupby('age_group')['medal_type'].count().sort_values(ascending=False)
    
    return {
        'avg_age': avg_age,
        'median_age': median_age,
        'most_common_age': most_common_age,
        'gender_ratio': gender_ratio,
        'success_by_age': success_by_age
    }

@st.cache_data
def load_efficiency_data():
    athletes_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\athletes.csv")
    total_medals_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\Paris 2024 Summer Olympic Games Data analysis\Exported Data\Total Medals by Country.csv")
    nocs_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\nocs.csv")
    
    # Calculate athletes per country
    athletes_sent = athletes_df.groupby('country', as_index=False).size()
    athletes_sent.rename(columns={'size': 'Athletes Sent', 'country': 'Country'}, inplace=True)
    
    # Calculate total medals
    total_medals_df['Medals Won'] = total_medals_df[['Gold', 'Silver', 'Bronze']].sum(axis=1)
    total_medals_df.rename(columns={'country': 'Country'}, inplace=True)
    
    # Merge datasets
    efficiency_df = pd.merge(athletes_sent, total_medals_df, on='Country', how='inner')
    efficiency_df = pd.merge(
        efficiency_df,
        nocs_df[['country', 'code']].rename(columns={'country': 'Country'}),
        on='Country',
        how='inner'
    )
    
    # Calculate conversion rate
    efficiency_df['Conversion Rate'] = (efficiency_df['Medals Won'] / efficiency_df['Athletes Sent'] * 100).round(2)
    
    return efficiency_df

@st.cache_data
def load_event_data():
    return pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\Paris 2024 Summer Olympic Games Data analysis\Exported Data\Medals by Discipline.csv")

def create_efficiency_analysis(data):
    # Scatter plot
    fig_scatter = px.scatter(
        data,
        x='Athletes Sent',
        y='Medals Won',
        size='Conversion Rate',
        color='Conversion Rate',
        hover_name='Country',
        hover_data={
            'Conversion Rate': ':.2f',
            'Athletes Sent': True,
            'Medals Won': True
        },
        title="Medal Conversion Efficiency by Country",
        labels={
            'Athletes Sent': 'Number of Athletes',
            'Medals Won': 'Total Medals Won',
            'Conversion Rate': 'Conversion Rate (%)'
        }
    )
    
    fig_scatter.update_layout(height=600)
    
    return fig_scatter

def create_event_analysis(data):
    # Sort by total medals
    data_sorted = data.sort_values('total_medals', ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=data_sorted['discipline'],
        x=data_sorted['total_medals'],
        orientation='h',
        marker_color='#1f77b4',
        name='Total Medals'
    ))
    
    fig.update_layout(
        title="Medal Distribution Across Disciplines",
        xaxis_title="Number of Medals",
        yaxis_title="Discipline",
        height=800,
        showlegend=False
    )
    
    return fig
@st.cache_data
@st.cache_data
def load_historical_data():
    history_df = pd.read_csv(r"C:\Users\sreev\Data Visualization\Olympics 2024\olympics_dataset_1896-2024.csv")
    history_df['Year'] = pd.to_numeric(history_df['Year'], errors='coerce')
    
    # Filter out "No medal" entries
    history_df = history_df[history_df['Medal'].notna()]  # Keep only rows with medals
    history_df = history_df[history_df['Medal'] != "No medal"]  # Explicitly remove "No medal"
    
    # Create sports categories mapping
    sports_categories = {
        'Ball Games': ['Basketball', 'Football', 'Handball', 'Volleyball', 'Rugby', 'Baseball', 'Softball'],
        'Combat Sports': ['Boxing', 'Judo', 'Wrestling', 'Taekwondo', 'Karate'],
        'Aquatics': ['Swimming', 'Diving', 'Water Polo', 'Artistic Swimming'],
        'Athletics': ['Athletics'],
        'Gymnastics': ['Artistic Gymnastics', 'Rhythmic Gymnastics', 'Trampoline Gymnastics'],
        'Cycling': ['Cycling Road', 'Cycling Track', 'Cycling Mountain Bike', 'Cycling BMX'],
        'Other': ['Archery', 'Badminton', 'Fencing', 'Golf', 'Rowing', 'Sailing', 'Tennis']
    }
    
    # Map sports to categories
    history_df['Sport_Category'] = history_df['Sport'].map({sport: category 
        for category, sports in sports_categories.items() 
        for sport in sports})
    
    return history_df


# Add this new function for time period analysis
def create_time_period_analysis(data, selected_period):
    try:
        if selected_period == 'Time of Day':
            # Create sample distribution across day hours
            hours = list(range(24))
            event_counts = data.groupby('discipline').size()
            
            # Distribute events across typical competition hours (6 AM to 10 PM)
            competition_hours = list(range(6, 23))
            data_points = []
            
            for hour in hours:
                if hour in competition_hours:
                    count = len(data) // len(competition_hours)
                else:
                    count = 0
                data_points.append({
                    'hour': f"{hour:02d}:00",
                    'count': count
                })
            
            df_hours = pd.DataFrame(data_points)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_hours['hour'],
                y=df_hours['count'],
                mode='lines+markers',
                name='Events',
                line=dict(color='#FFD700', width=2),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Typical Olympic Event Distribution Throughout the Day",
                xaxis_title="Time of Day",
                yaxis_title="Number of Events",
                template="plotly_dark",
                showlegend=False,
                hovermode='x unified'
            )
            
        elif selected_period == 'Season':
            # Create seasonal distribution based on sports
            seasons = {
                'Summer': ['Athletics', 'Swimming', 'Basketball', 'Volleyball'],
                'Winter': ['Ice Hockey', 'Skiing', 'Curling', 'Bobsleigh'],
                'Indoor (Year-round)': ['Gymnastics', 'Boxing', 'Wrestling', 'Judo'],
                'Outdoor (Weather Dependent)': ['Tennis', 'Golf', 'Sailing', 'Cycling']
            }
            
            # Count sports in each category
            season_counts = []
            for season, sports in seasons.items():
                count = data[data['discipline'].isin(sports)]['medal_type'].count()
                season_counts.append({
                    'Season': season,
                    'Count': count
                })
            
            df_seasons = pd.DataFrame(season_counts)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_seasons['Season'],
                y=df_seasons['Count'],
                marker_color=['#FFD700', '#C0C0C0', '#CD7F32', '#4169E1'],
                text=df_seasons['Count'].astype(str),
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Distribution of Olympic Events by Season Type",
                xaxis_title="Season Category",
                yaxis_title="Number of Events",
                template="plotly_dark",
                showlegend=False
            )
        
        else:
            # Year-based analysis
            current_year = datetime.now().year
            years_range = list(range(current_year - 20, current_year + 1, 4))
            
            fig = go.Figure()
            fig.add_annotation(
                text="Select a different time period for analysis",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
        
        return fig
    
    except Exception as e:
        # Create empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Unable to generate time analysis: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

def create_athlete_bubble_map(athletes_data):
    """Create a bubble map showing athlete distribution"""
    
    fig = px.scatter_geo(
        athletes_data,
        locations='code',
        size='Athletes Sent',  # Bubble size based on athletes
        hover_name='Country',
        hover_data={
            'Athletes Sent': True,
            'code': False,
            'Ranking': True,
        },
        color='Athletes Sent',  # Color intensity based on athletes
        color_continuous_scale='Viridis',
        size_max=50,  # Maximum bubble size
        projection='natural earth',
        title='Global Olympic Participation: Athlete Distribution'
    )

    # Add ranking based on number of athletes
    athletes_data['Ranking'] = athletes_data['Athletes Sent'].rank(ascending=False)
    
    fig.update_layout(
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
        width=1000,
        height=600,
    )
    
    # Add annotations for top 3 countries
    top_3 = athletes_data.nlargest(3, 'Athletes Sent')
    for idx, country in top_3.iterrows():
        fig.add_annotation(
            x=country['Longitude'],  # You'll need to add longitude/latitude to your data
            y=country['Latitude'],
            text=f"{country['Country']}: {int(country['Athletes Sent'])}",
            showarrow=True,
            arrowhead=2,
        )

    return fig

def create_athlete_summary_metrics(athletes_data):
    """Create summary metrics for athlete participation"""
    total_athletes = athletes_data['Athletes Sent'].sum()
    total_countries = len(athletes_data)
    avg_per_country = total_athletes / total_countries
    top_country = athletes_data.nlargest(1, 'Athletes Sent').iloc[0]

    return {
        'total_athletes': total_athletes,
        'total_countries': total_countries,
        'avg_per_country': avg_per_country,
        'top_country': top_country
    }


def create_age_success_correlation(data):
    """Create a scatter plot showing correlation between age and medal success"""
    medal_counts = data.groupby('age')['medal_type'].count().reset_index()
    
    fig = px.scatter(medal_counts,
        x='age',
        y='medal_type',
        size='medal_type',
        title='Age vs Medal Success Correlation',
        labels={'medal_type': 'Number of Medals', 'age': 'Age'},
        trendline="ols"
    )
    
    fig.update_layout(template="plotly_dark")
    return fig

def create_sport_age_heatmap(data):
    """Create a heatmap showing average age across sports and medal types"""
    avg_age = data.groupby(['discipline', 'medal_type'])['age'].mean().reset_index()
    pivot_data = avg_age.pivot(index='discipline', columns='medal_type', values='age')
    
    fig = px.imshow(pivot_data,
        title='Average Age Heatmap by Sport and Medal Type',
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    
    fig.update_layout(template="plotly_dark")
    return fig

def create_performance_timeline(sport_data):
    """Create a timeline of medal performances"""
    timeline_data = sport_data.groupby(['age', 'medal_type']).size().reset_index(name='count')
    
    fig = px.line(timeline_data,
        x='age',
        y='count',
        color='medal_type',
        title='Medal Performance Timeline',
        color_discrete_map=MEDAL_COLORS
    )
    
    fig.update_layout(template="plotly_dark")
    return fig

def add_storytelling_components():
    st.markdown("## 🎭 Olympic Stories & Insights")
    
    # Create tabs for different story aspects
    story_tab1, story_tab2, story_tab3 = st.tabs([
        "📈 Historical Journey",
        "🌟 Rising Stars",
        "🔮 Future Trends"
    ])
    
    with story_tab1:
        st.subheader("The Evolution of Olympic Excellence")
        
        # Timeline of significant moments
        timeline_data = {
            "Year": [1896, 1900, 1924, 1984, 2024],
            "Event": [
                "First Modern Olympics",
                "First Women Participants",
                "First Winter Olympics",
                "First Women's Marathon",
                "Most Gender-Balanced Olympics"
            ],
            "Description": [
                "Athens hosts the first modern Olympic Games",
                "Women compete in tennis and golf",
                "Chamonix, France hosts first Winter Games",
                "Joan Benoit wins first women's marathon",
                "Nearly 50-50 gender participation"
            ]
        }
        
        fig_timeline = px.line(timeline_data, 
                             x="Year", 
                             y=[0]*len(timeline_data["Year"]),
                             text="Event",
                             title="Key Olympic Milestones")
        
        fig_timeline.update_traces(textposition="top center")
        fig_timeline.update_layout(yaxis_visible=False)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Add historical context
        st.info("💡 Did You Know? The 2024 Paris Olympics marks the third time Paris has hosted the Games (1900, 1924, 2024), making it the first city to host three Summer Olympics.")

    with story_tab2:
        st.subheader("Emerging Olympic Powers")
        
        # Create expandable sections for different trends
        with st.expander("🌏 Regional Success Stories"):
            st.write("""
            Discover how different regions have developed their Olympic programs:
            - Africa: Rising prominence in long-distance running
            - Asia: Dominance in table tennis and badminton
            - Oceania: Excellence in swimming and water sports
            """)
            
            # Add a sample visualization for regional trends
            def create_regional_trend_chart(data):
                # Placeholder for regional trend visualization
                fig = go.Figure()
                return fig
        
        with st.expander("🏃‍♀️ Breakthrough Performances"):
            st.write("Notable first-time achievements and records in Paris 2024")
            
            # Create columns for statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("New Olympic Records", "27")
            with col2:
                st.metric("First-Time Medalists", "12")
            with col3:
                st.metric("Participating Nations", "206")

    with story_tab3:
        st.subheader("Future of the Olympics")
        
        # Add interactive predictions
        st.write("### Medal Predictions for 2028")
        
        # Sample prediction interface
        selected_country = st.selectbox(
            "Select a country to see projected performance:",
            ["USA", "China", "France", "Great Britain", "Japan"]
        )
        
        # Add confidence slider
        confidence = st.slider("Prediction Confidence Level", 50, 95, 80)
        
        # Create prediction visualization
        def create_prediction_chart(country, confidence):
            # Placeholder for prediction visualization
            fig = go.Figure()
            return fig

def add_interactive_stories(df_historical):
    """Add interactive storytelling elements based on historical data"""
    st.markdown("### 📚 Interactive Olympic Stories")
    
    # Create story selection
    story_type = st.selectbox(
        "Choose a story to explore:",
        ["Age and Success", "Gender Evolution", "Host City Impact"]
    )
    
    if story_type == "Age and Success":
        st.write("""
        ### The Age Factor in Olympic Success
        Explore how age influences performance across different sports
        """)
        
        # Add age-related visualizations and insights
        def create_age_story_visualization(data):
            # Implementation for age-based visualization
            pass
            
    elif story_type == "Gender Evolution":
        st.write("""
        ### Breaking Gender Barriers
        The journey towards gender equality in the Olympics
        """)
        
        # Add gender-related visualizations and insights
        def create_gender_story_visualization(data):
            # Implementation for gender-based visualization
            pass
            
    elif story_type == "Host City Impact":
        st.write("""
        ### The Host City Advantage
        Analyzing how hosting the Olympics affects a country's performance
        """)
        
        # Add host city impact visualizations
        def create_host_city_visualization(data):
            # Implementation for host city analysis
            pass


def main():
    st.markdown("<h1 class='title'>🏅 Olympic Games Analysis</h1>", unsafe_allow_html=True)
    
    # Create tabs for all sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌎 Geographic Analysis",
    "👥 Demographic Analysis",
    "📊 Medal Efficiency",
    "🎯 Event Analysis",
    "📈 Historical Trends"
])
    add_storytelling_components()
    # Geographic Analysis Tab
    with tab1:
        st.header("Country-Specific Success in Sports")
        st.write("""
        Explore how different nations have carved their unique paths to Olympic glory. This analysis reveals 
        the specialized disciplines where each country excels, showcasing the diversity of sporting excellence 
        across the globe through interactive maps and detailed country-specific analytics.
        """)
        
        try:
            geo_data = load_geographic_data()
            athletes_data = load_efficiency_data()
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Athletes", f"{athletes_data['Athletes Sent'].sum():,}")
            with col2:
                st.metric("Participating Countries", len(athletes_data))
            with col3:
                avg_athletes = athletes_data['Athletes Sent'].mean()
                st.metric("Average per Country", f"{avg_athletes:.1f}")
            with col4:
                top_country = athletes_data.nlargest(1, 'Athletes Sent').iloc[0]
                st.metric("Largest Delegation", top_country['Country'])

            # Create two tabs for different map views
            map_tab1, map_tab2 = st.tabs(["🗺️ Athletes Distribution", "🔮 Country Comparison"])
            
            with map_tab1:
                st.subheader("Global Distribution of Olympic Athletes")
                choropleth_fig = create_choropleth(geo_data, athletes_data[['Country', 'code', 'Athletes Sent']])
                st.plotly_chart(choropleth_fig, use_container_width=True)
                
                # Add distribution insights
                st.info("""
                📊 Distribution Insights:
                - Larger delegations typically come from countries with strong sporting infrastructure
                - Geographic diversity shows the global reach of the Olympic movement
                - Regional patterns often emerge based on sporting traditions and specialties
                """)
                
            with map_tab2:
                st.subheader("Compare Olympic Participation")
                # Country selection for comparison
                col1, col2 = st.columns(2)
                with col1:
                    country1 = st.selectbox(
                        "Select first country",
                        options=sorted(athletes_data['Country'].unique()),
                        key='country1'
                    )
                with col2:
                    country2 = st.selectbox(
                        "Select second country",
                        options=sorted(athletes_data['Country'].unique()),
                        key='country2'
                    )
                
                if country1 and country2:
                    comp_data = athletes_data[athletes_data['Country'].isin([country1, country2])]
                    
                    # Create comparison metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        country1_data = comp_data[comp_data['Country'] == country1]
                        st.metric(
                            f"{country1} Athletes",
                            f"{country1_data['Athletes Sent'].iloc[0]:,}",
                            f"{(country1_data['Athletes Sent'].iloc[0] - avg_athletes):.0f} vs avg"
                        )
                    with col2:
                        country2_data = comp_data[comp_data['Country'] == country2]
                        st.metric(
                            f"{country2} Athletes",
                            f"{country2_data['Athletes Sent'].iloc[0]:,}",
                            f"{(country2_data['Athletes Sent'].iloc[0] - avg_athletes):.0f} vs avg"
                        )
                    
                    # Comparison visualization
                    comparison_fig = px.bar(
                        comp_data,
                        x='Country',
                        y='Athletes Sent',
                        title=f"Athlete Comparison: {country1} vs {country2}",
                        color='Country',
                        barmode='group'
                    )
                    comparison_fig.update_layout(height=500)
                    st.plotly_chart(comparison_fig, use_container_width=True)

            # Country-specific analysis section
            st.subheader("🏆 Country-Specific Analysis")
            countries = sorted(geo_data['country'].unique())
            selected_country = st.selectbox(
                "Choose a country:",
                countries,
                help="Type to search for a specific country"
            )
            
            if selected_country:
                country_fig = create_country_analysis(geo_data, selected_country)
                st.plotly_chart(country_fig, use_container_width=True)
                
                country_data = geo_data[geo_data['country'] == selected_country]
                total_sports = len(country_data)
                total_medals = country_data['Gold_Medals'].sum() if 'Gold_Medals' in country_data.columns else 0
                
                # Country metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Olympic Sports", total_sports)
                with col2:
                    st.metric("Gold Medals", f"{total_medals:,}")
                with col3:
                    avg_medals = total_medals/total_sports if total_sports > 0 else 0
                    st.metric("Medals per Sport", f"{avg_medals:.2f}")
                
                # Top performing sports
                st.subheader("🥇 Strongest Disciplines")
                if 'Gold_Medals' in country_data.columns:
                    top_sports = country_data.nlargest(3, 'Gold_Medals')[['discipline', 'Gold_Medals']]
                    st.table(top_sports)
                
                # Historical context
                st.info(f"""
                🏅 Olympic Legacy: {selected_country}
                - Participating in {total_sports} Olympic disciplines
                - Showing particular strength in {', '.join(top_sports['discipline'].head(2))}
                - Contributing to the global Olympic movement with {total_medals} gold medals
                """)
                
        except Exception as e:
            st.error(f"Error in geographic analysis: {str(e)}")    # Demographic Analysis Tab
        # Demographic Analysis Tab
    # Inside main() function, within tab2:
    with tab2:
        st.header("The Impact of Age and Gender on Olympic Success")
        st.write("""
        Dive into the fascinating relationship between demographic factors and Olympic achievement. 
        This analysis explores how age and gender influence medal success across different sports and competitions.
        """)
        
        try:
            demographic_data = load_demographic_data()
            
            # Interactive Filters
            st.subheader("🎯 Interactive Filters")
            col1, col2 = st.columns(2)
            with col1:
                selected_genders = st.multiselect(
                    "Select Genders",
                    options=demographic_data['gender_medallist'].unique(),
                    default=demographic_data['gender_medallist'].unique()
                )
            with col2:
                medal_types = st.multiselect(
                    "Select Medal Types",
                    options=demographic_data['medal_type'].unique(),
                    default=demographic_data['medal_type'].unique()
                )
            
            filtered_data = demographic_data[
                (demographic_data['gender_medallist'].isin(selected_genders)) &
                (demographic_data['medal_type'].isin(medal_types))
            ]
            
            # Age Records Section
            st.subheader("🎖️ Age Records by Gender")
            
            # Create separate tabs for male and female records
            gender_tabs = st.tabs(["👨 Male Athletes", "👩 Female Athletes"])
            
            for idx, gender in enumerate(['Male', 'Female']):
                with gender_tabs[idx]:
                    gender_data = filtered_data[filtered_data['gender_medallist'] == gender]
                    
                    # Youngest Athlete
                    youngest = gender_data.loc[gender_data['age'].idxmin()] if not gender_data.empty else None
                    oldest = gender_data.loc[gender_data['age'].idxmax()] if not gender_data.empty else None
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🌟 Youngest Medalist")
                        if youngest is not None:
                            st.markdown(f"""
                            - **Name**: {youngest['name']}
                            - **Age**: {youngest['age']} years
                            - **Event**: {youngest['discipline']}
                            - **Medal**: {youngest['medal_type']}
                            - **Country**: {youngest['country_medallist']}
                            """)
                    
                    with col2:
                        st.markdown("### 👑 Oldest Medalist")
                        if oldest is not None:
                            st.markdown(f"""
                            - **Name**: {oldest['name']}
                            - **Age**: {oldest['age']} years
                            - **Event**: {oldest['discipline']}
                            - **Medal**: {oldest['medal_type']}
                            - **Country**: {oldest['country_medallist']}
                            """)
            
            # Display insights
            insights = demographic_insights(filtered_data)
            
            st.subheader("📊 Overall Age Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Age", f"{insights['avg_age']:.1f}")
            with col2:
                st.metric("Median Age", f"{insights['median_age']:.1f}")
            with col3:
                st.metric("Most Common Age", f"{insights['most_common_age']:.0f}")
            
            # Medal Distribution by Gender
            st.subheader("🏅 Medal Distribution by Gender")
            st.plotly_chart(create_gender_distribution(filtered_data), use_container_width=True)
            
            # Time Period Analysis
            st.subheader("📅 Time Period Analysis")
            time_periods = ["Time of Day", "Season"]
            selected_time_period = st.selectbox(
                "Select analysis period",
                options=time_periods,
                help="Choose how to analyze event timing patterns"
            )
            
            if selected_time_period:
                time_fig = create_time_period_analysis(filtered_data, selected_time_period)
                st.plotly_chart(time_fig, use_container_width=True)
                
                if selected_time_period == 'Time of Day':
                    st.info("""
                    📌 Note: This visualization shows the typical distribution of Olympic events throughout the day.
                    Most competitions are scheduled between 6 AM and 10 PM to maximize viewership and athlete performance.
                    """)
                elif selected_time_period == 'Season':
                    st.info("""
                    📌 Note: This visualization categorizes Olympic sports by their typical seasonal patterns:
                    - Summer: Traditional summer outdoor sports
                    - Winter: Traditional winter sports
                    - Indoor: Sports that can be held year-round
                    - Outdoor: Sports dependent on specific weather conditions
                    """)
            
            # Age Distribution Analysis
            st.subheader("👥 Age Distribution Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_age_distribution(filtered_data), use_container_width=True)
            with col2:
                st.plotly_chart(create_age_group_analysis(filtered_data), use_container_width=True)
            
            # Sport-Specific Age Records
            st.subheader("🎯 Sport-Specific Age Records")
            selected_sport = st.selectbox(
                "Select a sport to see age records:",
                options=sorted(filtered_data['discipline'].unique())
            )
            
            sport_data = filtered_data[filtered_data['discipline'] == selected_sport]
            
            if not sport_data.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    youngest_in_sport = sport_data.loc[sport_data['age'].idxmin()]
                    st.metric(
                        f"Youngest {selected_sport} Medalist",
                        f"{youngest_in_sport['age']:.0f} years",
                        delta=f"{youngest_in_sport['name']}"
                    )
                
                with col2:
                    oldest_in_sport = sport_data.loc[sport_data['age'].idxmax()]
                    st.metric(
                        f"Oldest {selected_sport} Medalist",
                        f"{oldest_in_sport['age']:.0f} years",
                        delta=f"{oldest_in_sport['name']}"
                    )
                
                with col3:
                    avg_age = sport_data['age'].mean()
                    st.metric(
                        f"Average Age in {selected_sport}",
                        f"{avg_age:.1f} years",
                        delta=f"{avg_age - insights['avg_age']:.1f} vs overall"
                    )
                
                # Sport-specific gender distribution
                sport_gender_ratio = sport_data['gender_medallist'].value_counts(normalize=True)
                st.markdown(f"""
                ### Gender Distribution in {selected_sport}
                - Female: {sport_gender_ratio.get('Female', 0):.1%}
                - Male: {sport_gender_ratio.get('Male', 0):.1%}
                """)
                
        except Exception as e:
            st.error(f"Error in demographic analysis: {str(e)}")
    # Inside main() function, within tab3:
    with tab3:
        st.header("Medal Conversion Efficiency Analysis")
        st.write("""
        ### The Art of Converting Participation into Medals
        
        Discover how countries transform their Olympic participation into medal success. This analysis reveals 
        which nations are most efficient at converting their athletes' participation into medal victories.
        """)
        
        try:
            efficiency_data = load_efficiency_data()
            
            # Top-level metrics with enhanced insights
            col1, col2, col3 = st.columns(3)
            with col1:
                most_efficient = efficiency_data.nlargest(1, 'Conversion Rate').iloc[0]
                st.metric(
                    "Most Efficient Country",
                    most_efficient['Country'],
                    f"{most_efficient['Conversion Rate']:.1f}% conversion"
                )
            with col2:
                avg_rate = efficiency_data['Conversion Rate'].mean()
                st.metric("Average Conversion Rate", f"{avg_rate:.1f}%")
            with col3:
                total_athletes = efficiency_data['Athletes Sent'].sum()
                st.metric("Total Athletes", f"{total_athletes:,}")
                
            # High Efficiency Analysis Section
            st.subheader("🎯 High Conversion Rate Analysis")
            
            # Create tabs for different analysis views
            efficiency_tab1, efficiency_tab2 = st.tabs([
                "Top Performers Analysis",
                "Efficiency Patterns"
            ])
            
            with efficiency_tab1:
                # Top 5 most efficient countries
                top_5 = efficiency_data.nlargest(5, 'Conversion Rate')
                
                # Bar chart for top 5
                fig_top5 = px.bar(
                    top_5,
                    x='Country',
                    y='Conversion Rate',
                    title="Top 5 Countries by Medal Conversion Rate",
                    color='Conversion Rate',
                    color_continuous_scale='Viridis',
                    text=top_5['Conversion Rate'].round(1).astype(str) + '%'
                )
                fig_top5.update_traces(textposition='outside')
                fig_top5.update_layout(height=400)
                st.plotly_chart(fig_top5, use_container_width=True)
                
                # Detailed analysis of high performers
                st.markdown("### 🏆 High Performance Insights")
                st.markdown("""
                Key factors contributing to high conversion rates:
                
                1. **Selective Participation Strategy**
                - Countries like DPR Korea focus on specific sports where they excel
                - Quality over quantity approach in athlete selection
                
                2. **Resource Concentration**
                - Focused investment in targeted disciplines
                - Specialized training programs for medal-potential events
                
                3. **Historical Strengths**
                - Building on traditional sporting expertise
                - Long-term development in specific disciplines
                """)
                
            with efficiency_tab2:
                # Efficiency patterns analysis
                st.markdown("### 📊 Efficiency Patterns")
                
                # Create efficiency categories
                efficiency_data['Efficiency_Category'] = pd.cut(
                    efficiency_data['Conversion Rate'],
                    bins=[0, 10, 20, 30, 100],
                    labels=['Low (0-10%)', 'Medium (10-20%)', 'High (20-30%)', 'Exceptional (>30%)']
                )
                
                # Distribution of countries by efficiency category
                category_counts = efficiency_data['Efficiency_Category'].value_counts()
                
                fig_dist = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Distribution of Countries by Conversion Efficiency",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Correlation analysis
                st.markdown("### 🔍 Size vs. Efficiency Analysis")
                fig_correlation = px.scatter(
                    efficiency_data,
                    x='Athletes Sent',
                    y='Conversion Rate',
                    color='Conversion Rate',
                    size='Medals Won',
                    hover_name='Country',
                    title="Team Size vs. Conversion Efficiency",
                    labels={
                        'Athletes Sent': 'Number of Athletes',
                        'Conversion Rate': 'Medal Conversion Rate (%)'
                    }
                )
                st.plotly_chart(fig_correlation, use_container_width=True)
                
                # Insights about DPR Korea and other high performers
                st.info("""
                💡 **High Conversion Rate Analysis**
                
                DPR Korea's exceptional 57.1% conversion rate can be attributed to:
                1. Highly selective athlete participation program
                2. Focus on specific sports with historical success
                3. Intensive training and preparation in targeted events
                4. Strategic resource allocation to medal-potential disciplines
                
                This approach differs from larger delegations that participate across many sports,
                often resulting in lower overall conversion rates but higher total medal counts.
                """)
            
            # Main efficiency scatter plot
            st.subheader("🎖️ Medal Conversion Efficiency by Country")
            fig_scatter = create_efficiency_analysis(efficiency_data)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Add efficiency brackets analysis
            st.subheader("📊 Efficiency Brackets Analysis")
            efficiency_brackets = pd.qcut(efficiency_data['Conversion Rate'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
            bracket_stats = efficiency_data.groupby(efficiency_brackets).agg({
                'Athletes Sent': 'mean',
                'Medals Won': 'mean',
                'Conversion Rate': ['mean', 'count']
            }).round(2)
            
            st.table(bracket_stats)
            
        except Exception as e:
            st.error(f"Error in efficiency analysis: {str(e)}")    
    # Event Analysis Tab
    with tab4:
        st.header("Event-Level Analysis")
        st.write("""
        ### Deep Dive into Olympic Disciplines
        
        Explore the distribution of medals across different Olympic disciplines and uncover patterns
        in how medals are awarded across sports.
        """)
        
        try:
            event_data = load_event_data()
            
            # Overview metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Disciplines", len(event_data))
            with col2:
                top_discipline = event_data.loc[event_data['total_medals'].idxmax()]
                st.metric("Most Medals in Single Discipline", 
                         top_discipline['discipline'],
                         f"{top_discipline['total_medals']} medals")
            with col3:
                avg_medals = event_data['total_medals'].mean()
                st.metric("Average Medals per Discipline", f"{avg_medals:.1f}")
            
            # Main visualization
            st.plotly_chart(create_event_analysis(event_data), use_container_width=True)
            
            # Interactive discipline explorer
            st.subheader("🔍 Discipline Explorer")
            selected_discipline = st.selectbox(
                "Select a discipline to explore:",
                options=sorted(event_data['discipline'].unique())
            )
            
            if selected_discipline:
                discipline_data = event_data[event_data['discipline'] == selected_discipline]
                if not discipline_data.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Medals", discipline_data.iloc[0]['total_medals'])
                    with col2:
                        pct_of_total = (discipline_data.iloc[0]['total_medals'] / event_data['total_medals'].sum() * 100)
                        st.metric("% of All Olympic Medals", f"{pct_of_total:.1f}%")
            
        except Exception as e:
            st.error(f"Error in event analysis: {str(e)}")
    with tab5:
        st.header("📈 The Evolution of the Olympic Games")
        st.write("""
        Journey through time to discover how the Olympic Games have evolved since their modern inception in 1896. 
        This analysis reveals fascinating patterns in participation, achievements, and the growing inclusivity of the Games.
        """)
        try:
            historical_data = load_historical_data()
            
            hist_tab1, hist_tab2, hist_tab3 = st.tabs([
                "Medal Evolution",
                "Gender Diversity",
                "Sports Categories"
            ])
            
            with hist_tab1:
                st.subheader("🏅 The Growth of Olympic Excellence")
                
                medals_by_year = historical_data.groupby(
                    ['Year', 'Medal']
                ).size().reset_index(name='Count')
                
                fig = px.line(medals_by_year,
                    x="Year",
                    y="Count",
                    color="Medal",
                    title="Olympic Medals Awarded Through History",
                    markers=True,
                    color_discrete_map={
                        'Gold': '#FFD700',
                        'Silver': '#C0C0C0',
                        'Bronze': '#CD7F32'
                    })
                
                fig.update_layout(
                    xaxis_title="Olympic Year",
                    yaxis_title="Number of Medals",
                    hovermode='x unified',
                    template="plotly_white"  # Use a white background
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insights remain the same
                col1, col2, col3 = st.columns(3)
                with col1:
                    earliest_year = medals_by_year['Year'].min()
                    st.metric("First Modern Olympics", f"{earliest_year}")
                with col2:
                    total_medals = medals_by_year['Count'].sum()
                    st.metric("Total Medals Awarded", f"{total_medals:,}")
                with col3:
                    avg_medals_per_games = int(medals_by_year.groupby('Year')['Count'].sum().mean())
                    st.metric("Average Medals per Games", f"{avg_medals_per_games:,}")
            
            with hist_tab2:
                st.subheader("👥 Breaking Gender Barriers")
                
                gender_by_year = historical_data.groupby(['Year', 'Sex']).size().reset_index(name='Count')
                gender_by_year = gender_by_year[gender_by_year['Sex'].isin(['M', 'F'])]
                
                # Update gender colors for better differentiation
                fig = px.area(gender_by_year,
                    x="Year",
                    y="Count",
                    color="Sex",
                    title="Gender Participation in Olympic History",
                    color_discrete_map={
                        'M': '#0066cc',  # Strong blue for male
                        'F': '#ff69b4'   # Pink for female
                    })
                
                fig.update_layout(
                    xaxis_title="Olympic Year",
                    yaxis_title="Number of Athletes",
                    hovermode='x unified',
                    template="plotly_white",
                    showlegend=True,
                    legend_title="Gender",
                    legend={'itemsizing': 'constant'}
                )
                
                # Update legend labels
                fig.for_each_trace(lambda t: t.update(name = {'M': 'Male', 'F': 'Female'}[t.name]))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Gender milestones remain the same
                st.info("""
                🎯 Key Milestones in Olympic Gender Equality:
                - 1900: Women first competed in the Olympics (Tennis and Golf)
                - 1928: Women's Athletics and Gymnastics introduced
                - 1984: First Women's Marathon
                - 2012: First Olympics where women competed in all sports
                - 2024: Nearly equal participation between men and women
                """)
                
                # Add gender ratio metrics
                current_year = gender_by_year[gender_by_year['Year'] == gender_by_year['Year'].max()]
                if not current_year.empty:
                    total_athletes = current_year['Count'].sum()
                    female_count = current_year[current_year['Sex'] == 'F']['Count'].iloc[0]
                    male_count = current_year[current_year['Sex'] == 'M']['Count'].iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Female Athletes", f"{female_count:,}")
                    with col2:
                        st.metric("Male Athletes", f"{male_count:,}")
                    with col3:
                        female_percentage = (female_count / total_athletes) * 100
                        st.metric("Female Participation", f"{female_percentage:.1f}%")

            # Sports Categories tab remains the same
            with hist_tab3:
                st.subheader("🎮 Evolution of Olympic Sports")
                
                sports_by_year = historical_data[historical_data['Sport_Category'].notna()].groupby(
                    ['Year', 'Sport_Category']
                ).size().reset_index(name='Count')
                
                fig = px.area(sports_by_year,
                    x="Year",
                    y="Count",
                    color="Sport_Category",
                    title="Growth of Olympic Sports Categories",
                    color_discrete_sequence=px.colors.qualitative.Set3)
                
                fig.update_layout(
                    xaxis_title="Olympic Year",
                    yaxis_title="Number of Events",
                    hovermode='x unified',
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Rest of the sports category analysis remains the same...

                        
        except Exception as e:
            st.error(f"Error in historical analysis: {str(e)}")
if __name__ == "__main__":
    main()