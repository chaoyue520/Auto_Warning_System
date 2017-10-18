#!/bin/bash
date_a=`date "+%Y-%m-%d"`

a=`cat load_data.txt|wc -l`

# 当条件大于阈值的时候才出发邮件
if [ $a -ge 2 ];then
echo "<p><strong>Hi,all</strong></p>" > simi_a.html
echo "<p><strong> $date_a 测试表 .</strong></p>" >> simi_a.html
echo "<p>一、table_name_v1</p>" >> simi_a.html
echo "<table border=1>" >> simi_a.html
echo "<tr><td align=center>日期</td><td align=center>col_1</td><td align=center>col_2</td><td align=center>col_3</td><td align=center>col_4</td><td align=center>col_5</td><td align=center>col_6</td><td align=center>col_7</td></tr>" >> simi_a.html
cat load_data.txt|grep -v "rows"|tr -d " "|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'|' 'NR != "1" && NR != "2" && $1 != ""{print a$1b$2b$3b$4b$5b$6b$7b$8c}' >> simi_a.html
echo "</table>" >> simi_a.html

echo "<p>二、table_name_v2</p>" >> simi_a.html
echo "<table border=1>" >> simi_a.html
echo "<tr><td align=center>日期</td><td align=center>col_1</td><td align=center>col_2</td><td align=center>col_3</td><td align=center>col_4</td><td align=center>col_5</td><td align=center>col_6</td><td align=center>col_7</td><td align=center>col_8</td><td align=center>col_9</td></tr>" >> simi_a.html
cat load_data.txt|grep -v "rows"|tr -d " "|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'|' 'NR != "1" && NR != "2" && $1 != ""{print a$1b$2b$3b$4b$5b$6b$7b$8b$9b$10c}' >> simi_a.html
echo "</table>" >> simi_a.html

# 发件人
MAIL='xxx@xx.com' 
mutt -s "mail_subject - $date_a" -F ./.muttrc -e 'set content_type="text/html"' $MAIL < ./simi_a.html
else
  echo "empty"
fi
sleep 300s   #每5分钟遍历一次，并根据结果做判断是否发预警邮件
done


