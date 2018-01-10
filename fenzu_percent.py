#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import copy
import warnings

warnings.filterwarnings('ignore')

# load data
data=pd.read_table('result_v1.txt'
                   ,sep='\t'
                   ,header=None
                   ,names=['dt','total_bid','fraud_cnt','credit_cnt','good_cnt','other_cnt',\
                           'white_total_bid','white_fraud_cnt','white_credit_cnt','white_good_cnt','white_other_cnt',\
                           'nonwhite_total_bid','nonwhite_fraud_cnt','nonwhite_credit_cnt','nonwhite_good_cnt','nonwhite_other_cnt'])

# 计算占比
def ratio(input_data):
    output_data=copy.deepcopy(input_data)
    n=output_data.shape[0]
    for col in list(output_data.columns):
        for i in range(n):
            if col=='dt':
                output_data['dt'][i]=input_data.iloc[i][0]
            else :
                output_data[col][i]=str(round(100.0*input_data[col][i]/input_data.iloc[:,1][i],2)) + '%'
    return output_data


# 输出Total占比
v0=ratio(data)
v0=v0.drop(['dt','total_bid'],axis=1)
v0=pd.concat([data['dt'],data['total_bid'],v0],axis=1)
v0.to_csv('result_v2.txt',sep='\t',header=True,index=False)

# 表三
data_total=data[['dt','total_bid','fraud_cnt','credit_cnt','good_cnt','other_cnt']]
v1=ratio(data_total)
v1=v1.drop(['dt','total_bid'],axis=1)
v1=pd.concat([data_total['dt'],data_total['total_bid'],v1],axis=1)

data_white=data[['dt','white_total_bid','white_fraud_cnt','white_credit_cnt','white_good_cnt','white_other_cnt']]
v2=ratio(data_white)
v2=v2.drop(['dt','white_total_bid'],axis=1)
v2=pd.concat([data_white['white_total_bid'],v2],axis=1)

data_nonwhite=data[['dt','nonwhite_total_bid','nonwhite_fraud_cnt','nonwhite_credit_cnt','nonwhite_good_cnt','nonwhite_other_cnt']]
v3=ratio(data_nonwhite)
v3=v3.drop(['dt','nonwhite_total_bid'],axis=1)
v3=pd.concat([data_nonwhite['nonwhite_total_bid'],v3],axis=1)


# 输出各客群占比
v123=pd.concat([v1,v2,v3],axis=1)
v123.to_csv('result_v3.txt',sep='\t',header=True,index=False)

