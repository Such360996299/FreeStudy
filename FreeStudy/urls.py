"""FreeStudy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

import xadmin

from django.views.static import serve

from apps.users.views import LoginView, LogoutView, DynamicLoginView, RegisterView
# from apps.users.views import ActiveUserView,ForgetPwdView
from apps.users.views import SendRegEmailView,SendLogEmailView,SendForEmailView
from FreeStudy.settings import MEDIA_ROOT
from apps.operations.views import IndexView
from apps.organizations.views import TeacherListView, TeacherDetailView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),#注册
    path('d_login/', DynamicLoginView.as_view(), name="d_login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^send_reg_email/', csrf_exempt(SendRegEmailView.as_view()), name="send_reg_email"),#邮箱注册验证码发送
    url(r'^send_log_email/', csrf_exempt(SendLogEmailView.as_view()), name="send_log_email"),#邮箱登陆验证码发送
    # url(r'^send_for_email/', csrf_exempt(SendForEmailView.as_view()), name="send_for_email"),#账号忘记邮箱验证码发送
    path('index/', IndexView.as_view(), name="index"),
    # url(r'^forgetpwd/$', ForgetPwdView.as_view(),name="forget_pwd"),#r'^forgetpwd/$'中的forgetpwd


    #配置上传文件的访问url
    url(r'^media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve, {"document_root":STATIC_ROOT}),

    #机构相关页面
    url(r'^org/', include(('apps.organizations.urls', "organizations"), namespace="org")),

    #机构相关页面
    url(r'^course/', include(('apps.courses.urls', "courses"), namespace="course")),

    #讲师相关页面
    url(r'^teachers/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),

    #用户相关操作
    url(r'^op/', include(('apps.operations.urls', "operations"), namespace="op")),

    #个人中心
    url(r'^users/', include(('apps.users.urls', "users"), namespace="users")),

    #配置富文本相关的url
    url(r'^ueditor/',include('DjangoUeditor.urls' )),
]

#1. CBV(class base view) FBV(function base view)

#编写一个view的几个步骤
"""
1. view代码
2. 配置url
3. 修改html页面中相关的地址
"""
