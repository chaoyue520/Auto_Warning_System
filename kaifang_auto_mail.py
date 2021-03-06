#!/usr/bin/python
# -*- coding: UTF-8 -*-


import pandas as pd 
import numpy as np 
import time
import datetime
import os
import smtplib
import copy
from email.mime.text import MIMEText
from email.header import Header
from email.utils import COMMASPACE
import warnings

#忽略所有的warnings信息
warnings.filterwarnings('ignore')

# 定义时间变量
# time.strftime('%Y%m%d',time.localtime())
yesterday = datetime.date.today() - datetime.timedelta(days=1)
data_yest=yesterday.strftime('%Y%m%d')
xpath='./data'

###########################################################################################################################################
############################################################### 原始数据 ##################################################################

# 加载数据
# fangkuan_data=os.popen(" bash fangkuan_daily_report.sh")
# fangkuan_data=os.popen(" bash zaiku_daily_report.sh")
fangkuan_data=os.popen(""" hive -e "use jiwenchao;select * from fangkuan_daily_data"  """)

zaiku_data=os.popen(""" hive -e "use jiwenchao;select * from zaiku_daily_data"  """)

# 初始化列表
fangkuan_data_v1=[]
for line in fangkuan_data.readlines():
    fangkuan_data_v1.append(line.strip().split('\t'))


fangkuan_data.close()

# 初始化列表
zaiku_data_v1=[]
for line in zaiku_data.readlines():
    zaiku_data_v1.append(line.strip().split('\t'))


zaiku_data.close()

# 原始数据
fk_data_set=pd.DataFrame(fangkuan_data_v1,columns=['transaction_id','entrolment_date','initialAmount','bid','odu_days_cls'])
zk_data_set=pd.DataFrame(zaiku_data_v1,columns=['bid','entrolment_date','outstd_trxn_amount','odu_days_cls'])

fk_data_set.shape
zk_data_set.shape

#去个重 
zk_data_set=zk_data_set[zk_data_set.duplicated()==False]


##################################################################################################################################################
############################################################### 表1：指标 ########################################################################

# Total_Act-放款账户
fk_bid_cnt=fk_data_set.groupby(['entrolment_date'])['bid'].count()
Total_Act=pd.DataFrame(fk_bid_cnt)
Total_Act=Total_Act[(Total_Act.index!='NULL') & (Total_Act.index!=0)]  #主表索引删除异常值
Total_Act=Total_Act.bid.astype(int)

# Total Act With bal-在库帐户
zk_bid_cnt=zk_data_set.groupby(['entrolment_date'])['bid'].count()
Total_Act_With_bal=pd.DataFrame(zk_bid_cnt)
Total_Act_With_bal=Total_Act_With_bal.bid.astype(int)


# MTD Average Line-当月账户平均额度
fk_data_set=fk_data_set.replace('NULL',0)
fk_data_set['initialAmount']=fk_data_set['initialAmount'].astype(str).astype(float)
MTD_Sum=fk_data_set.groupby(['entrolment_date'])['initialAmount'].sum()
MTD_Avg=pd.DataFrame(MTD_Sum/fk_bid_cnt,columns=['avg_initialAmt'])
MTD_Avg=MTD_Avg[(MTD_Avg.index!='NULL') & (MTD_Avg.index!=0)]
MTD_Average_Line=MTD_Avg.where(MTD_Avg.notnull(),0).avg_initialAmt.astype(int)


# Balance-当前本金余额：在库余额
zk_data_set['outstd_trxn_amount']=zk_data_set['outstd_trxn_amount'].astype(str).astype(float)
Balance_Sum=zk_data_set.groupby(['entrolment_date'])['outstd_trxn_amount'].sum()/10000
Balance=pd.DataFrame(Balance_Sum)
Balance=Balance[(Balance.index!='NULL') & (Balance.index!=0)]
Balance=Balance.outstd_trxn_amount.astype(int)  # 以万为单位，并取整


# Limit Utilit%-额度使用率
Limit_Utilit=pd.DataFrame(Balance_Sum*10000/MTD_Sum,columns=['percent_used_amt'])
Limit_Utilit=Limit_Utilit[(Limit_Utilit.index!='NULL') & (Limit_Utilit.index!=0)]
Limit_Utilit=Limit_Utilit.percent_used_amt.apply(lambda x : format(x, '.2%'))
#Limit_Utilit[data_index.index!=0].round(decimals=2)


## 合并表1
data_index=pd.concat([Total_Act, Total_Act_With_bal,MTD_Average_Line,Balance,Limit_Utilit], axis=1, join_axes=[Total_Act.index])
data_index.columns=['Total Act-帐户','Total Act With bal-在库帐户','MTD Average Line-当月账户平均额度','Balance-当前本金余额(万)','Limit Utilit%-额度使用率']
data_index=data_index[(data_index.index!='NULL') & (data_index.index!=0)]
data_index_transform=data_index.T


# 本地存储
data_index_transform.to_csv(xpath+'/data_index_transform.txt',sep='\t',header=True,index=True)


##################################################################################################################################################
############################################################### 表2：在库账户逾期分类 ############################################################

# Account in bucket  在库账户数
zaiku_bid_cnt=zk_data_set.pivot_table(['bid'],index=['odu_days_cls'],columns=['entrolment_date'],aggfunc='count',dropna=True)
zaiku_bid_odus=zaiku_bid_cnt.where(zaiku_bid_cnt.notnull(),0).bid.astype(int)
zaiku_bid_odus.loc['Total Account']=zaiku_bid_odus.apply(lambda x : x.sum())

# 存储本地
zaiku_bid_odus.to_csv(xpath+'/zaiku_bid_odus.txt',sep='\t',header=True,index=True)


##################################################################################################################################################
############################################################### 表3：在库金额逾期分类 ############################################################

# Account in bucket  在库账户数
zk_data_set['outstd_trxn_amount']=zk_data_set['outstd_trxn_amount'].astype(str).astype(float)
zaiku_balance_odus=zk_data_set.pivot_table(['outstd_trxn_amount'],index=['odu_days_cls'],columns=['entrolment_date'],aggfunc='sum',dropna=True)
zaiku_balance_odus=zaiku_balance_odus/10000  # 金额单位设置为万
zaiku_balance_odus=zaiku_balance_odus.where(zaiku_balance_odus.notnull(),0)
zaiku_balance_odus.loc['Total Balance']=zaiku_balance_odus.apply(lambda x : x.sum())


# 深拷贝
zaiku_balance_odus_v1=copy.deepcopy(pd.DataFrame(zaiku_balance_odus))
zaiku_balance_odus_v1.columns=[chr(i) for i in range(97,97+zaiku_balance_odus_v1.shape[1])]


for col in zaiku_balance_odus_v1.columns:
    zaiku_balance_odus_v1[col]=zaiku_balance_odus_v1[col].apply(lambda x : format(x, '.1f'))

zaiku_balance_odus_v1.columns=list(zaiku_balance_odus.outstd_trxn_amount.columns)

zaiku_balance_odus=zaiku_balance_odus_v1


# 存储本地
zaiku_balance_odus.to_csv(xpath+'/zaiku_balance_odus.txt',sep='\t',header=True,index=True)


##################################################################################################################################################
############################################################### 表4：账户逾期率 ##################################################################

zk_bid_cnt=zk_data_set.pivot_table(['bid'],index=['odu_days_cls'],columns=['entrolment_date'],aggfunc='count',dropna=True)
zk_bid_cnt=zk_bid_cnt.where(zk_bid_cnt.notnull(),0).bid.astype(float)
zk_bid_cnt.loc['Total_Account_ratio']=zk_bid_cnt.apply(lambda x : x.sum())
Bid_odus_ratio=copy.deepcopy(zk_bid_cnt)

# 计算账户逾期率
for i in range(zk_bid_cnt.shape[0]):
    for j in range(zk_bid_cnt.shape[1]):
        Bid_odus_ratio.iloc[i,j]=zk_bid_cnt.iloc[i,j]/zk_bid_cnt.iloc[zk_bid_cnt.shape[0]-1,j]


for i in range(Bid_odus_ratio.shape[1]):
    Bid_odus_ratio.iloc[zk_bid_cnt.shape[0]-1,i]=1-Bid_odus_ratio.iloc[0,i]


Bid_odus_ratio_v1=copy.deepcopy(pd.DataFrame(Bid_odus_ratio))
Bid_odus_ratio_v1.columns=[chr(i) for i in range(97,97+Bid_odus_ratio_v1.shape[1])]

for col in Bid_odus_ratio_v1.columns:
    Bid_odus_ratio_v1[col]=Bid_odus_ratio_v1[col].apply(lambda x : format(x, '.2%'))

Bid_odus_ratio_v1.columns=list(zk_bid_cnt.columns)

Bid_odus_ratio=Bid_odus_ratio_v1



# 存储本地
Bid_odus_ratio.to_csv(xpath+'/Bid_odus_ratio.txt',sep='\t',header=True,index=True)



##################################################################################################################################################
############################################################### 表5：金额逾期率 ##################################################################
zaiku_balance_odus=zk_data_set.pivot_table(['outstd_trxn_amount'],index=['odu_days_cls'],columns=['entrolment_date'],aggfunc='sum',dropna=True)
zaiku_balance_odus=zaiku_balance_odus.where(zaiku_balance_odus.notnull(),0).outstd_trxn_amount.astype(float)
zaiku_balance_odus.loc['Total_Balance_ratio']=zaiku_balance_odus.apply(lambda x : x.sum())
Banlance_odus_ratio=copy.deepcopy(zaiku_balance_odus)

# 计算账户逾期率
for i in range(zaiku_balance_odus.shape[0]):
    for j in range(zaiku_balance_odus.shape[1]):
        Banlance_odus_ratio.iloc[i,j]=zaiku_balance_odus.iloc[i,j]/zaiku_balance_odus.iloc[zaiku_balance_odus.shape[0]-1,j]


for i in range(Banlance_odus_ratio.shape[1]):
    Banlance_odus_ratio.iloc[zaiku_balance_odus.shape[0]-1,i]=1-Banlance_odus_ratio.iloc[0,i]


Banlance_odus_ratio_v1=copy.deepcopy(pd.DataFrame(Banlance_odus_ratio))
Banlance_odus_ratio_v1.columns=[chr(i) for i in range(97,97+Banlance_odus_ratio_v1.shape[1])]

for col in Banlance_odus_ratio_v1.columns:
    Banlance_odus_ratio_v1[col]=Banlance_odus_ratio_v1[col].apply(lambda x : format(x, '.2%'))

Banlance_odus_ratio_v1.columns=list(Banlance_odus_ratio.columns)

Banlance_odus_ratio=Banlance_odus_ratio_v1

# 存储本地
Banlance_odus_ratio.to_csv(xpath+'/Banlance_odus_ratio.txt',sep='\t',header=True,index=True)


##################################################################################################################################################
############################################################### 表6：Flow Rates ##################################################################

# Flow Rates (amt)
zaiku_balance_odus=zk_data_set.pivot_table(['outstd_trxn_amount'],index=['odu_days_cls'],columns=['entrolment_date'],aggfunc='sum',dropna=True)
zaiku_balance_odus=zaiku_balance_odus.where(zaiku_balance_odus.notnull(),0).outstd_trxn_amount.astype(float)

Flow_Rates=copy.deepcopy(zaiku_balance_odus)

for i in range(zaiku_balance_odus.shape[0]):
    for j in range(zaiku_balance_odus.shape[1]):
        if j>=1 and i>=1:
            Flow_Rates.iloc[i,j]=zaiku_balance_odus.iloc[i,j]/zaiku_balance_odus.iloc[i-1,j-1]


# 替换无效值，替换滚动率大于100%的值
Flow_Rates_sub=Flow_Rates.where(Flow_Rates.notnull(),0).replace('inf',0)

# 百分比转化
Flow_Rates_sub_v1=copy.deepcopy(pd.DataFrame(Flow_Rates_sub))
Flow_Rates_sub_v1[Flow_Rates_sub_v1>=1]=1
Flow_Rates_sub_v1.columns=[chr(i) for i in range(97,97+Banlance_odus_ratio_v1.shape[1])]

for col in Flow_Rates_sub_v1.columns:
    Flow_Rates_sub_v1[col]=Flow_Rates_sub_v1[col].apply(lambda x : format(x, '.2%'))


Flow_Rates_sub_v1.columns=list(Flow_Rates_sub.columns)


#5月份没有滚动率，M0没有滚动率
Flow_Rates_sub_v1[['2017-05']]='-'
Flow_Rates_sub_v1.iloc[0,:]='-'

Flow_Rates_sub=Flow_Rates_sub_v1


# 修改数据框行索引 index
for i in range(Flow_Rates_sub.shape[0]):
    if i==0:
        Flow_Rates_sub.index.values[i]=str('M')+str(i)
    elif i < Flow_Rates_sub.shape[0]-1:
        Flow_Rates_sub.index.values[i]=str('M')+str(i-1)+str('->')+str('M')+str(i)
    else:
        Flow_Rates_sub.index.values[i]=str('M')+str(i-1)+str('->')+str('M')+str(i)+str('+')


# 存储本地
Flow_Rates_sub.to_csv(xpath+'/Flow_Rates_sub.txt',sep='\t',header=True,index=True)

##################################################################################################################################################
############################################################### 设置邮件内容 #####################################################################

# 设置邮件正文
a=os.popen(("""
echo "<p><strong>Hi,all</strong></p>" 
echo "<p><strong> 以下是截止到%s开放客群资产质量表统计指标:</strong></p>" 
echo "<p><strong> 说明: 开放客群包含名单类型(whiteListType)为00,07,32,50,51(已排除内部员工)，且用信时间为20170501起，截止到%s的用户 :</strong></p>" 

cat ./mail_content.html

echo "<p><strong> 一. 指标 </strong></p>" 
echo "<table border=1>" 
cat ./data/data_index_transform.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"


echo "<p><strong> 二. Account in bucket  在库笔数 </strong></p>" 
echo "<table border=1>" 
cat ./data/zaiku_bid_odus.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"

echo "<p><strong> 三. Balance in bucket 在库金额(万) </strong></p>" 
echo "<table border=1>" 
cat ./zaiku_balance_odus.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"

echo "<p><strong> 四. Total Account percentage 在库账户逾期率 </strong></p>" 
echo "<table border=1>" 
cat ./Bid_odus_ratio.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"

echo "<p><strong> 五. Total balance percentage 金额逾期率 </strong></p>" 
echo "<table border=1>" 
cat ./Banlance_odus_ratio.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"

echo "<p><strong> 六. Flow Rates(amt) : 金额滚动率 </strong></p>" 
echo "<table border=1>" 
cat ./Flow_Rates_sub.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
echo "</table>"

""")%(data_yest,data_yest))


#发件人，收件人，邮件主题
FROM = 'xxx@baidu.com'
TO=['xxx@baidu.com','xxx@baidu.com']
CC=['xxx@baidu.com']   #抄送人
subject = " 开放客群资产质量监控报表 - %s " %data_yest

# 
simi_html=a.read()
message = MIMEText(simi_html, 'html', 'utf-8')
message['Subject'] = Header(subject, 'utf-8')
message['From'] = FROM
message['TO'] = COMMASPACE.join(TO)
message['CC'] = COMMASPACE.join(CC)

# 发送邮件
try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(FROM, TO, message.as_string())
    print "Bingo"
except smtplib.SMTPException:
    print "Oh~No"




