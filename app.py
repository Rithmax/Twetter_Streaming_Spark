from flask import Flask
from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask,jsonify,request
from flask import render_template
import ast
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import datetime
import random
import requests
import pandas as pd
import numpy as np

server = Flask(__name__)

labels = []
values = []


@server.route('/refreshData')
def refresh_graph_data():
    global labels, values
    print("labels now: " + str(labels))
    print("data now: " + str(values))
    return jsonify(sLabel=labels, sData=values)


@server.route('/updateData', methods=['POST'])
def update_data_post():
    global labels, values
    if not request.form or 'data' not in request.form:
        return "error",400
    labels = ast.literal_eval(request.form['label'])
    values = ast.literal_eval(request.form['data'])
    print("labels received: " + str(labels))
    print("data received: " + str(values))
    return "success",201



app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

def generate_news_table(dataframe, max_rows=10):
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        dataframe.iloc[i]["title"],
                                        href=dataframe.iloc[i]["url"],
                                        target="_blank",
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(dataframe), max_rows))
                    ]
                ),
                style={"height": "150px", "overflowY": "scroll"},
            ),
            html.P(
                "Last update : " + datetime.datetime.now().strftime("%H:%M:%S"),
                style={"fontSize": "11", "marginTop": "4", "color": "#45df7e"},
            ),
        ],
        style={"height": "100%"},
    )

def update_news():
    r = requests.get('https://newsapi.org/v2/top-headlines?sources=financial-times&apiKey=da8e2e705b914f9f86ed2e9692e66012')
    json_data = r.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title","url"]])
    return generate_news_table(df)



app = Dash(server=server)

t=datetime.datetime.now()

app.layout = html.Div(
    [
        html.Div(className='container-fluid', children=[html.H2('Live Twitter Sentiment', style={'color': "#CECECE"})],
                 style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}),

        #dcc.Graph(id='live-graph', animate=True),


        html.Div(className='row', children=[html.Div(dcc.Graph(id='live-graph', animate=False), className='col s12 m6 l6'),
                                            ]),

        html.P(
            t.strftime("%H:%M:%S"),
            id="live_clock",
            style={"color": "#45df7e", "textAlign": "center"},
        ),

        dcc.Interval(id='graph-update',interval=1*5000),
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),

        html.Div([
                    html.P('Headlines',style={"fontSize":"13","color":"#45df7e"}),
                    html.Div(update_news(),id="news")
                    ],
                    style={
                        "height":"33%",
                        "backgroundColor": "#18252E",
                        "color": "white",
                        "fontSize": "12",
                        "padding":"10px 10px 0px 10px",
                        "marginTop":"5",
                        "marginBottom":"0"
        }),

        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),


    ],style={'backgroundColor': app_colors['background'], 'margin-top':'-30px', 'height':'2000px',}
)


@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])
def update_graph_scatter():
    data = plotly.graph_objs.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value',
                   textfont=dict(size=20, color=app_colors['text']))



    return {'data': [data],'layout' : plotly.graph_objs.Layout(
                                                  title='Hash Tag Catogorization',
                                                  font={'color':app_colors['text']},
                                                  plot_bgcolor = app_colors['background'],
                                                  paper_bgcolor = app_colors['background'],
                                                  showlegend=True)}


@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M:%S")


def update_news():
    r = requests.get('https://newsapi.org/v2/top-headlines?sources=financial-times&apiKey=da8e2e705b914f9f86ed2e9692e66012')
    json_data = r.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title","url"]])
    return generate_news_table(df)



@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news_div(n):
    return update_news()



if __name__ == '__main__':
    #server.run(host='0.0.0.0', port=9000)
    app.run_server(host='0.0.0.0', port='9000', debug=False)
