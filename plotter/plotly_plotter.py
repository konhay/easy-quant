"""
 * Plotly Plotter
 *
 * Intro to Animations in Python
 * https://plotly.com/python/animations/
 *
 * Basic Range Slider and Range Selectors
 * https://plotly.com/python/range-slider/
 *
 * Simple Candlestick with Pandas
 * https://plotly.com/python/candlestick-charts/
 *
 * @since 2020.1
 * @version 1st
 * @author Bing.Han
 *
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_animations_go(df, y_name='close', name=None):
    """

    :param df: dataframe
    :param y_name: y column name
    :param name: chart name
    :return:
    """
    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {"range": [0, len(df) - 1], "title": "x"}
    fig_dict["layout"]["yaxis"] = {"title": y_name}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    # define sliders_dict for layout sliders
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Point:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # make data
    data_dict = {
        "x": list(np.arange(len(df))),
        "y": list(df[y_name]),
        "mode": "lines",
        "text": list(df.iloc[:].index),
        "name": name
    }
    fig_dict["data"] = data_dict

    # make frames
    for i in np.arange(len(df)):
        # make frames
        frame = {"data": [], "name": 'frame' + str(i)}
        data_dict = {
            "x": list(np.arange(0, i + 1)),
            "y": list(df.iloc[0:i + 1][y_name]),
            "mode": "lines",
            "text": list(df.iloc[0:i + 1].index),
            "name": name
        }
        frame["data"].append(data_dict)
        fig_dict["frames"].append(frame)

        # initial steps of sliders_dict (for layout)
        slider_step = {
            "args": [
                i,
                {"frame": {"duration": 300, "redraw": False},
                 "mode": "immediate",
                 "transition": {"duration": 300}}
            ],
            "label": int(i),
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    fig.show()


def plot_animations_px(df, y_name='close', zero=False):
    """

    :param df: dataframe
    :param y_name: y column name
    :param zero: chart name
    :return:
    """
    df['point'] = 0  # slider number
    df['datetime'] = df.index
    df.index = np.arange(1, len(df) + 1)

    # make dataset
    if not zero:
        # plotting begin with point 1 (240 points totally)
        dataset = pd.DataFrame()
    else:
        # plotting begin with point 0 (241 points totally)
        dataset = df.copy()

    for i in np.arange(len(df)):
        # append dataframe for every single tick point
        df['point'] = i + 1
        dataset = pd.concat([dataset, df.iloc[0:i + 1]], ignore_index=False)  # keep old index as x value

    fig = px.line(dataset
                  , x=dataset.index
                  , y=y_name
                  , animation_frame="point"
                  , animation_group=dataset.index
                  , hover_name="datetime"
                  , range_x=[1, len(df)] # define xaxis scope
                  , range_y=[min(df[y_name]), max(df[y_name])] # define yaxis scope
                  )

    # fig.update_layout(yaxis= dict(autorange=True)) # ineffective
    fig.update_layout(title_text="Trend")

    fig.show()


def plot_scatter(df, y_name='close'):
    """

    :param df: dataframe
    :param y_name: y column name
    :return:
    """
    # Create figure
    fig = go.Figure()

    # Add trace
    fig.add_trace(
        go.Scatter(x=list(df.index), y=list(df[y_name])))

    # Set title
    fig.update_layout(
        title_text="Time series with range slider and selectors"
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="category",
            nticks=30,
        )
    )
    fig.show()


def plot_scatter_tick(df, y_name, days):
    """
    Only support tick data(1m), can be multiple days
    :param df: dataframe
    :param y_name: y column name
    :param days: trading days
    :return:
    """
    # set 15:00 data to None
    if abs(days) != 1:
        df.iloc[np.arange(1, abs(days)) * 240 - 1] = None

    fig = go.Figure(
        data=go.Scatter(x=np.arange(0, len(df)), y=df[y_name], mode='lines'),
        layout=go.Layout(
            # set figure size or not
            height=400, width=1200,
            # # there are 240 samples by minute per trading date
            xaxis=dict(
                tickvals=np.arange(0, days) * 240,
                ticktext=(['d' + str(x + 1) for x in np.arange(days)])
            )
        )  # Reference :property xaxis of _layout.py
    )
    fig.show()


def plot_scatter_8steps(df, y_name):
    """
    Show daily tick data(1m) as eight steps per half an hour
    :param df: dataframe
    :param y_name: column name as y value, for example JoinQuant:'price', tushare:'close'
    :return:

    how to remove df.iloc[120,121] ? if 240 need to be changed to 242 ?
                         price  change      volume    amount
    2020-07-01 11:30:00  3.000   -0.01  119.000000   35800.0
    2020-07-01 13:00:00  3.005    0.00  343.333333  103080.0
    """
    if len(df) != 240:
        print("len(df) must be 240, but", len(df))
        return

    # Make Sub-plots (https://plotly.com/python/table-subplots/)

    # rows * cols must be 8
    rows, cols = 4, 2

    fig = make_subplots(
        rows=rows,
        cols=cols,
        shared_xaxes=False,
        horizontal_spacing=0.05,
        vertical_spacing=0.05,
        specs=[[{"type": "scatter"}] * cols] * rows
    )

    # add trace for every subplot
    for i in np.arange(1, rows + 1):
        for j in np.arange(1, cols + 1):
            # subplot's serial number
            serial = cols * (i - 1) + j

            # copy a new dataframe for every subplot
            df_copy = df.copy()
            df_copy.index = np.arange(len(df_copy))

            # Separate Mode
            # get difference set across sub-dataframe and total dafaframe
            # index_d = df_copy.index[np.arange((serial-1)*30, serial*30)] ^ df_copy.index

            # Accumulate Mode
            # get unhappened time period
            index_d = df_copy.index[np.arange(serial * 30, 240)]

            # re-value price column of difference set
            df_copy.loc[index_d, y_name] = None

            fig.add_trace(
                go.Scatter(
                    x=df_copy.index,
                    y=df_copy[y_name],
                    mode="lines",
                    line=dict(width=2, color="blue"),
                    name="tick-" + str(serial)
                ),
                row=i,
                col=j,
                secondary_y=None
            )

    # dictionary of xaxis property
    xaxis_dict = {'tickvals': np.arange(1, 9) * 30 - 1,  # array([ 29,  59,  89, 119, 149, 179, 209, 239])
                  'ticktext': (['10:00', '10:30', '11:00', '11:30/13:00', '13:30', '14:00', '14:30', '15:00'])
                  }

    # update figure layout globally
    fig.update_layout(
        # If you do not set height with a large value, subplot swill overlap on the page.
        height=1000,
        showlegend=False,
        title_text="step tick data",
        # update xaxis property for all subplots
        xaxis1=xaxis_dict,
        xaxis2=xaxis_dict,
        xaxis3=xaxis_dict,
        xaxis4=xaxis_dict,
        xaxis5=xaxis_dict,
        xaxis6=xaxis_dict,
        xaxis7=xaxis_dict,
        xaxis8=xaxis_dict
    )
    fig.show()


def plot_candlestick(df):
    """
    Plot candlestick figures.
    :param df: columns 'open','high','low','close' are necessary.
    :return:
    """
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])
    # fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(xaxis=dict(type="category", nticks=30))
    fig.show()


def plot_distribution(df):
    """
    Customizing Individual Bar Colors & Bar Chart with Direct Labels
    https://plotly.com/python/bar-charts/

    :param df: SQL(getDistribution)
    :return:
    """
    if not df.empty:
        # df.columns = ['chg','count']
        df["chg"] = df["chg"].astype(str).str[:-2]  # 去除float后面的.0

        # Make bar dataframe
        chg_list = [str(x) for x in list(range(-10, 11))]
        chg_list.insert(10, '-0')
        df_bar = pd.DataFrame(data={"chg": chg_list})
        df_bar = pd.merge(df_bar, df, on=["chg"], how='left')
        df_bar.fillna(0, inplace=True)
        print(df_bar)

        # Plot bar chart
        colors = ['green', ] * 11 + ['red', ] * 11
        fig = go.Figure(data=[go.Bar(
            x=df_bar["chg"],
            y=df_bar["count"],
            text=df_bar["count"],
            marker_color=colors,
            textposition='auto',
        )])
        fig.update_layout(title_text='Profit and Loss Distribution of Main Market', xaxis=dict(title="Profit and loss by %"), yaxis=dict(title="Number of stocks"))
        fig.show()

    else:
        print("dataframe is empty.")
