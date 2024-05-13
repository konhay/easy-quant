"""
 * Cufflinks Plotter
 *
 * If you want to use cufflinks :
 * step 1: install chart-studio first (pip3 install chart_studio)
 * step 2: edit ..\cufflinks\offline.py (https://blog.csdn.net/acdefghb/article/details/107412152)
 *
 * @reference: Python金融科技:cufflinks绘制金融图表
 * :https://blog.csdn.net/weixin_43915798/java/article/details/106096026
 *
 * @since 2020.1
 * @version 1st
 * @author Bing.Han
 *
"""
import cufflinks as cf
from plotly.offline import plot, iplot
import numpy as np
import pandas as pd


def plot_quantfig(df, asHtml=False):
    """
    description: plot cufflinks quant figures.
    :param df: columns 'open','high','low','close','volume' are necessary.
    :param asHtml: html or image
    :return:
    """
    # # sort_index: sort by index desc (...,3,2,1,0), as is trade_date asc
    # df.sort_index(ascending=False, inplace=True)
    # # reset_index: reset index to 0,1,2,3,...
    # df.reset_index(drop=False, inplace=True)
    # # inplace=True: Do not create new objects, directly modify the original objects

    # rename columns
    df.rename(columns={'vol': 'volume'}, inplace=True)

    layout = dict(
        # xaxis=dict(
        #     #categoryorder="category ascending",
        #     type='category'), # Excluding non-trading days if setting trade_date as index
    )

    # 去除交易日的另一种方法是，将日期索引转变为字符索引，这样可以避免引入缩略图
    df.index = df.index.format()
    df.index = [x.replace('-', '/') for x in df.index.format()]

    cf.set_config_file(offline=True, world_readable=True)
    #qf = cf.QuantFig(df, title='cufflinks-trend', legend='right', name='QF')
    qf = cf.QuantFig(df, title="Candlestick", legend='right', name='QF')

    # Add trading volume
    qf.add_volume(up_color='red', down_color='green')

    # Add MACD line
    qf.add_macd()

    # Add SMA line
    qf.add_sma(periods=[5, 20], color=['blue', 'red'])

    # # Add EMA line
    # qf.add_ema(periods=[10, 20])

    # # Add RSI line
    # qf.add_rsi(periods=10)

    # Add Bollinger line
    # qf.add_bollinger_bands(periods=10)

    # # Add CCI line
    # qf.add_cci(periods=[10, 20])

    # # # Add ADX line
    # qf.add_adx(periods=5)

    # # Add ATR line
    # qf.add_atr(periods=5)

    # # Add DMI line
    # qf.add_dmi(periods=5)

    #qf.iplot(up_color='red', down_color='green', layout=layout, asHtml=asHtml)  # , asImage=True, display_image=False)
    plot(qf.iplot(up_color='red', down_color='green', layout=layout), filename="test.html")
