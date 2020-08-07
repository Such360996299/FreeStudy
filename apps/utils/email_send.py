# -*- coding: utf-8 -*
_author_ = 'such'
_date_ = '2020/3/1 17:09'

from apps.users.models import EmailVerifyRecord
from random import Random
from django.core.mail import send_mail
from FreeStudy.settings import EMAIL_FROM


#定义生成验证码字符函数
# def random_str(randomlength=8):
#     str = ''
#     chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
#     length = len(chars) - 1
#     random = Random() #调用Random方法，随机取数后取对应字符
#     for i in range(randomlength):
#         str+=chars[random.randint(0,length)]
#     return str
    #random.randint(a,b)用于生成一个指定范围内的整数。其中参数a是下限，参数b是上限，生成的随机数n: a <= n <= b。
    #print random.randint(12, 20)  #生成的随机数n: 12 <= n <= 20
    #print random.randint(20, 20)  #结果永远是20
    #print random.randint(20, 10)  #该语句是错误的。下限必须小于上限

#定义生成验证码【数字】
def random_str(randomlength=6):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random() #调用Random方法，随机取数后取对应字符
    for i in range(randomlength):
        str+=chars[random.randint(0,length)]
    return str

def send_register_email(code,email,send_type='register'):
    email_record = EmailVerifyRecord()
    # code = random_str(6)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save() #保存至数据库


    email_title = ''
    email_body = ''

    # if send_type == 'register':
    #     email_title = 'FreeStudy注册激活链接'
    #     email_body = '请点击下面的链接激活你的账号：http://127.0.0.1:8000/active/{0}'.format(code)
    #     send_status = send_mail(email_title,email_body,EMAIL_FROM,[email])
    #     if send_status:
    #         pass

    if send_type == 'register':
        email_title = 'FreeStudy注册验证码'
        email_body = '你的FreeStudy账号注册验证码:{0}。有效期30分钟,请尽快输入。如非本人操作，请忽略本邮件'.format(code)
        send_status = send_mail(email_title,email_body,EMAIL_FROM,[email])
        if send_status:
            return send_status

    # if send_type == 'forget':
    #     email_title = 'FreeStudy密码重置链接'
    #     email_body = '请点击下面的链接重置你的密码：http://127.0.0.1:8000/reset/{0}'.format(code)
    #     send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    #     if send_status:
    #         pass

    if send_type == 'login':
        email_title = 'FreeStudy登陆验证码'
        email_body = '你的FreeStudy账号登陆验证码:{0}。有效期15分钟,请尽快输入。如非本人操作，请忽略本邮件'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            return send_status


