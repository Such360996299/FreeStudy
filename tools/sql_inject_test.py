import MySQLdb

username = "' OR 1=1 #"
password = "xxx"
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="xxx", db="freestudy", charset="utf8")
cursor = conn.cursor()
sql = "select * from users_userprofile where username='{}' and password='{}'".format(username,password)
print(sql)
cursor.execute(sql)
for row in cursor.fetchall():
    print(row)

#1. 表单验证
#2. 查询用户的逻辑
#3. django的orm会对特殊字符转义, orm会确保用户输入数据的安全性
