#!/bin/bash
b=1
while [ $b -eq 1 ]
do

#设置自动化时间
date_f=`date --date "360 minutes ago" "+%H"`
date_e=`date --date "370 minutes ago" "+%H"`
date_g=`date --date "360 minutes ago" "+%Y%m%d"`
date_t=`date --date "360 minutes ago" "+%Y%m%d%H%M%S"`
date_y=`date --date "370 minutes ago" "+%Y%m%d%H%M%S"`

echo $date_f $date_e $date_g $date_t $date_y

# load_data
hive -e "
set hive.cli.print.header=true;
select t2.userid
       ,t2.cardmobile
       ,t2.bindmobile
       ,t2.occurtime
       ,t2.goodsname
       ,t2.devicefinger
       ,t2.payip
       ,t2.cardno
from risk.rcs_event
where dt>='$date_g' and hour>='$date_e' and hour<='$date_f';
         " > load_data.txt


# 定时发送
bash mail_content.sh

# 当满足一定条件的时候发送
bash mail_content_if_then.sh