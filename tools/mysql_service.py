# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
import pandas as pd
import glog

def watch_prepared_statement(sql, params):
    """
    When we use prepared sql statement, the program doesn't the real sql neither in the python program or
    database process. This function will parse the expected sql statement for debugging.
    """
    expected_sql = sql % tuple(params)
    return expected_sql


class MySQLUtil:
    host = 'localhost'
    port = '3306'
    username = 'username'
    password = 'password'
    db = 'finance'
    charset = 'utf8'
    # mysql_connect = create_engine('mysql://username:password@localhost:3306/finance?charset=utf8')
    mysql_connect = create_engine(
        'mysql+pymysql://' + username + ':' + password + '@' + host + ':' + port + '/' + db + '?charset=' + charset)

    @staticmethod
    def query(sql, params=None):
        """
        Query action.
        :param sql: being executed sql statement
        :param params: sql param, to avoid the sql injection
        :return: Query Result
        :rtype: list
        """
        connection = MySQLUtil.mysql_connect
        cursor = connection.cursor()

        if params is None:
            params = []
        try:
            cursor.execute(str(sql), params)
            result = cursor.fetchall()
        except Exception as e:
            expected_sql = watch_prepared_statement(sql, params)
            glog.error("[" + str(e) + "]" + expected_sql)
            result = None
        finally:
            # release the connection to the pooled
            cursor.close()
            connection.close()

        return result

    @staticmethod
    def update(sql, params=None):
        """
        Update action.
        :param sql: being executed sql statement
        :param params: sql param, to avoid the sql injection
        :return: affected rows count and the last row id
        :rtype: tuple
        """
        connection = MySQLUtil.mysql_connect
        cursor = connection.cursor()

        if params is None:
            params = []
        try:
            cursor.execute(str(sql), params)
            row_count = cursor.rowcount
            row_id = cursor.lastrowid
            connection.commit()
            result = row_count, row_id
        except Exception as e:
            expected_sql = watch_prepared_statement(sql, params)
            glog.error("[" + str(e) + "]" + expected_sql)
            result = None
        finally:
            # release the connection to the pooled
            cursor.close()
            connection.close()

        return result

    @staticmethod
    def call_proc(procname, params=None):
        """
        Call mysql procedule(by hanbing)
        :param procname: procedule name
        :param params: sql param, to avoid the sql injection
        :return: query result or nothing in insert operation
        """
        connection = MySQLUtil.mysql_connect
        cursor = connection.cursor()

        if params is None:
            params = []
        try:
            cursor.callproc(procname, params)
            result = cursor.fetchall()
        except Exception as e:
            glog.error("[" + str(e) + "]" + procname)
            result = None
        finally:
            # release the connection to the pooled
            cursor.close()
            connection.close()

        return result

    @staticmethod
    def df_write(data, table):
        """

        :param data: DataFrame
        :param table: String
        :return:
        """
        pd.io.sql.to_sql(data, table, MySQLUtil.mysql_connect, schema=MySQLUtil.db, if_exists='append', index=False)
        MySQLUtil.mysql_connect.dispose()

        # todo: what's the difference between pd.io.sql.to_sql() and pd.to_sql() ?

    @staticmethod
    def df_read(sql, params=None):
        """

        :param sql: SQL statement
        :param params: parameters
        :return: DataFrame
        """
        df = pd.read_sql(sql, MySQLUtil.mysql_connect, params=params)
        MySQLUtil.mysql_connect.dispose()

        return df
