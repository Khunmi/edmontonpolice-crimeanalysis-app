import pandas as pd
import geopandas as gpd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl
# from task import mapper
# import dash_leaflet.express as dlx
# from dash_extensions.javascript import Namespace
import json

CHROMA = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gdf = gpd.read_file(r'data/crime_record.zip')
gdf1 = gpd.read_file(r'data/City_of_Edmonton_-_Corporate_Boundary__current.zip')
data_with_tooltip = gdf.copy(deep=True)
data_with_tooltip['tooltip'] = gdf.school_nam +'<BR>Crime Reported: '+gdf.NUMPOINTS.astype('string')
t_crimes = data_with_tooltip['NUMPOINTS'].sum()
t_schools = data_with_tooltip['NUMPOINTS'].count()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    external_scripts=[CHROMA])
server = app.server

df1 = pd.read_csv('data\crime_count.csv')
df2 = pd.read_csv('data\crimes_1km.csv')
# gjson = pd.read_csv('data\crime_count.geojson')

app.title = 'Edmonton Crime Analysis - Public Schools Proximity 2023'

app.layout = html.Div([
    html.Div(id='page-top-placeholder', style={'padding': 3}),
    html.Div([
        html.H2(dbc.Badge('Edmonton Crime Analysis- Public School Proximity',
                          className='ms-1', color="white", text_color='black',
                          style={'padding-top': 30, 'padding-left': 150}))
    ], style={'display': 'inline-flex', 'backgroundColor': 'white',
              'border-radius': '10px', 'width': '99.5%', 'margin-left': '0.25%'}),
    html.Div([
        html.Div([
            html.H5(dbc.Badge("", className="mt-0", text_color="black", color='white'),
                    style={'text-align': 'left', 'padding-top': '10px'}),
            dbc.InputGroup([
                html.H5(dbc.Badge("Month", className="mt-0", text_color="black", color='white'),
                        style={'text-align': 'center', 'width': '20%'}),
                dcc.Dropdown(id='month_selection', value='Jun',
                             options=[{'label': mon, 'value': mon} for mon in sorted(df2.month.unique())],
                             multi=False, style={'margin': '0 auto', 'width': '80%'})
            ], style={'padding-top': '10px'}),
            dbc.InputGroup([
                html.H5(dbc.Badge("Crime Category", className="mt-0", text_color="black", color='white'),
                        style={'text-align': 'center', 'width': '20%'}),
                dcc.Dropdown(id='crime-occurrence', value='Drugs',
                             options=[{'label': reg, 'value': reg} for reg in sorted(df2.Occurrence_Category.unique())],
                             multi=False, style={'margin': '0 auto', 'width': '80%'})
            ], style={'padding-top': '10px'}),
            dbc.InputGroup([
                html.H5(dbc.Badge("School Ward", className="mt-0", text_color="black", color='white'),
                        style={'text-align': 'center', 'width': '20%'}),
                dcc.Dropdown(id='school_ward', value='WARD 01',
                             options=[{'label': reg, 'value': reg} for reg in sorted(df1.city_ward.unique())],
                             multi=False, style={'margin': '0 auto', 'width': '80%'})
            ], style={'padding-top': '10px'})
        ], style={'display': 'inline-flex', 'width': '100%'}),
    ], style={"background-color": '#E8E8E8'}),
    html.Br(),
    html.Div([html.Div(id='output_container', children=[],style ={'float':'down'}),
              html.Button("Click to Activate Ward Map View", id='btn1', style ={'float':'right','display': 'inline-flex', 'backgroundColor': 'white'}),
        dl.Map([
            dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
            dl.GeoJSON(data=json.loads(data_with_tooltip.to_json()),
            id="Geojson", zoomToBounds=True,zoomToBoundsOnClick = True)
        ],    
            style={"width": "1620px", "height": "500px"}),
            html.Div([
        html.H4(dbc.Badge('A total of {} public schools were analysed and a total of {} crimes have been reported within 1.5km proximity as of the time of data extraction.'.format(t_schools, t_crimes),
                          className='ms-1', color="white", text_color='black',
                          style={'padding-top': 0, 'padding-left': 0}))
    ], style={'display': 'inline-flex', 'backgroundColor': 'white',
              'border-radius': '10px', 'width': '99.5%', 'margin-left': '0.25%'})
    ]),
    html.Br(),
    html.Div(children=[
        dcc.Graph(id='busiest_week_day', figure={},
                  style={'display': 'inline-block', 'padding-right': '70px', 'padding-left': '20px',
                         "width": "820px", "height": "450px"}),
        dcc.Graph(id='monthly_crime_freq', figure={},
                  style={'display': 'inline-block', 'padding-right': '0px', 'padding-left': '20px',
                         "width": "820px", "height": "450px"})
    ]),
])


@app.callback(
           Output('busiest_week_day','figure'),   
    Input('month_selection', 'value'),
    Input('crime-occurrence', 'value')   
    )

def chart_update(month, crime):

    print(month)
    print(crime)
    print(type(crime))
    print(type(month))
    print(len(month))
    print(len(crime))

    # container = "Crime Category chosen is: {} and year chosen is {}".format(crime,month)

    df2_1 = df2.copy()
    df2_1 = df2_1[(df2_1['Occurrence_Category'] == crime) & (df2_1['month'] == month) ]

    # df2_2 = df2.copy()
    # df2_2 = df2_2[df2_2['month'] == month]

         # Plotly Express
    fig = px.bar(
        data_frame=df2_1,
        x='weekday',
        y='Reported_Day',
        title='Weekday Crime Distribution',
        #scope="usa",
        # color='Occurrence_Group',
        hover_data=['Date_Reported'],
        labels={'Reported Day'},
        template='plotly_dark'
    )


    return fig

@app.callback(
           Output('monthly_crime_freq','figure'),   
       Input('crime-occurrence', 'value')   
    )

def chart_update(crime):

    
    print(crime)
    print(type(crime))
    print(len(crime))

    # container = "Crime Category chosen is: {} and year chosen is {}".format(crime,month)

    df2_2 = df2.copy()
    df2_2 = df2_2[(df2_2['Occurrence_Category'] == crime)]

    # df2_2 = df2.copy()
    # df2_2 = df2_2[df2_2['month'] == month]

         # Plotly Express
    fig2 = px.bar(
        data_frame=df2_2,
        x='month',
        y='Reported_Day',
        title='Monthly Distribution of Crime',
        #scope="usa",
        # color='Occurrence_Group',
        hover_data=['Date_Reported'],
        labels={'Reported Day'},
        template='plotly_dark'
    )


    return fig2

@app.callback(
    Output('Geojson','data'),  
    Input('btn1', 'n_clicks'),
    Input('school_ward', 'value')

    )

def btn_filter(n_clicks, ward):

    if (n_clicks and (n_clicks % 2 == 1)):
        return json.loads(data_with_tooltip[data_with_tooltip.city_ward == ward].to_json())
    else:
        return json.loads(data_with_tooltip.to_json())
    
    
@app.callback(
    Output('output_container', 'children'),
    Input('school_ward', 'value')
    )

def map_info(input):

    total_crimes = data_with_tooltip[data_with_tooltip.city_ward == input]['NUMPOINTS'].sum()
    total_schools = data_with_tooltip[data_with_tooltip.city_ward == input]['NUMPOINTS'].count()
    
    container = "Total number of crimes reported within 1.5km radius of {} public schools in {} is {}".format(total_schools,input,total_crimes)

    return container


     # Plotly Graph Objects (GO)
    # fig3 = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode ='geojson-id',
    #         locations=df1_1['address'],
    #         z=df1_1["NUMPOINTS"].astype(float),
    #         colorscale='Reds'
    #     )]
   
    # fig3.update_layout(
    #     title_text="Crime Severity Map Around Public Schools",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='canada')
    # )

    # )

    # return fig3
    
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )





if __name__ == '__main__':
    app.run_server(debug=True)