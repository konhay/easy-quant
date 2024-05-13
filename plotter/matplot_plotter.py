"""
 * Matplotlib Plotter
 *
 * @since 2020.1
 * @version 1st
 * @author Bing.Han
 *
"""
from matplotlib import ticker
from matplotlib import pyplot as plt
import mpl_finance as mpf
import datetime
import math

# import matplotlib
# matplotlib.use('Agg')

# 指定默认字体
plt.rcParams['font.sans-serif'] = ['SimHei']

# 解决保存图像是负号'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False


def format_plot(ax):
    """
    格式化绘图参数
    :param ax:
    :return:
    """
    # 为y轴刻度设置百分比格式
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
    # 隐藏刻度(含x，y轴)
    ax.tick_params(length=0)
    # 隐藏x轴（浅灰色，含）
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # 隐藏子图实黑色边沿
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_line(df, column='close', display=False):
    """
    绘制收盘价折线图
    :param df: dataframe including close price at least
    :param column:
    :param display:
    :return:
    """
    # set image size to 600x200
    fig = plt.figure(figsize=(6, 2))
    ax = fig.add_subplot(111)
    plt.plot(range(len(df)), df[column])
    # format_plot(ax)
    if display:
        plt.show()
    else:
        file_name = 'data/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + '.jpg'
        plt.savefig(file_name)  # , bbox_inches='tight') #488x178
        print(file_name, "saved.")
    plt.close()


def plot_bar(df, display=False):
    """
    绘制K线烛状图
    :param df: dataframe with columns open, high, low, close at least.
    :param display:
    :return:
    """
    # set image size to 600x200
    fig = plt.figure(figsize=(6, 2))
    ax = fig.add_subplot(111)
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.6, colorup='r', colordown='g')
    # format_plot(ax)
    if display:
        plt.show()
    else:
        file_name = 'data/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + '.jpg'
        plt.savefig(file_name)  # , bbox_inches='tight') #488x178
        print(file_name, "saved.")
    plt.close()


def plot_tick(df, days=1, average=True, display=False):
    """
    绘制绝对价格分时图(绝对价格分时图的劣势之一是误认为除权是暴跌)
    df: return value from get_df_tick()
    days: how many trading days does the tick data span
    :param df:
    :param days:
    :param average:
    :param display:
    :return:
    """
    # 4.3 is a constant value
    fig = plt.figure(figsize=(math.log(days) * 4.3, 3))
    ax = fig.add_subplot(111)
    count = int(len(df) / days)
    for i in range(days):
        # plot minute tick line, ten colors default
        plt.plot(range(i * count, (i + 1) * count),
                 df['close'][i * count: (i + 1) * count])
        if average:
            # get average price list
            price_avg = df['money'][i * count:(i + 1) * count].cumsum() / df['volume'][
                                                                          i * count:(i + 1) * count].cumsum()
            # plot average price line
            plt.plot(range(i * count, (i + 1) * count), price_avg)
    format_plot(ax)
    if display:
        plt.show()
    else:
        file_name = 'data/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + '.jpg'
        plt.savefig(file_name)  # , bbox_inches='tight') #488x178
        print(file_name, "saved.")
    plt.close()
