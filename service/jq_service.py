"""
 Methods with Joinquant
 https://www.joinquant.com/

 @note: keep jqdatasdk version <=1.8.5

 * 获取历史交易日直接使用api
 get_all_trade_days()
 get_trade_days(start_date=None, end_date=None, count=None)

 * 获取所有股票直接使用api
 get_all_securities(types=[], date=None)

 * 将标的代码转化成聚宽标准格式
 normalize_code(code)

 * @since 2021.9
 * @version 1st
 * @author Bing.Han
 *
"""
from jqdatasdk import *
import os
import pandas as pd
from tools.mysql_service import MySQLUtil
import datetime


# np.set_printoptions(suppress=True)  # 关闭科学计数法
# pd.set_option('display.max_columns', None)  # 完整显示控制台打印的列
# pd.set_option('display.max_rows', 50)  # 设置控制台打印的行数
# pd.set_option('display.width', 1000)  # 设置控制台打印的宽度

def initial_author():
    auth('137********','Han*******') #username and password
    print(is_auth)
    print(get_query_count())


def initial_js_calendar():
    """
    Initial or update to latest js calendar
    tableName: js_calendar
    :return:
    """
    data = get_all_trade_days()
    df = pd.DataFrame(data)
    df.columns = ['cal_date']
    try:
        if not df.empty:
            MySQLUtil().update("truncate table js_calendar")
            MySQLUtil.df_write(df, 'js_calendar')
            print("SUCCESS")
        else:
          print("EMPTY")
    except Exception as e:
        print(str(e).split("\n")[0].split(") ")[1])


def save_trade_days():
    """
    Get and save all trade days from 2015 to next 2 years
    (Due to the uncertainty of legal holidays each year, the data may be inaccurate)
    :return:
    """
    data = get_all_trade_days()
    df = pd.DataFrame(data)
    df.to_csv('data/ALL_TRADE_DAYS', sep=' ', index=False, header=None) #覆盖原有文件
    # If using pd.DataFrame(data).to_csv, the program executes successfully
    # but the file is not immediately generated.
    print('file ALL_TRADE_DAYS initialized successfully.')


def get_next_date(date, count=1):
    """
    获取未来第N个交易日(date必须是交易日，默认获取下一个交易日)
    :param date: string like 'yyyy-mm-dd'
    :param count: 可以是负数
    :return:
    """
    if not os.path.exists('data/ALL_TRADE_DAYS'):
        print("file ALL_TRADE_DAYS does not exist, please execute all_trade_days()")
        # all_trade_days()
    else:
        file = open('data/ALL_TRADE_DAYS', 'r')
        dates = [line.strip() for line in file]
        file.close()
        try:
            next_date = dates[dates.index(date) + count]
            return next_date
        except ValueError as e:
            # Not in scope or not a trading day
            print(date, 'is either not in date list or not a trading day.')


def save_securities(trade_date=None, save=False):
    securities = get_all_securities(types=['stock'], date=trade_date)
    securities = securities[securities['end_date'] == '2200-01-01']  # 剔除退市
    securities = securities[-securities['display_name'].str.contains('ST')]  # 剔除ST
    securities = securities[securities.index.str[:2].isin(['00', '60'])]  # 剔除30/68

    if save:
        securities.to_csv('./ALL_SECURITIES', sep=' ', index=True, header=True)
        print('ALL_SECURITIES: file initialized successfully')

    return securities  #dataframe: display_name|name|start_date|end_date|type


def get_securities():
    if not os.path.exists('./ALL_SECURITIES'):
        print("ALL_SECURITIES: file does not exist")
    else:
        df = pd.read_csv('./ALL_SECURITIES', sep=' ', header=0, index_col=0)
        return df


def get_code(display_name):
    """
    Get security code by display_name
    :param display_name: e.g. 平安银行
    :return:
    """
    if not os.path.exists('./ALL_SECURITIES'):
        print("ALL_SECURITIES: file does not exist")
    else:
        file = open('data/ALL_SECURITIES', 'r', encoding='UTF-8')
        for line in file:
            if display_name in line:
                code = line.split(' ')[0]
                file.close()
                return code
        # if not find
        file.close()
        return None


def get_name(code):
    """
    Get security display name by code
    :param code: e.g. 000001.XSHE
    :return:
    """
    if not os.path.exists('data/ALL_SECURITIES'):
        print("file ALL_SECURITIES does not exist, please execute all_securities()")
    else:
        file = open('data/ALL_SECURITIES', 'r', encoding='UTF-8')
        for line in file:
            if code in line:
                display_name = line.split(' ')[1]
                file.close()
                return display_name
        # if not find
        file.close()
        return None


def get_security(code):
    """
    > security.__class__
    > <class 'jqdatasdk.utils.Security'>
    > security.__module__
    > 'jqdatasdk.utils'
    > security.__dict__.keys()
    > dict_keys(['code', 'display_name', 'name', 'start_date', 'end_date', 'type', 'parent'])
    >
    :param code:
    :return:
    """
    code = normalize_code(code)
    security = get_security_info(code)
    return security.__dict__


def get_df_price(frequency='1d', security=None, end_date=None, count=1):
    """
    获取指定日期（可以是非交易日）的价格数据
    :param frequency: 'Xd','Xm'
    :param security:
    :param end_date: default 2015-12-31
    :param count:
    :return:
    """
    if security is None:
        security = list(get_securities().index)
    if end_date is None:
        end_date = str(datetime.date.today())
    df_price = get_price(security
                         # (start_date, count) only one param is required
                         # query result includes end date data
                         # default end_date None means 2015-12-31
                         , frequency='daily'
                         , count=count
                         , end_date=end_date
                         ,
                         fields=['open', 'close', 'low', 'high', 'volume', 'money', 'factor', 'high_limit', 'low_limit',
                                 'avg', 'pre_close']
                         , skip_paused=True)
    df_price['change_pct'] = round(df_price['close'] / df_price['pre_close'] - 1, 4)

    df_price['high_pct'] = round(df_price['high'] / df_price['pre_close'] - 1, 4)
    df_price['swing'] = round((df_price['high'] - df_price['low']) / df_price['pre_close'], 4)
    df_price['center'] = round(0.5 * (df_price['open'] + df_price['close']), 3)

    return df_price


def get_mac(security, trade_date, ma, frequency='daily'):
    """
    单个股票单日的MA数据
    :param security:
    :param trade_date:
    :param ma:
    :param frequency:
    :return:
    """
    if ma not in (5, 10, 20, 60, 250):
        print("invalid ma value:", ma)
    df = get_price(security
                   , count=ma
                   , end_date=trade_date
                   , frequency=frequency
                   , skip_paused=True)
    value = df['close'].mean()
    return value


def get_df_bar(security, unit, end_dt=None, days=1):
    """
    获取指定日期（及之前）的K线数据
    :param security:
    :param unit: '1m'(as tick), '5m', '15m', '30m', '60m', '120m', '1d', '1w', '1M'
    :param end_dt: None means now
    :param days: how many trading days does the tick data span
    :return:
    """
    if end_dt is not None:
        # switch current trading date to its next trading date
        end_dt = get_next_date(end_dt)

    df_bar = get_bars(security, count=get_unit_count(unit) * days, unit=unit, include_now=False,
                      fields=['date', 'open', 'close', 'high', 'low', 'volume', 'money'],
                      # query result does not include end_dt data
                      end_dt=end_dt)
    df_bar.set_index('date', inplace=True)

    return df_bar


def get_curve(security, unit="1m", end_dt=None):
    """
    获取指定交易日的相对价格曲线（包含分时线和均价线）
    :param security:
    :param unit: '1m, '5m'
    :param end_dt: None means now
    :return:
    """
    df = get_df_bar(security, unit, end_dt)
    pre_close = get_df_price(security, end_dt)['pre_close'][0]
    df['curve'] = round(df['close'] / pre_close - 1, 4)  # as is change_pct
    df['avg'] = round(df['money'].cumsum() / df['volume'].cumsum(), 3)
    df['avg_curve'] = round(df['avg'] / pre_close - 1, 4)

    return df


def get_df_tick(security, days=1, end_dt=None):
    df_tick = get_df_bar(security, '1m', days=days, end_dt=end_dt)
    return df_tick


def get_daily_limit(trade_date):
    """
    获取指定日期的涨停股
    :param trade_date:
    :return: dataframe: time|code|close|high_limit|paused
    """
    stock_list = list(get_securities().index)
    df_price = get_price(stock_list
                         # (start_date, count) only one param is required
                         # query result includes end date data
                         , count=1
                         , end_date=trade_date
                         , frequency='daily'
                         , fields=['close', 'high_limit', 'paused'])
    df_limit = df_price[df_price['close'] == df_price['high_limit']][df_price['paused'] == 0.0]

    return df_limit


def get_sudden_limit(end_date):
    '''
    description: 获取指定日期的突然涨停股(采用策略为ma5 slope)
    '''
    df_limit = get_daily_limit(end_date)

    if len(df_limit) == 0:
        return None

    # filter limit with ma5 slope rule
    code_list = []
    for code in df_limit['code']:
        df_price = get_df_price(code, end_date=end_date, count=3+5-1)

        # 付费因子
        factor_data = get_factor_values(securities=code,
            factors=['MAC5'],
            end_date=end_date,
            count=3)
        ma5 = df_price['close'] * factor_data['MAC5'][code]

        # # 自定义方法
        # cal_ma(df_price, 5)
        # ma5 = df_price['ma5'][-3:]

        # The slope of the previous two trading days
        slope = (ma5[1]-ma5[0]) / ma5[0]
        if abs(slope) < 0.01 :
            code_list.append(code)
            print(code)

    return code_list


def get_limit_set(date):
    """
    仅用于演示差集和交集的取法
    :param date:
    :return:
    """
    date1 = get_next_date(date, count=1)
    date2 = get_next_date(date, count=2)
    date3 = get_next_date(date, count=3)

    l1 = get_daily_limit(date1)
    l2 = get_daily_limit(date2)
    l3 = get_daily_limit(date3)

    # 取l1 l2差集
    code_set = l2.append(l1).append(l1).drop_duplicates(['code'], keep=False)

    # 取l2 l3交集
    code_set = pd.merge(code_set, l3, on='code')

    return code_set


def get_rebound(security_list):
    """
    获取底部反弹股
    @Note: That's down more than 50% in three months
    :param security_list: list type
    :return:

    todo: unfinished function
    """
    for security in security_list:
        df = get_bars(security, 3, unit='1M',
            fields=['date', 'open', 'high', 'low', 'close'],
            include_now=False, end_dt=str(datetime.date.today()))


#
# Common methods
#


def format_date(date):
    """
    Format date string from '2021-1-1' to '2021-01-01'
    :param date:
    :return:
    """
    return  str(datetime.datetime.strptime(date, '%Y-%m-%d').date())


def save_df(df, filepath=""):
    """
    Save dataframe data to txt file
    :param df:
    :param filepath: ".../"
    :return:
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    df.to_csv(filepath+timestamp+'.txt', sep=' ', index=True, header=True)
    print("df data saved.")


def load_df(filename):
    """
    Load data as dataframe from txt file
    :param filename: include filepath
    :return:
    """
    df = pd.read_csv(filename, sep=' ', header=0, index_col=0)
    print(filename, 'file loaded with', len(df), 'rows.')
    return df


def get_unit_count(unit):
    """
    get count by unit
    :param unit:
    :return:
    """
    tick = {'1m':240, '5m':48, '10m':24, '15m':16, '30m':8, '60m':4, '120m':2}
    try :
        count = tick[unit]
        return count
    except TypeError as e:
        print('unknown unit value', unit)