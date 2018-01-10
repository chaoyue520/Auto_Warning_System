#!/bin/bash

date_yesterday=`date -d "1 days ago" +%Y%m%d`
date_yesterday_unix=`date -d "$date_yesterday" +%s`
date_10_ago=`date -d "10 days ago" +%Y%m%d`

echo $date_yesterday
echo $date_10_ago

cd ./auto_mail

hive -e "

SELECT dt
---Total
      ,count(distinct bid) AS Total_bid
      ,count(distinct case when y_tag_v2=1 then bid else null end) AS Total_fraud_bid
      ,count(distinct case when y_tag_v2=2 then bid else null end) AS Total_credit_bid
      ,count(distinct case when y_tag_v2=3 then bid else null end) AS Total_good_bid
      ,count(distinct case when y_tag_v2=4 then bid else null end) AS Total_other_bid

---白名单
      ,count(distinct case when white_type =1 then bid else null end) AS White_total_bid
      ,count(distinct case when white_type =1 and y_tag_v2=1 then bid else null end) AS White_total_fraud_bid
      ,count(distinct case when white_type =1 and  y_tag_v2=2 then bid else null end) AS White_total_credit_bid
      ,count(distinct case when white_type =1 and  y_tag_v2=3 then bid else null end) AS White_total_good_bid
      ,count(distinct case when white_type =1 and  y_tag_v2=4 then bid else null end) AS White_total_other_bid

---非白名单
      ,count(distinct case when white_type =0 then bid else null end) AS NonWhite_total_bid
      ,count(distinct case when white_type =0 and y_tag_v2=1 then bid else null end) AS NonWhite_total_fraud_bid
      ,count(distinct case when white_type =0 and  y_tag_v2=2 then bid else null end) AS NonWhite_total_credit_bid
      ,count(distinct case when white_type =0 and  y_tag_v2=3 then bid else null end) AS NonWhite_total_good_bid
      ,count(distinct case when white_type =0 and  y_tag_v2=4 then bid else null end) AS NonWhite_total_other_bid

FROM  jxj_y_tag_v2
WHERE dt>=$date_10_ago and dt<=$date_yesterday and bid is not null and bid!='-9999'
group by dt
order by dt desc
limit 20000;">result_v1.txt

a=`cat result_v1.txt| wc -l`

if [ $a -ge 1 ];then
date_Y=`date -d "1 days ago" +%Y-%m-%d`
echo "<p><strong>Hi,all</strong></p>" > simi_a.html
echo "<p><strong> $date_Y 信贷Y标签分类表如下所示.</strong></p>" >> simi_a.html
echo "<p>一、信贷Y标签分类分布</p>" >> simi_a.html
echo "<table border=1>" >> simi_a.html
echo "<tr><td align=center rowspan="2">日期</td><td align=center colspan="5">汇总</td><td align=center colspan="5">白名单客群</td><td align=center colspan="5">非白名单客群</td></tr>" >> simi_a.html
echo "<tr><td align=center>total_bid</td><td align=center>fraud_bid</td><td align=center>credit_bid</td><td align=center>good_bid</td><td align=center>other_bid</td>
          <td align=center>white_bid</td><td align=center>fraud_bid</td><td align=center>credit_bid</td><td align=center>good_bid</td><td align=center>other_bid</td>
          <td align=center>nonwhite_bid</td><td align=center>fraud_bid</td><td align=center>credit_bid</td><td align=center>good_bid</td><td align=center>other_bid</td></tr>" >> simi_a.html
cat result_v1.txt|tr -d " "|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '$1!=""{print a$1b$2b$3b$4b$5b$6b$7b$8b$9b$10b$11b$12b$13b$14b$15b$16c}' >> simi_a.html
echo "</table>" >> simi_a.html

echo "<p>二、各类标签占总人群比例(分母为total_bid)</p>" >> simi_a.html
echo "<table border=1>" >> simi_a.html
echo "<tr><td align=center rowspan="2">日期</td><td align=center colspan="5">汇总</td><td align=center colspan="5">白名单客群</td><td align=center colspan="5">非白名单客群</td></tr>" >> simi_a.html
echo "<tr><td align=center>total_bid</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td>
          <td align=center>white_ratio</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td>
          <td align=center>nonwhite_ratio</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td></tr>" >> simi_a.html
python ./fenzu_percent.py
cat result_v2.txt|tr -d " "|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' 'NR!="1" && $1!=""{print a$1b$2b$3b$4b$5b$6b$7b$8b$9b$10b$11b$12b$13b$14b$15b$16c}' >> simi_a.html
echo "</table>" >> simi_a.html


echo "<p>三、各类标签占各自人群比例(分母分别为total_bid,white_bid,nonwhite_bid)</p>" >> simi_a.html
echo "<table border=1>" >> simi_a.html
echo "<tr><td align=center rowspan="2">日期</td><td align=center colspan="5">汇总</td><td align=center colspan="5">白名单客群</td><td align=center colspan="5">非白名单客群</td></tr>" >> simi_a.html
echo "<tr><td align=center>total_bid</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td>
          <td align=center>white_bid</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td>
          <td align=center>nonwhite_bid</td><td align=center>fraud_ratio</td><td align=center>credit_ratio</td><td align=center>good_ratio</td><td align=center>other_ratio</td></tr>" >> simi_a.html
cat result_v3.txt|tr -d " "|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' 'NR!="1" && $1!=""{print a$1b$2b$3b$4b$5b$6b$7b$8b$9b$10b$11b$12b$13b$14b$15b$16c}' >> simi_a.html
echo "</table>" >> simi_a.html


MAIL='xxx@baidu.com'
to="xxx@baidu.com;x@baidu.com"



mutt $to -s "JXJ_Y_tag_monitor - 信贷Y标签分类监控 : $date_Y" -F ./.muttrc -e 'set content_type="text/html"' $MAIL < ./simi_a.html

else 
	echo "empty"
fi


