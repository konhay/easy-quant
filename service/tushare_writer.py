"""
 * Writers with Tushare Pro
 * https://www.tushare.pro/
 *
 * For "AttributeError: module 'tushare' has no attribute 'set_token'",
 * the file name cannot be the same as the package name.
 *
 * @since 2020.5
 * @version 1st
 * @author Bing.Han
 *
"""
import tushare as ts
import datetime
import time
import configparser
from sqlalchemy.exc import IntegrityError
from tools.mysql_service import MySQLUtil
# warnings.filterwarnings('ignore')


config = configparser.ConfigParser()
config.read('conf/token.conf', encoding='UTF-8')
sections = config.sections()
my_token = config.get(sections[0], "token")
ts.set_token(my_token)
pro = ts.pro_api()

def refresh_trade_cal():
    """
    description: truncate and insert latest trade calendar
    tableName: pro_trade_cal
    :return:
    """
    df = pro.trade_cal()
    try:
        if not df.empty:
            MySQLUtil.update("truncate table pro_trade_cal")
            MySQLUtil.df_write(df, 'pro_trade_cal')
            print("SUCCESS")
        else:
          print("EMPTY")
    except Exception as e:
        print(e)


def refresh_stock_basic():
    """
    description: truncate and insert the latest basic information for all stocks
    table: pro_stock_basic
    :return:
    """
    try:
        df = pro.stock_basic(
            fields='ts_code,symbol name,area industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
        if not df.empty:
            MySQLUtil.update("truncate table pro_stock_basic")
            MySQLUtil.df_write(df, 'pro_stock_basic')
            print("SUCCESS")
        else:
            print("EMPTY")
    except Exception as e:
        print(e)


def insert_daily(trade_date) :
    """
    description: insert one-day daily data for all stocks
    tableName: pro_stock_daily
    for multiple dates, use :
        # for i in dates:
        #     i = i.strftime("%Y%m%d")
        #     insert_stock_daily(i)
    :param trade_date: yyyymmdd
    :return:
    """
    try:
        df = pro.daily(trade_date=trade_date)
        if not df.empty:
            MySQLUtil.df_write(df, 'pro_stock_daily')
            print("SUCCESS", trade_date)
        else:
            print("EMPTY", trade_date)
    except Exception as e:
        # Duplicate Primary Key
        if isinstance(e, IntegrityError):
            print("SKIP", trade_date)
        else:
            print(e)


def append_daily(end_date=None):
    """
    description: append data, support breakpoint resume by parameter end_date
    table: pro_stock_daily
    :param end_date: yyyymmdd
    :return:
    """
    if end_date is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(end_date, '%Y%m%d')
    while(True):
        try:
            # trade_date must be string YYYYMMDD
            df = pro.daily(trade_date=date.strftime("%Y%m%d"))
            if not df.empty:
                MySQLUtil.df_write(df, 'pro_stock_daily')
                print("SUCCESS", date)
            else:
                print("EMPTY", date)
            date = date - datetime.timedelta(days=1)
        except Exception as e:
            # Duplicate Primary Key
            if isinstance(e, IntegrityError):
                print("SKIP", date)
                break
            else:
                print(e)


def insert_daily_basic(trade_date) :
    """
    description: insert one-day daily basic information for all stocks
    table: pro_stock_daily_basic
    for multiple dates, use :
        # for i in dates:
        #     i = i.strftime("%Y%m%d")
        #     insert_daily_basic(i)
    :param trade_date: yyyymmdd
    :return:
    """
    try:
        df = pro.daily_basic(trade_date=trade_date)
        if not df.empty:
            MySQLUtil.df_write(df, 'pro_stock_daily_basic')
            print("SUCCESS", trade_date)
        else:
            print("EMPTY", trade_date)
    except Exception as e:
        # Duplicate Primary Key
        if isinstance(e, IntegrityError):
            print("SKIP", trade_date)
        else:
            print(e)


def append_daily_basic(end_date=None):
    """
    description: append, support breakpoint resume by parameter end_date
    table: pro_stock_daily_basic
    :param end_date: yyyymmdd
    :return:
    """
    if end_date is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(end_date, '%Y%m%d')
    while(True):
        try:
            # trade_date must be string YYYYMMDD
            df = pro.daily_basic(trade_date=date.strftime("%Y%m%d"))
            if not df.empty:
                MySQLUtil.df_write(df, 'pro_stock_daily_basic')
                print("SUCCESS", date)
            else:
                print("EMPTY", date)
            date = date - datetime.timedelta(days=1)
        except Exception as e:
            # Duplicate Primary Key
            if isinstance(e, IntegrityError):
                print("SKIP", date)
                break
            else:
                print(e)


def insert_index_daily(ts_code):
    """
    description: truncate and insert all-history daily data for 000001.SH and 399001.SZ
    table: pro_index_daily
    :param ts_code: e.g. 123456.SZ/SH
    :return:
    """
    try:
        df = pro.index_daily(ts_code=ts_code)
        if not df.empty:
            MySQLUtil.update("truncate table pro_index_daily")
            MySQLUtil.df_write(df, 'pro_index_daily')
            print("SUCCESS", ts_code)
        else:
            print("EMPTY", ts_code)
    except Exception as e:
        print(e)


def append_index_daily(ts_code, end_date=None):
    """
    description: append daily data for 000001.SH and 399001.SZ, support breakpoint resume by parameter end_date
    table: pro_index_daily
    :param ts_code: e.g. 123456.SZ/SH
    :param end_date: yyyymmdd
    :return:
    """
    if end_date is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(end_date, '%Y%m%d')
    while(True):
        # you can use index_daily up to 50 times per minute
        time.sleep(1.2)
        try:
            # trade_date must be string YYYYMMDD
            df = pro.index_daily(ts_code=ts_code, trade_date=date.strftime("%Y%m%d"))
            if not df.empty:
                MySQLUtil.df_write(df, 'pro_index_daily')
                print("SUCCESS", date)
            else:
                print("EMPTY", date)
            date = date - datetime.timedelta(days=1)
        except Exception as e:
            # Duplicate Primary Key
            if isinstance(e, IntegrityError):
                print("SKIP", date)
                break
            else:
                print(e)
