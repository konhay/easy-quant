# EasyQuant
## Introduction

This project implements a high-level quantitative toolkit based on open stock data platforms. It uses *mysql* as the backend database, and extracts, processes and integrates daily market data to support the research and development of quantitative strategies.

## Data Source
<img src="img_2.png" alt="img_2.png" style="zoom:50%;" />

[*Tushare*](https://www.tushare.pro/) is a free, open source python financial data interface package. It mainly realizes the processing of stock data, and provides financial analysts with fast, clean and diverse data interfaces, so that they can focus more on the research and implementation of strategies and models.

    with code field name 'ts_code'
    and format '60XXXX.SH', '00XXXX.SZ' for individual stock
    and '000001.SH', '399001.SZ' for index of SSE and SZSE.

<img src="img_1.png" alt="img_1.png" style="zoom:50%;" />

[*JoinQuant*](https://www.joinquant.com/) is a cloud platform tailored for quants, providing easy-to-use API documentation that allows quants to quickly implement and use their own quant trading strategies.

    with code field name 'code' 
    and format '60XXXX.XSHG', 00XXXX.XSHE for individual stock
    and '000001.XSHG', '399001.XSHE' for index of SSE and SZSE.

## Code Structure
    > easy-quant
        > conf 
        > data 
            > demo 
            > html
        > learner 
        > plotter 
        > service 
        > tools 

The ***conf*** folder stores the configuration files required by the project, such as token information, database links, or parameters for strategy objects.

The ***data*** folder holds the *.html* file output from the plotting methods and the images of typical trend (under the ***demo*** subfolder). In addition, the two text files named *ALL_SECURITIES* and *ALL_TRADE_DAYS* are cached to make it faster when getting the trading calendar, stock names or codes without having to access a database or remote API.

The ***learner*** package realizes models based on machine learning and deep learning, which support for further analysis of stock data. We will use a series of popular tools such as *[sklearn](https://github.com/scikit-learn/scikit-learn)*, *[tensorflow](https://github.com/tensorflow/)* and *[Keras](https://keras.io/)*. This folder is currently being extended on demand.

The ***plotter*** package provides a rich visualization implementation. It integrates *[matplot](https://matplotlib.org/), [plotly](https://github.com/plotly), [cufflinks](https://github.com/santosjorge/cufflinks)* and other popular visualization modules, which is very powerful.

The ***service*** package provides the most important data processing capabilities and is built on top of *Tushare* and *JoinQuant*'s remote python APIs. After the market closes, we will call the interfaces of these data platforms to append the latest trading data to our *mysql* database. This process ensures that the data in our database is up to date. Meanwhile, we provide advanced methods for calendar, market data, stock information and trading indicators. Based on these methods, we can easily write our own strategies, such as *"look for stocks that suddenly rose by the daily limit", "Which stocks triggered our MA rule today"*. Of course, you can also write your strategy as a stored procedure and let the database process it periodically.

The **tools** package provides some basic functions, such as database services (on *mysql*), mathematical methods, and so on.

## Database

* Example of mysql function

```sql
-- functionName: getTradeDateBack
-- description: Get trade date backward
CREATE DEFINER=`username`@`dbname` FUNCTION `getTradeDateBack`(TD char(8), N int) RETURNS char(8) CHARSET utf8mb3
    COMMENT 'TD: trade_date with format yyyymmdd; N: number of days;'
begin 
    return (
		select trade_date  
		from (select replace(cal_date,'-','') as trade_date
				,rank() over (order by cal_date desc) rk 
			from js_calendar jc 
			where replace(cal_date,'-','') < TD
		) t 
		where rk = N
	);
end
```

* Example of custom query

```sql
SELECT t.statement FROM finance.sql_statement t WHERE name = 'getSuddenLimit' AND 'version=1.0';
```

```sql
-- queryName: getSuddenLimit 
-- description: Get sudden limit-up stocks using MA5 slope
-- inputs: trade_date

 set @TD1 = (select getTradeDateBackgetTradeDateBack(%s,1));
 set @TD2 = (select getTradeDateBack(%s,2));
 
 with checkSlope as 
 (select *  
 	from (select t1.ts_code
 		, @TD1 as td1 
 		, t1.ma5 as ma5_td1
 		, @TD2 as td2 
 		, t2.ma5 as ma5_td2
 		, round(abs(t1.ma5 - t2.ma5)/t2.ma5, 3) as slope
 		from 
 		(select ts_code, ma5 from pro_stock_kline where trade_date = @TD1) t1 
 		inner join 
 		(select ts_code , ma5 from pro_stock_kline where trade_date = @TD2) t2 
 		on t1.ts_code = t2.ts_code
 	) t 
 	where slope < 0.01 
 	order by ts_code
 ) -- check with ma5 slope 
 
 select a.*, b.*
 from 
 (select t1.* 
 	from pro_stock_daily t1 
 	where 1=1 
 	and t1.trade_date = %s
 	and substring(t1.ts_code,1,2) in ('00','60')
 	and abs(round(t1.pre_close*1.1,2) - round(t1.close,2))<=0.02
 	order by ts_code asc
 ) a -- get daily limit 
 inner join checkSlope b
 on a.ts_code = b.ts_code 
 order by a.ts_code
 ;
```

**For complete database schema script, please contact konhay@163.com*.

## Visualization

* Profit and Loss Distribution of Market, [<button>*Click* </button>](data/html/Profit_and_Loss_Distribution_of_Market,_2024-05-10.html) to open with *html*.

```python
from service.tushare_querier import get_distribution
from plotter.plotly_plotter import plot_distribution
df = get_distribution("20240510")
plot_distribution(df)
```

* Example of Animation Effect, [<button>*Click* </button>](data/html/000001.SZ(PNGAY)_Trend_of_120Days.html) to open with *html*.

```python
from service.tushare_querier import get_stock_daily
from plotter.plotly_plotter import plot_animations_px
df = get_stock_daily("000001.SZ", "20240510", count=120)
plot_animations_px(df, y_name='close')
```

* Candlestick of Underlying Asset, [<button>*Click* </button>](data/html/000001.SZ(PNGAY)_Candlestick,_2024-05-10.html) to open with *html*.

```python
from service.tushare_querier import get_stock_daily
from plotter.cufflinks_plotter import plot_quantfig
df = get_stock_daily("000001.SZ", "20240510", count=120)
df.set_index("trade_date", inplace=True)
plot_quantfig(df)
```



## Next

At present, the project has relatively strong data processing and visualization capabilities. Next, we will focus on the development of factors and policies, as well as support for backtesting. If you have any good suggestions, please contact *konhay@163.com*.
