import xadmin

from apps.courses.models import Course, Lesson, Video, BannerCourse, CourseResource
from xadmin.layout import Fieldset, Main, Side, Row

class GlobalSettings(object):
    site_title = "FreeStudy后台管理系统"
    site_footer = "FreeStudy"
    # menu_style = "accordion"


class BaseSettings(object):
    enable_themes = True
    use_bootswatch = True


class LessonInline(object):
    model = Lesson
    # style = "tab"
    extra = 0
    exclude = ["add_time"]


class CourseResourceInline(object):
    model = CourseResource
    style = "tab"
    extra = 1


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_editable = ["degree", "desc"]


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_editable = ["degree", "desc"]

    def queryset(self):
        qs = super(BannerCourseAdmin,self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


from import_export import resources

class MyResource(resources.ModelResource):
    class Meta:
        model = Course
        # fields = ('name', 'description',)
        # exclude = ()


#固定的ip
#1. 本地的ip是一个动态分配的ip地址
#2. 数据包转发问题 scp
class NewCourseAdmin(object):
    import_export_args = {'import_resource_class': MyResource, 'export_resource_class': MyResource} #导入与导出文件
    list_display = ['name', 'desc', 'show_image', 'go_to', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_editable = ["degree", "desc"]
    readonly_fields = ["students", "add_time"]
    # exclude = ["click_nums", "fav_nums"]
    ordering = ["click_nums"]
    model_icon = 'fa fa-address-book'
    inlines = [LessonInline, CourseResourceInline]
    style_fields = {
        "detail":"ueditor"
    }

    def queryset(self):
        qs = super(NewCourseAdmin,self).queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                    Main(
                        Fieldset("讲师信息",
                                 'teacher','course_org',
                                 css_class='unsort no_title'
                                 ),
                        Fieldset("基本信息",
                                 'name', 'desc',
                                 Row('learn_times', 'degree'),
                                 Row('category', 'tag'),
                                 'youneed_know', 'teacher_tell', 'detail',
                                 ),
                    ),
                    Side(
                        Fieldset("访问信息",
                                 'fav_nums', 'click_nums', 'students','add_time'
                                 ),
                    ),
                    Side(
                        Fieldset("选择信息",
                                 'is_banner', 'is_classics'
                                 ),
                    )
            )
        return super(NewCourseAdmin, self).get_form_layout()

    def save_models(self):

        # 在保存课程的时候统计课程机构的课程数

        obj = self.new_obj

        obj.save()

        if obj.course_org is not None:

            course_org = obj.course_org

            course_org.course_nums = Course.objects.filter(course_org=course_org).count()

            course_org.save()




class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']
    form_layout = (
        Fieldset(None,
                 'course', 'name', 'learn_times'), #这里是要显示的选项
        Fieldset(None,
                 'teacher',**{"style":"display:None"} #隐藏该选项，使用默认值
                 )
    )

    def queryset(self):
        qs = super(LessonAdmin,self).queryset() #超级用户能直接获取全部内容
        if not self.request.user.is_superuser: #如果不是超级用户，就返回当前用户的内容
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

     # 需要重写instance_forms方法，此方法作用是生成表单实例
    def instance_forms(self):
        super(LessonAdmin,self).instance_forms()
        # 判断是否为新建操作，新建操作才会设置teacher的默认值
        if not self.org_obj:
            self.form_obj.initial['teacher'] = self.request.user.teacher #默认值是从当前用户获取对应的教师属性值


class VideoAdmin(object):
    list_display = ['course','lesson', 'name', 'add_time']
    search_fields = ['course','lesson', 'name']
    list_filter = ['course','lesson', 'name', 'add_time']
    style_fields = {
        "detail": "ueditor" #配置编辑器
    }
    form_layout = (
        Fieldset(None,
                 'course', 'lesson', 'name', 'learn_times', 'url', 'detail'),
        Fieldset(None,
                 'teacher', **{"style": "display:None"}
                 )
    )

    def queryset(self):
        qs = super(VideoAdmin, self).queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

        # 需要重写instance_forms方法，此方法作用是生成表单实例

    def instance_forms(self):
        super(VideoAdmin, self).instance_forms()
        # 判断是否为新建操作，新建操作才会设置teacher的默认值
        if not self.org_obj:
            self.form_obj.initial['teacher'] = self.request.user.teacher



class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'file', 'add_time']
    search_fields = ['course', 'name', 'file']
    list_filter = ['course', 'name', 'file', 'add_time']
    form_layout = (
        Fieldset(None,
                 'course', 'name', 'file'),
        Fieldset(None,
                 'teacher', **{"style": "display:None"}
                 )
    )

    def queryset(self):
        qs = super(CourseResourceAdmin, self).queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

        # 需要重写instance_forms方法，此方法作用是生成表单实例

    def instance_forms(self):
        super(CourseResourceAdmin, self).instance_forms()
        # 判断是否为新建操作，新建操作才会设置teacher的默认值
        if not self.org_obj:
            self.form_obj.initial['teacher'] = self.request.user.teacher


# class CourseTagAdmin(object):
#     list_display = ['course', 'tag','add_time']
#     search_fields = ['course', 'tag']
#     list_filter = ['course', 'tag','add_time']

# xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Course, NewCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
# xadmin.site.register(CourseTag, CourseTagAdmin)

xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)
xadmin.site.register(xadmin.views.BaseAdminView, BaseSettings)