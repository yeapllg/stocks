#!/usr/bin/python3
# -*- coding:utf-8 -*-
'''
神奇九转
'''
import pandas as pd
import numpy as np
import os

#仅对近一个月（即20个交易日）的数据进行分析，因为九转最多也就13个交易日，分析近一个月是为了回测数据
#data文件夹里的数据请用data_163脚本自动生成

#选股
def dress():
    list_code = []
    for j in os.listdir('data'):
        print(j,'开始')
        data = pd.read_csv("data/%s"%j)
        data = data.iloc[:20]
        data_close = data.close.values
        for i in range(len(data_close)-4):
            for k in range(9):
                if i+k+4<len(data_close):
                    if data_close[i+k] < data_close[i+k+4]:
                        if k == 8 and i==0:
                            print(j,data.trade_date.values[i],'进入观察期')
                            list_code.append(j[:-4])
                        continue
                    else:
                        break

        print(j,'完成')
    print(set(list_code))
            
#回测，主要看出现九转买入信号候，第二天以开盘价买入，然后在接下来的5个交易日内高点卖出，看是否亏损和收益多大
def back_testing():
    list_code = {}
    for j in os.listdir('data'):
        print(j,'开始')
        data = pd.read_csv("data/%s"%j)
        data = data.iloc[:20]
        data_close = data.close.values
        data_high = data.high.values
        data_open = data.open.values
        for i in range(len(data_close)-4):
            for k in range(9):
                if i+k+4<len(data_close):
                    if data_close[i+k] < data_close[i+k+4]:
                        if k == 8 and i>=6:
                            buy = data_open[i-1]
                            sell = max(data_high[i-6:i-2])   #出现买入信号候第二天以开盘价买入，看一周之内是否有合适卖出机会
                            list_code[j[:-4]] = str(round((sell - buy)*100/buy,2))+'%'
                        continue
                    else:
                        break

        print(j,'完成')
    print(list_code)
    print('最大收益:',str(max([float(i[:-1]) for i in list(list_code.values())]))+'%')
    print('最小收益:',str(min([float(i[:-1]) for i in list(list_code.values())]))+'%')
    print('平均收益:',str(round(sum([float(i[:-1]) for i in list(list_code.values())])/len(list(list_code.values())),2))+'%')
    print('正收益：',len([float(i[:-1]) for i in list(list_code.values()) if i[0]!='-']))
    print('负收益：',len([float(i[:-1]) for i in list(list_code.values()) if i[0]=='-']))

#back_testing()
#dress()
    
