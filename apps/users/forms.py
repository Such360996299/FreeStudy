from django import forms
from captcha.fields import CaptchaField
import redis

from FreeStudy.settings import REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile


class UpdateMobileForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data

class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

    def clean(self):
        pwd1 = self.cleaned_data["password1"]
        pwd2 = self.cleaned_data["password2"]

        if pwd1 != pwd2:
            raise forms.ValidationError("密码不一致")
        return self.cleaned_data


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name", "gender", "birthday", "address"]


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]


class RegisterGetForm(forms.Form):
    captcha = CaptchaField()

# 短信注册
# class RegisterPostForm(forms.Form):
#     mobile = forms.CharField(required=True, min_length=11, max_length=11)
#     code = forms.CharField(required=True, min_length=4, max_length=4)
#     password = forms.CharField(required=True)
#
#     def clean_mobile(self):
#         mobile = self.data.get("mobile")
#         # 验证手机号码是否已经注册
#         users = UserProfile.objects.filter(mobile=mobile)
#         if users:
#             raise forms.ValidationError("该手机号码已注册")
#         return mobile
#
#     def clean_code(self):
#         mobile = self.data.get("mobile")
#         code = self.data.get("code")
#         r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
#         redis_code = r.get(str(mobile))
#         if code != redis_code:
#             raise forms.ValidationError("验证码不正确")
#
#         return code

#邮箱注册
class RegisterPostForm(forms.Form):
    email = forms.EmailField(required=True)
    code = forms.CharField(required=True, min_length=6, max_length=6)
    password = forms.CharField(required=True)

    def clean_email(self):
        email = self.data.get("email")
        # 验证邮箱地址是否已经注册
        users = UserProfile.objects.filter(email=email)
        if users:
            raise forms.ValidationError("该邮箱地址已注册")
        return email

    def clean_code(self):
        email = self.data.get("email")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(email))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")

        return code

class LoginForm(forms.Form):
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)

class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid':u'验证码错误'})


class DynamicLoginForm(forms.Form):
    email = forms.EmailField(required=True) #注意邮箱使用EmailField
    captcha = CaptchaField()


class DynamicLoginPostForm(forms.Form):
    email = forms.EmailField(required=True) #注意邮箱使用EmailField
    code = forms.CharField(required=True, min_length=6, max_length=6) #设置邮箱验证码长度

    def clean_code(self):
        email = self.data.get("email")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(email))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data

    # def clean(self):
    #     mobile = self.cleaned_data["mobile"]
    #     code = self.cleaned_data["code"]
    #
    #     r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
    #     redis_code = r.get(str(mobile))
    #     if code != redis_code:
    #         raise forms.ValidationError("验证码不正确")
    #     return self.cleaned_data


