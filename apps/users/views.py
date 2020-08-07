from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import redis
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, UploadImageForm
from apps.users.forms import UserInfoForm, ChangePwdForm
from apps.users.forms import RegisterGetForm, UpdateMobileForm,ForgetForm,RegisterPostForm
# from apps.utils.YunPian import send_single_sms
from apps.utils.random_str import generate_random
# from FreeStudy.settings import yp_apikey
from FreeStudy.settings import REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile,EmailVerifyRecord
from apps.operations.models import UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Course
from apps.utils.email_send import send_register_email


class CustomAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def message_nums(request):
    """
    Add media-related context variables to the context.
    """
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()}
    else:
        return {}


class MyMessageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        messages = UserMessage.objects.filter(user=request.user)
        current_page = "message"
        for message in messages:
            message.has_read = True
            message.save()

        # 对讲师数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(messages, per_page=1, request=request)
        messages = p.page(page)

        return render(request, "usercenter-message.html",{
            "messages":messages,
            "current_page":current_page
        })


class MyFavCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_course"
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            try:
                course = Course.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Course.DoesNotExist as e:
                pass
        return render(request, "usercenter-fav-course.html",{
            "course_list":course_list,
            "current_page":current_page
        })

class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_teacher"
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            org = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(org)
        return render(request, "usercenter-fav-teacher.html",{
            "teacher_list":teacher_list,
            "current_page":current_page
        })


class MyFavOrgView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfavorg"
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html",{
            "org_list":org_list,
            "current_page":current_page
        })


class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mycourse"
        # my_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html",{
            # "my_courses":my_courses,
            "current_page":current_page
        })


class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        mobile_form = UpdateMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            #已经存在的记录不能重复注册
            # if request.user.mobile == mobile:
            #     return JsonResponse({
            #         "mobile": "和当前号码一致"
            #     })
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({
                    "mobile":"该手机号码已经被占用"
                })
            user = request.user
            user.mobile = mobile
            user.username = mobile
            user.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(mobile_form.errors)
            # logout(request)


class ChangePwdView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            # pwd1 = request.POST.get("password1", "")
            # pwd2 = request.POST.get("password2", "")
            #
            # if pwd1 != pwd2:
            #     return JsonResponse({
            #         "status":"fail",
            #         "msg":"密码不一致"
            #     })
            pwd1 = request.POST.get("password1", "")
            user = request.user
            user.set_password(pwd1)
            user.save()
            # login(request, user)

            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(pwd_form.errors)


class UploadImageView(LoginRequiredMixin, View):
    login_url = "/login/"

    # def save_file(self, file):
    #     with open("C:/Users/Administrator/PycharmProjects/FreeStudy/media/head_image/uploaded.jpg", "wb") as f:
    #         for chunk in file.chunks():
    #             f.write(chunk)

    def post(self, request, *args, **kwargs):
        #处理用户上传的头像
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse({
                "status": "fail"
            })
        # files = request.FILES["image"]
        # self.save_file(files)

        #1. 如果同一个文件上传多次，相同名称的文件应该如何处理
        #2. 文件的保存路径应该写入到user
        #3. 还没有做表单验证


class UserInfoView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        return render(request, "usercenter-info.html",{
            "captcha_form":captcha_form,
            "current_page":current_page
        })

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(user_info_form.errors)

#短信注册
# class RegisterView(View):
#     def get(self, request, *args, **kwargs):
#         register_get_form = RegisterGetForm()
#         return render(request, "register.html", {
#             "register_get_form":register_get_form
#         })
#
#     def post(self, request, *args, **kwargs):
#         register_post_form = RegisterPostForm(request.POST)
#         if register_post_form.is_valid():
#             mobile = register_post_form.cleaned_data["mobile"]
#             password = register_post_form.cleaned_data["password"]
#             # 新建一个用户
#             user = UserProfile(username=mobile)
#             user.set_password(password)
#             user.mobile = mobile
#             user.save()
#             login(request, user)
#             return HttpResponseRedirect(reverse("index"))
#         else:
#             register_get_form = RegisterGetForm()
#             return render(request, "register.html", {
#                 "register_get_form":register_get_form,
#                 "register_post_form": register_post_form
#             })


#邮箱激活链接注册
# class RegisterView(View):
#     def get(self,request):
#         register_form = RegisterGetForm()
#         return render(request, "register.html", {'register_form':register_form})
#
#     def post(self,request):
#         register_form = RegisterGetForm(request.POST)
#         if register_form.is_valid():
#             pass_word = request.POST.get('password', '')
#             user_name = request.POST.get('email', '')
#             if UserProfile.objects.filter(email=user_name):
#                 return render(request, "register.html",{'register_form':register_form,"msg":'用户已经存在'})
#             # user_profile = UserProfile()
#             # user_profile.nick_name = user_name
#             user_profile = UserProfile.objects.create_user(username=user_name,password=pass_word,email=user_name)
#             #注意：使用create_user会在auth_user表新建数据！利于authenticate检测！
#             user_profile.is_active = False  #表示账号未激活 注意！设置此项会导致authenticate总是None！
#             # user_profile.password = make_password(pass_word) #对密码的明文加密
#             user_profile.save()
#             send_register_email(user_name,'register')
#             return render(request, 'login.html')
#         else:
#             return render(request, "register.html",{'register_form':register_form})
#注意else部分！否则会出现The view users.views.RegisterView didn't return an HttpResponse object！


#邮箱验证码注册(关联注册并登陆button）
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        banners = Banner.objects.all()[:3]
        return render(request, "register.html", {
            "register_get_form":register_get_form,
            "banners":banners
        })

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        if register_post_form.is_valid():
            email = register_post_form.cleaned_data["email"]
            password = register_post_form.cleaned_data["password"]
            # 新建一个用户
            user = UserProfile(username=email)  #username必须唯一，比如如果数据库存在该username，就会出现无法插入数据库记录错误。
            user.set_password(password)
            user.email = email
            user.save()
            login(request, user)
            new_message = "欢迎使用FreeStudy，祝您学习愉快！"
            messages = UserMessage()
            messages.user = request.user
            messages.message = new_message
            messages.save()
            return HttpResponseRedirect(reverse("index")) #注册成功返回主页
        else:
            register_get_form = RegisterGetForm()
            return render(request, "register.html", {
                "register_get_form":register_get_form,
                "register_post_form": register_post_form
            })

#短信动态登陆
# class DynamicLoginView(View):
#     def get(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return HttpResponseRedirect(reverse("index"))
#         next = request.GET.get("next", "")
#         login_form = DynamicLoginForm()
#         banners = Banner.objects.all()[:3]
#         return render(request, "login.html",{
#             "login_form":login_form,
#             "next":next,
#             "banners":banners
#         })
#
#     def post(self, request, *args, **kwargs):
#         login_form = DynamicLoginPostForm(request.POST)
#         dynamic_login = True
#         banners = Banner.objects.all()[:3]
#         if login_form.is_valid():
#             #没有注册账号依然可以登录
#             mobile = login_form.cleaned_data["mobile"]
#             existed_users = UserProfile.objects.filter(mobile=mobile)
#             if existed_users:
#                 user = existed_users[0]
#             else:
#                 #新建一个用户
#                 user = UserProfile(username=mobile)
#                 password = generate_random(10, 2)
#                 user.set_password(password)
#                 user.mobile = mobile
#                 user.save()
#             login(request, user)
#             next = request.GET.get("next", "")
#             if next:
#                 return HttpResponseRedirect(next)
#             return HttpResponseRedirect(reverse("index"))
#         else:
#             d_form = DynamicLoginForm()
#             return render(request, "login.html", {"login_form": login_form,
#                                                   "d_form": d_form,
#                                                   "banners":banners,
#                                                   "dynamic_login":dynamic_login})


#邮箱动态登陆
class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        banners = Banner.objects.all()[:3]
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
            "banners":banners
        })

    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():#账号符合表单结构（forms中进行验证码匹配）
            #没有注册账号依然可以登录
            email = login_form.cleaned_data["email"]
            existed_users = UserProfile.objects.filter(email=email)#寻找数据库中该邮箱用户
            if existed_users:#如果账号存在
                user = existed_users[0]
            else:
                #新建一个用户
                user = UserProfile(username=email)
                password = generate_random(10, 2)
                user.set_password(password)
                user.email = email
                user.save()
            login(request, user)#登陆
            next = request.GET.get("next", "")
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse("index"))
        else:
            d_form = DynamicLoginForm()
            return render(request, "login.html", {"login_form": login_form,
                                                  "d_form": d_form,
                                                  "banners":banners,
                                                  "dynamic_login":dynamic_login})



#短信验证码发送
# class SendSmsView(View):
#     def post(self, request, *args, **kwargs):
#         send_sms_form = DynamicLoginForm(request.POST)
#         re_dict = {}
#         if send_sms_form.is_valid():
#             mobile = send_sms_form.cleaned_data["mobile"]
#             #随机生成数字验证码
#             code = generate_random(4, 0)
#             re_json = send_single_sms(yp_apikey,code ,mobile=mobile)
#             if re_json["code"] == 0:
#                 re_dict["status"] = "success"
#                 r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
#                 r.set(str(mobile), code)
#                 r.expire(str(mobile), 60*5) #设置验证码五分钟过期
#             else:
#                 re_dict["msg"] = re_json["msg"]
#         else:
#             for key, value in send_sms_form.errors.items():
#                 re_dict[key] = value[0]
#
#         return JsonResponse(re_dict)

#邮箱注册验证码发送(关联发送验证码button）
class SendRegEmailView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)#遵循从froms表中的DynamicLoginForm返回数据的格式
        re_dict = {}
        if send_sms_form.is_valid():
            email = send_sms_form.cleaned_data["email"]
            #随机生成数字验证码
            code = generate_random(6, 0)#6位数字
            re_json = send_register_email(code,email=email,send_type='register')#发送邮件
            if re_json:#发送成功时
                re_dict["status"] = "success" #设置status状态，便于js处理控件样式变化
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)#连接redis（需要终端开启redis）
                r.set(str(email), code)#redis中建立键值对,储存邮箱验证码信息
                r.expire(str(email), 60*30) #设置验证码30分钟过期
            else:
                re_dict["msg"] = re_json #发送失败则返回错误信息
        else:
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)#返回json至js处理

#邮箱登陆验证码发送
class SendLogEmailView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)#遵循从froms表中的DynamicLoginForm返回数据的格式
        re_dict = {}
        if send_sms_form.is_valid():
            email = send_sms_form.cleaned_data["email"]
            #随机生成数字验证码
            code = generate_random(6, 0)#6位数字
            re_json = send_register_email(code,email=email,send_type='login')#发送邮件
            if re_json:#发送成功时
                re_dict["status"] = "success" #设置status状态，便于js处理控件样式变化
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)#连接redis（需要终端开启redis）
                r.set(str(email), code)#redis中建立键值对,储存邮箱验证码信息
                r.expire(str(email), 60*15) #设置验证码30分钟过期
            else:
                re_dict["msg"] = re_json #发送失败则返回错误信息
        else:
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)#返回json至js处理

#账号忘记邮箱验证码发送
class SendForEmailView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)#遵循从froms表中的DynamicLoginForm返回数据的格式
        re_dict = {}
        if send_sms_form.is_valid():
            email = send_sms_form.cleaned_data["email"]
            #随机生成数字验证码
            code = generate_random(6, 0)#6位数字
            re_json = send_register_email(code,email=email,send_type='forget')#发送邮件
            if re_json:#发送成功时
                re_dict["status"] = "success" #设置status状态，便于js处理控件样式变化
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)#连接redis（需要终端开启redis）
                r.set(str(email), code)#redis中建立键值对,储存邮箱验证码信息
                r.expire(str(email), 60*30) #设置验证码30分钟过期
            else:
                re_dict["msg"] = re_json #发送失败则返回错误信息
        else:
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)#返回json至js处理



class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        banners = Banner.objects.all()[:3]
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
            "banners":banners
        })

    def post(self, request, *args, **kwargs):
        #表单验证
        login_form = LoginForm(request.POST)
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():
            #用于通过用户和密码查询用户是否存在
            user_name = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=user_name, password=password)
            #1. 通过用户名查询到用户
            #2. 需要先加密再通过加密之后的密码查询
            # user = UserProfile.objects.get(username=user_name, password=password)
            if user is not None:
                #查询到用户
                login(request, user)
                #登录成功之后应该怎么返回页面
                next = request.GET.get("next", "")
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse("index"))
            else:
                #未查询到用户
                return render(request, "login.html", {"msg":"用户名或密码错误", "login_form": login_form, "banners":banners})
        else:
            return render(request, "login.html", {"login_form": login_form,
                                                  "banners":banners})


# class ForgetPwdView(View):
#     def get(self,request):
#         forget_form = ForgetForm()
#         return render(request,'forgetpwd.html',{"forget_form":forget_form})
#
#
#     def post(self,request):
#         forget_form = ForgetForm(request.POST)
#         if forget_form.is_valid():
#             email = request.POST.get('email','')
#             if UserProfile.objects.filter(email=email):
#                 send_register_email(email, 'forget')
#                 return render(request, 'send_success.html')
#             else:return render(request, "forgetpwd.html",{'forget_form':forget_form,"msg":'用户不存在'})
#         else:
#             return render(request,'forgetpwd.html',{"forget_form":forget_form})

#验证数据库的验证码与访问邮箱链接地址是否匹配！
# class ActiveUserView(View):
#     def get(self,request,active_code):
#         all_recode = EmailVerifyRecord.objects.filter(code=active_code)
#         if all_recode:
#             for recode in all_recode:
#                 email = recode.email
#                 user = UserProfile.objects.get(email=email) #注意是User!即在auth_user表下比对数据!方便下一步进行修改user表的is_active状态!
#                 user.is_active = True
#                 user.save()
#             return render(request, 'login.html')
#         else:return render(request, 'active_fail.html')