#!/usr/bin/python3
# -*- coding:utf-8 -*-
import requests
import time
import os
import tushare as ts
import pandas as pd
import concurrent.futures
'''
http://quotes.money.163.com/service/chddata.html?code=代码&start=开始时间&end=结束时间&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP
参数说明：代码为股票代码，上海股票前加0，如600756变成0600756，深圳股票前加1。时间都是6位标识法，年月日，fields标识想要请求的数据。可以不变。
大盘指数数据查询（上证指数000001前加0，沪深300指数000300股票前加0，深证成指399001前加1，中小板指399005前加1，创业板指399006前加1）：
http://quotes.money.163.com/service/chddata.html?code=0000300&start=20151219&end=20171108&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER
'''


# 下载股票日K，网易接口
def stock_163(list_codes,start_time,end_time):
    for id in list_codes:
        if id[-2:] == 'SZ':
            code = '1'+id[:-3]
        else:
            code = '0'+id[:-3]
        res = requests.get('http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP' % (code, start_time, end_time))
        try:
            res.raise_for_status()
            with open("data/%s.csv"%code[1:],"wb")as f:
                f.write(res.content)
        except:
            try:
                stock_tushare(id,start_time,end_time)
            except:
                continue
            continue
        data = pd.read_csv("data/%s.csv"%code[1:],header=0,encoding = "gbk",usecols=[0,1,3,4,5,6,7,8,9,10,11,12,13,14])
        data = data.iloc[:-5]
        data.rename(columns={'日期':'trade_date', '股票代码':'ts_code', '收盘价':'close','最高价':'high','最低价':'low','开盘价':'open','前收盘':'pre_close','涨跌额':'change','涨跌幅':'pct_chg','换手率':'turnover_rate','成交量':'vol','成交金额':'amount','总市值':'total_mv','流通市值':'circ_mv'}, inplace = True)
        data = data[~data['open'].isin([0])]
        data.to_csv("data/%s.csv"%code[1:],index=0)
        # print(code[1:],':','完成')
        time.sleep(1)

# tushare接口（备用）
def stock_tushare(id, start_time, end_time):
    ts.set_token('你的token，没有的去https://tushare.pro/申请')
    pro = ts.pro_api()
    data1 = ts.pro_bar(ts_code=id,adj='qfq', start_date=start_time, end_date=end_time)
    data2 = pro.daily_basic(ts_code=id,start_date=start_time, end_date=end_time, fields='ts_code,trade_date,turnover_rate,total_mv,circ_mv')
    data1['turnover_rate'] = data2.turnover_rate.values
    data1['total_mv'] = data2.total_mv.values
    data1['circ_mv'] = data2.circ_mv.values
    order = ['trade_date','ts_code','close','high','low','open','pre_close','change','pct_chg','turnover_rate','vol','amount','total_mv','circ_mv']
    data = data1[order]
    data = data.iloc[:-5]
    vol = data.vol.values*100
    amount = data.amount.values*1000
    total_mv = data.total_mv.values*10000
    circ_mv = data.circ_mv.values*10000
    data['vol'] = vol
    data['amount'] = amount
    data['total_mv'] = total_mv
    data['circ_mv'] = circ_mv
    data.to_csv("data/%s.csv"%id[:-3],index=0)
    # print(id[:-3],':','完成')
    time.sleep(1)


def main():
    # 获取正常上市交易的股票
    ts.set_token('你的token，没有的去https://tushare.pro/申请')
    pro = ts.pro_api()
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    list_codes = []
    for i in [i for i in data.name.values if i[0]!='*' and i[:2]!='ST']:
        list_codes.append(data[data.name == i].ts_code.values[0])
    # 获取当前时间
    end_time = time.strftime("%Y%m%d", time.localtime())
    start_time = '20090101'
    # stock_163(list_codes, start_time, end_time)  # 获取股票数据并存档
    n = int(len(list_codes)/8)
    list_code = []
    for i in range(0, len(list_codes), n):
        list_code.append(list(list_codes[i:i + n]))
    with concurrent.futures.ProcessPoolExecutor(max_workers=len(list_code)) as executor:
        for item in list_code:
            obj = executor.submit(stock_163, item, start_time, end_time)
    executor.shutdown()


if __name__ == "__main__":
    main()
