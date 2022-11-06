import dash
from dash import dcc
from dash import html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
# model
from model import prediction
from sklearn.svm import SVR

import dash_bootstrap_components as dbc


def get_stock_price_fig(df):

    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")

    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap",
        dbc.themes.BOOTSTRAP, dbc.themes.MATERIA
    ])
server = app.server
# html layout of site
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        dbc.Container(
                            [
                                # Navigation
                                html.P("Welcome to the Stock Dash App!",
                                       className="lead"),
                                html.Div([
                                    dbc.Input(
                                        id="dropdown_tickers",
                                        type="text",
                                        value="",
                                        placeholder="Enter stock code..."),
                                    dbc.Button("Submit",
                                               id='submit',
                                               className="btn btn-sm"),
                                ],
                                         className="input-group my-4"),
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='my-date-picker-range',
                                        min_date_allowed=dt(1995, 8, 5),
                                        max_date_allowed=dt.now(),
                                        initial_visible_month=dt.now(),
                                        end_date=dt.now().date()),
                                ],
                                         className="d-flex justify-content-evenly my-5"),
                                html.Div([
                                    html.Div([
                                    html.Button("Stock Price",
                                                id="stock",
                                                className="btn btn-sm btn-success"),
                                    html.Button("Indicators",
                                                id="indicators",
                                                className="btn btn-sm btn-success"),
                                    ],
                                             className="d-flex justify-content-evenly my-5"),
                                    
                                    html.Div([
                                        dbc.Input(
                                            id="n_days",
                                            type="text",
                                            placeholder="Enter number of days"),
                                        dbc.Button("Forecast",
                                                   id="forecast",
                                                   className="btn btn-sm"),
                                    ],
                                             className="input-group my-4"),
                                ],
                                         className="buttons"),
                                # here
                            ],
                            className="container"),
                    ],
                    className="col-md-4 side"),

                # content
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [  # header                                     
                                        html.H1("Stock Predictor", id="title"),
                                        html.Img(
                                            id="logo-main",
                                            className="img-fluid",
                                            src=
                                            "https://www.investopedia.com/thmb/oosdd6aVZyqChJIxUQDx5WyTNzo=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-1201350973-5f3d08e11c774a10ac4f1d3b15390e81.jpg"
                                        )
                                    ],
                                    className="nav-head"),
                                html.Div(
                                    [  # header                                     
                                        html.H2(id="ticker"),
                                        html.Img(id="logo",
                                                 className="img-fluid")
                                    ],
                                    className="header"),
                                html.Div(id="description",
                                         className="decription_ticker"),
                                html.Div([], id="graphs-content"),
                                html.Div([], id="main-content"),
                                html.Div([], id="forecast-content")
                            ],
                            className="content"),
                    ],
                    className="col-md-8 contentS")
            ],
            className="row")
    ],
    className="container")

app.logger.info('start')


# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        return "Hey there! Please enter a legitimate stock code to get details.", None, None, None, None, None
        # raise PreventUpdate
    else:
        if val == '':
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None


# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == '':
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == '':
        return [""]
    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    if n_days == None:
        return [""]
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)