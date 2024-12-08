import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
df_events = pd.read_csv(r'C:\Users\sreev\Data Visualization\Olympics 2024\Paris 2024 Summer Olympic Games Data analysis\Exported Data\Dominance in a Specific Event.csv')  # Replace with your file path

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Medal Analysis by Event", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df_events['country'].unique()],
        placeholder="Select a Country",
        style={'width': '50%', 'margin': 'auto'}
    ),
    dcc.Graph(id='medal-breakdown'),
])

# Callback
@app.callback(
    Output('medal-breakdown', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_graph(selected_country):
    if not selected_country:
        return {}
    
    # Filter data by selected country
    filtered_data = df_events[df_events['country'] == selected_country]
    
    # Melt the dataframe to long format for easier plotting
    melted_data = filtered_data.melt(
        id_vars=['event'], 
        value_vars=['Gold_Medals', 'Silver_Medals', 'Bronze_Medals'],
        var_name='Medal Type',
        value_name='Count'
    )
    
    # Create the bar chart
    fig = px.bar(
        melted_data,
        x='event',
        y='Count',
        color='Medal Type',
        title=f"Medal Breakdown for {selected_country}",
        labels={'event': 'Event', 'Count': 'Number of Medals'},
        barmode='group'
    )
    fig.update_layout(xaxis_tickangle=45, title_x=0.5, plot_bgcolor='white')
    return fig

# Run app
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
