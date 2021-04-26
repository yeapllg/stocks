#!/usr/bin/python3
# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import longhu_data
import requests
import json
import time

'''
龙虎榜腾讯接口
https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/lhbDetail?&date=2021-04-21   列表,date参数为空表示最新
https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/stockDetail?&stockCode=sz002241    明细
'''
# a = requests.get('https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/stockDetail?&stockCode=sz002241',timeout=(10,5)).text
# print(json.loads(a)['data']['detail'])
# https://data.gtimg.cn/flashdata/hushen/daily/21/sz000750.js

#选股
def xuangu():
    date = '2021-04-23' #确定日期，一般是当天或者最近的一个交易日，当天一般下午4点半之后龙虎榜会更新，所以晚上运行程序选股票比较好
    youzi = longhu_data.data
    dict_stock = {}
    list_stock = []
    data = requests.get('https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/lhbDetail?&date=%s'%date,timeout=(10,5)).text
    for i in json.loads(data)['data']['all']:
        if i[0] in list_stock:
            continue
        list_stock.append(i[0])
        if float(i[4]) > 9.0: #只有涨停票才算
            share = requests.get('https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/stockDetail?&stockCode=%s'%i[0],timeout=(10,5)).text
            for j in json.loads(share)['data']['detail']:
                if j['date'] == date:
                    buy = j['buy']
                    sell = j['sell']
                    n = 0
                    mai = 0
                    for m in buy:
                        if '专用' in m[1]:
                            n = n+1
                            mai = mai + m[2]
                        elif m[1] in list(youzi.keys()):
                            n = n+1
                            mai = mai + m[2]
                        else:
                            pass
                    if n >= 2:
                        for g in sell:
                            if '专用' in g[1]:
                                n = n-1
                            elif g[1] in list(youzi.keys()):
                                n = n-1
                    if n >= 2:
                        if mai/sum([q[2] for q in buy]) >= 0.6:
                            print(mai)
                            # print(json.loads(share)['data']['detail'][:2])
                            # print(json.loads(share)['data']['stockCode'],json.loads(share)['data']['stockName'])
                            print(json.loads(share)['data']['stockCode'],n)
                            dict_stock[json.loads(share)['data']['stockCode']] = {'attention':n}
            print(json.loads(share)['data']['stockName'],'完成')
            time.sleep(0.5)

    print(dict_stock)

#回测
def huice():
    dict_stock = {}
    times = requests.get('https://data.gtimg.cn/flashdata/hushen/daily/21/sh000001.js',timeout=(10,5)).text  #这里只是通过这个接口获取21年的交易日
    times = times.split('\\n\\\n')[1:-1]
    for t in times[:-6]:
        date_y = t.split(' ')[0]
        date =  '20'+date_y[:2]+'-'+date_y[2:4]+'-'+date_y[4:]
        youzi = longhu_data.data
        list_stock = []
        data = requests.get('https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/lhbDetail?&date=%s'%date,timeout=(10,5)).text
        for i in json.loads(data)['data']['all']:
            if i[0] in list_stock:
                continue
            list_stock.append(i[0])
            if float(i[4]) > 9.0: #只有涨停票才算
                m = 0
                while True:
                    if m == 5:
                        break
                    try:
                        share = requests.get('https://proxy.finance.qq.com/cgi/cgi-bin/longhubang/stockDetail?&stockCode=%s'%i[0],timeout=(10,5)).text
                        break
                    except:
                        m = m+1
                        print('网络错误，正在重试')
                        time.sleep(1)
                        continue
                if m ==5:
                    continue
                for j in json.loads(share)['data']['detail']:
                    if j['date'] == date:
                        buy = j['buy']
                        sell = j['sell']
                        n = 0
                        mai = 0
                        for m in buy:
                            if '专用' in m[1]:
                                n = n+1
                                mai = mai + m[2]
                            elif m[1] in list(youzi.keys()):
                                n = n+1
                                mai = mai + m[2]
                            else:
                                pass
                        if n >= 2:
                            for g in sell:
                                if '专用' in g[1]:
                                    n = n-1
                                elif g[1] in list(youzi.keys()):
                                    n = n-1
                        if n >= 2:
                            if mai/sum([q[2] for q in buy]) >= 0.6:
                                profit = requests.get('https://data.gtimg.cn/flashdata/hushen/daily/21/%s.js'%json.loads(share)['data']['stockCode'],timeout=(10,5)).text
                                profit = profit.split('\\n\\\n')[1:-1]
                                for p in range(len(profit)-6):
                                    list_p = profit[p].split(' ')
                                    if list_p[0] == date_y:
                                        open_buy = float(profit[p+1].split(' ')[1])
                                        high_sell = max([float(profit[p+2].split(' ')[3]),float(profit[p+3].split(' ')[3]),float(profit[p+4].split(' ')[3]),float(profit[p+5].split(' ')[3])])
                                        yingli = str(round((high_sell - open_buy)*100/open_buy,2)) + '%'
                                        # print('#####################开盘买入价：',open_buy,'#####################卖出价',high_sell,'#####################')
                                dict_stock[json.loads(share)['data']['stockCode']+':'+date] = {'attention':n,'t':date,'p':yingli}
                                print(json.loads(share)['data']['stockCode']+':'+date,yingli,n)
                print(json.loads(share)['data']['stockName'],'完成',date)
                time.sleep(0.2)
    print(dict_stock)
    print('负收益：',len([i['p'] for i in list(dict_stock.values()) if i['p'][0]=='-']))
    print('正收益：',len([i['p'] for i in list(dict_stock.values()) if i['p'][0]!='-']))
    print('最高收益：',max([float(i['p'][:-1]) for i in list(dict_stock.values()) if i['p'][0]!='-']),'%')
    print('最低收益：',min([float(i['p'][:-1]) for i in list(dict_stock.values()) if i['p'][0]=='-']),'%')
    print('平均收益：',sum([float(i['p'][:-1]) for i in list(dict_stock.values())])/len(dict_stock),'%')
    print('成功率：',len([i['p'] for i in list(dict_stock.values()) if i['p'][0]!='-'])*100/len(dict_stock),'%')
    print('以上回测数据为2021年至今，回测买卖周期为5个交易日，即以周为单位的短线投资')

# xuangu()
# huice()
