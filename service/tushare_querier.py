"""
 * Query methods
 *
 * @since 2020.5
 * @version 1st
 * @author Bing.Han
 *
"""
from tools.mysql_service import MySQLUtil
import pandas as pd


def get_stock_daily(ts_code, trade_date, count=1):
    """
    description: Get individual stock daily data by ts_code and date
    tableName: pro_stock_daily
    :param ts_code: e.g. 123456.SZ/SH
    :param trade_date: yyyymmdd
    :param count: int
    :return:
    """
    df = pd.DataFrame()
    # trade_date当日
    if count == 1:
        sql = """select * from pro_stock_daily where ts_code = %(ts_code)s and trade_date = %(trade_date)s;"""
        args = {"ts_code":ts_code, "trade_date":trade_date}
        df = MySQLUtil.df_read(sql, args)
    # 包含trade_date以及过去若干交易日
    elif isinstance(count, int) and count > 1:
        sql = """select * from (select * from pro_stock_daily where ts_code = %(ts_code)s and trade_date <= %(trade_date)s order by 
        trade_date desc limit %(count)s) t order by trade_date asc;"""
        args = {"ts_code":ts_code, "trade_date":trade_date, "count":count}
        df = MySQLUtil.df_read(sql, args)
    # 包含trade_date以及未来若干交易日
    elif isinstance(count, int) and count < 0:
        sql = """select * from pro_stock_daily where ts_code = %(trade_date)s and trade_date >= %(trade_date)s order by trade_date asc limit 
        %s;"""
        args = {"ts_code":ts_code, "trade_date":trade_date, "count":abs(count)}
        df = MySQLUtil.df_read(sql, args)
    else:
        print("parameter count must be an int value")
    return df


def get_market_daily(trade_date):
    """
    description: Get all stock daily data for specific market
    tableName: pro_stock_basic, pro_stock_daily
    :param trade_date: yyyymmdd
    :return:
    """
    sql = """select t1.* from pro_stock_daily t1 inner join pro_stock_basic t2 on t1.ts_code = t2.ts_code where 
    t1.trade_date = %s and t2.market='主板';"""
    args = {"trade_date": trade_date}
    df = MySQLUtil.df_read(sql, args)
    return df


def get_distribution(trade_date):
    """
    description: Gets data on the distribution of individual stock gains on a given date
    :param trade_date: yyyymmdd
    :return:
    """
    sql = get_query_statement("getDistribution")
    args = {"trade_date": trade_date}
    df = MySQLUtil.df_read(sql, args)
    return df


def get_daily_limit(trade_date):
    """
    description: Get limit-up stocks on a given date
    :param trade_date: yyyymmdd
    :return:
    """
    sql = get_query_statement("getDailyLimit")
    args = {"trade_date": trade_date}
    df = MySQLUtil.df_read(sql, args)
    return df


def get_query_statement(name, version="1.0"):
    sql = """select statement from finance.sql_statement where name = %(name)s and version = %(version)s;"""
    args = {"name": name, "version": version}
    df = MySQLUtil.df_read(sql, args)
    statement = df['statement'][0]
    return statement
