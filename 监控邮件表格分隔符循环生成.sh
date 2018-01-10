#!/bin/bash

##### 背景
# 在使用html语言生成表格的时候，经常需要生成如下形式的数据，
# a$1b$2c，即开头使用a参数定义成<tr><td>,中间b定义成</td><td>，结尾c定义成</td></tr>
# 如果列数少，可以用遍历的方式实现，如下

cat xxx.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' 'NR!="1" && $1!=""{print a$1b$2b$3b$4b$5b$6b$7b$8b$9b$10b$11c}'

# 但是当列数很多的时候，比如要生成20列的数据，就比较麻烦，或者自动每个月或者每周多生成一列的时候，就不够自动化
# 如何解决这个问题呢，如下所示：
cat xxx.txt|awk -v a="<tr><td align=center>" -v b="</td><td align=center>" -v c="</td></tr>" -F'\t' '{printf a}''{for(i=1;i<=(NF-1);i++) printf $i b}''{printf $NF c}'
