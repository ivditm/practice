import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import create_engine


load_dotenv()


db_config: dict[str:str] = {'user': os.getenv('user', ''),
                            'pwd': os.getenv('password', ''),
                            'host': os.getenv('host', ''),
                            'port': 5432,
                            'db': os.getenv('dbname', '')}

engine = create_engine(
     'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                          db_config['pwd'],
                                          db_config['host'],
                                          db_config['port'],
                                          db_config['db']))

query: str = '''
              SELECT * FROM quotes
             '''
data: pd.DataFrame = pd.io.sql.read_sql(query, con=engine)
data['date']: pd.Series = pd.to_datetime(data['date'])
data['price']: pd.Series = pd.to_numeric(data['price'], errors='coerce')


external_stylesheets: list[str] = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                compress=False)


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']},
                      children=[
    html.H1(children='Динамика фондового рынка',
            style={
             'textAlign': 'center',
             'color': colors['text']
            }),
    html.Br(),
    html.Div([
        html.Div([
            html.Label('Временной период:',
             style={'textAlign': 'center', 'color': colors['text']}),
            dcc.DatePickerRange(start_date=data['date'].dt.date.min(),
                                end_date=data['date'].dt.date.max(),
                                display_format='YYYY-MM-DD',
                                id='dt_selector',), ],
             className='four columns'),
        html.Div([
            html.Label('Режим отображения:',
                       style={'textAlign': 'center', 'color': colors['text']}),
            dcc.RadioItems(options=[
                {'label': html.Div(['Стоимость акции'],
                                   style={'color': 'Gold',
                                          'font-size': 12}),
                           'value': 'absolute_values'},
                {'label': html.Div(['Доходность акции'],
                                   style={'color': 'Gold',
                                          'font-size': 12}),
                    'value': 'relative_values'},
            ],
             value='absolute_values',
             id='mode_selector'),
        ], className='two columns'),
        html.Div([
            html.Label('Компании:',
                 style={'textAlign': 'center', 'color': colors['text']}),
            dcc.Dropdown(options=[{'label': x, 'value': x} for x in data[
                'company_name'
                ].unique()],
                         value=data['company_name'].unique().tolist(),
                         multi=True,
                         id='company_selector'), ], className='six columns'),
    ], className='row'),
    html.Br(),
    html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H5('Стоимость/доходность акций по дням',
             style={'textAlign': 'center', 'color': colors['text']}),
        dcc.Graph(
                id='quotes_per_day'), ], className='row'),

    html.Div([
        html.Div([
            html.H5('Средняя стоимость/доходность акций',
             style={'textAlign': 'center', 'color': colors['text']}),
            dcc.Graph(
                id='quotes_scatter_mean'), ], className='eight columns'),
        html.Div([html.H5('Распределение стоимости/доходности акций',
             style={'textAlign': 'center', 'color': colors['text']}),
                  dcc.Graph(
                    id='quotes_box'
                    ), ], className='four columns'), ], className='row'),
])


@app.callback(
    [Output('quotes_per_day', 'figure'),
     Output('quotes_box', 'figure'),
     Output('quotes_scatter_mean', 'figure'), ],
    [Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
     Input('mode_selector', 'value'),
     Input('company_selector', 'value'), ])
def update_figures(start_date, end_date, mode, selected_companys, data=data):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    filtered_data = data.query('date >= @start_date and date <= @end_date')
    filtered_data = filtered_data.query('company_name in @selected_companys')
    if mode == 'relative_values':
        filtered_data['price'] = data['price'].pct_change()

    data_quotes_per_day = []
    for company in filtered_data['company_name'].unique():
        data_quotes_per_day += [go.Scatter(x=filtered_data.query(
                                     'company_name == @company')['date'],
                            y=filtered_data.query(
            'company_name == @company')['price'],
                            mode='lines',
                            stackgroup='one',
                            name=company)]
    data_quotes_box = []
    for company in filtered_data['company_name'].unique():
        data_quotes_box += [go.Box(x=filtered_data.query(
            'company_name == @company')['price'],
                            name=company)]
    data_scatter_mean = []
    filtered_data['year'] = filtered_data['date'].dt.year
    grouped_data = (filtered_data
                    .groupby(['year', 'company_name'])
                    .agg({'price': 'mean'})
                    .reset_index())
    for company in grouped_data['company_name'].unique():
        data_scatter_mean += [go.Bar(x=grouped_data.query(
                                     'company_name == @company')['year'],
                                     y=grouped_data.query(
            'company_name == @company')['price'],
                                     name=company)]
    return (
                {
                    'data': data_quotes_per_day,
                    'layout': go.Layout(xaxis={'title': 'Дата и время'},
                                        yaxis={'title': 'Акции'},
                                        plot_bgcolor=colors['background'],
                                        paper_bgcolor=colors['background'],
                                        font={'color': colors['text']})
                 },
                {
                    'data': data_quotes_box,
                    'layout': go.Layout(xaxis={'title': 'Распределение'},
                                        plot_bgcolor=colors['background'],
                                        paper_bgcolor=colors['background'],
                                        font={'color': colors['text']})
                 },
                {
                    'data': data_scatter_mean,
                    'layout': go.Layout(xaxis={'title': 'Дата и время'},
                                        yaxis={
                                            'title': 'Средняя'
                                            ' стоимость/доходность акции'
                                        },
                                        plot_bgcolor=colors['background'],
                                        paper_bgcolor=colors['background'],
                                        font={'color': colors['text']})
                 },
    )


if __name__ == '__main__':
    app.run_server(debug=False)
