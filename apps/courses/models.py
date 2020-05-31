from datetime import datetime

from django.db import models

from apps.users.models import BaseModel
from apps.organizations.models import Teacher
from apps.organizations.models import CourseOrg

from DjangoUeditor.models import UEditorField

from stdimage.models import StdImageField
from stdimage.utils import UploadToUUID

#1. 设计表结构有几个重要的点
"""
实体1 <关系> 实体2
课程 章节 视频 文本 课程资源
"""
#2. 实体的具体字段

#3. 每个字段的类型，是否必填


class Course(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="讲师")
    course_org = models.ForeignKey(CourseOrg, null=True, blank=True, on_delete=models.CASCADE, verbose_name="课程机构")
    name = models.CharField(verbose_name="课程名", max_length=50)
    desc = models.CharField(verbose_name="课程描述", max_length=300)
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    degree = models.CharField(verbose_name="难度", choices=(("cj", "初级"), ("zj", "中级"), ("gj", "高级")), max_length=2)
    students = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    notice = models.CharField(verbose_name="课程公告", max_length=300, default="")
    category = models.CharField(default=u"后端开发", max_length=20, verbose_name="课程类别")
    tag = models.CharField(default="", verbose_name="课程标签", max_length=10)
    youneed_know = models.CharField(default="", max_length=300, verbose_name="课程须知")
    teacher_tell = models.CharField(default="", max_length=300, verbose_name="老师告诉你")
    is_classics = models.BooleanField(default=False, verbose_name="是否经典")
    detail = UEditorField(verbose_name="课程详情", width=600, height=300, imagePath="courses/ueditor/images/",
                          filePath="courses/ueditor/files/", default="")
    is_banner = models.BooleanField(default=False, verbose_name="是否广告位")
    image = StdImageField(max_length=100,
                          upload_to=UploadToUUID(path=datetime.now().strftime('courses/%Y/%m')),
                          verbose_name=u"封面图",
                          variations={'thumbnail': {'width': 100, 'height': 75}})

    class Meta:
        verbose_name = "课程信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def lesson_nums(self):
        return self.lesson_set.all().count()

    def show_image(self):
        if self.image:
            href = self.image.url  # 点击后显示的放大图片
            src = self.image.thumbnail.url  # 页面显示的缩略图
            # 插入html代码
            image_html = '<a href="%s" target="_blank" title="传图片"><img alt="" src="%s"/>' % (href, src)
            return image_html
        else:
            return u'上传图片'
    show_image.short_description = "封面图"
    show_image.allow_tags = True

    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='/course/{}'>跳转</a>".format(self.id))
    go_to.short_description = "跳转"


class BannerCourse(Course):
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True


# class CourseTag(BaseModel):
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
#     tag = models.CharField(max_length=100, verbose_name="标签")
#
#     class Meta:
#         verbose_name = "课程标签"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.tag


class Lesson(BaseModel):
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE, verbose_name="讲师",blank=True,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")  #on_delete表示对应的外键数据被删除后，当前的数据应该怎么办
    name = models.CharField(max_length=100, verbose_name="章节名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")

    class Meta:
        verbose_name = "课程章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Video(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="讲师", blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    lesson = models.ForeignKey(Lesson, verbose_name="章节", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=u"正文名称")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    url = models.CharField(max_length=1000, verbose_name=u"视频地址",blank=True,null=True)#取消必填
    detail = UEditorField(verbose_name="正文详情", width=600, height=300, imagePath="courses/ueditor/images/",
                          filePath="courses/ueditor/files/", default="")

    class Meta:
        verbose_name = "课程正文"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="讲师", blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    file = models.FileField(upload_to="course/resourse/%Y/%m", verbose_name="下载地址", max_length=200)

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name