from django.db import models
from django.db.models import Q

from django.utils import timezone
from django.utils.html import format_html

from mdeditor.fields import MDTextField
from django.contrib.auth.models import User


class BaseSchema(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    creator = models.ForeignKey(User,
                                on_delete=models.DO_NOTHING,
                                blank=True,
                                null=True,
                                verbose_name='创建者')
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    deleted_at = models.DateTimeField("删除时间", null=True, default=None, editable=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()


# 栏目
class Category(models.Model):
    CATEGORY_TYPE_CHOICES = (
        (1, '栏目'),
        (2, '文章'),
        (3, '页面'),
        (4, '链接'),
    )
    TARGET_CHOICES = (
        ('_self', '本窗口'),
        ('_blank', '新窗口'),
        ('_parent', '父窗口'),
        ('_top', '顶层窗口'),
    )

    parent = models.ForeignKey('self', limit_choices_to=Q(category_type=1),
                               on_delete=models.DO_NOTHING, verbose_name='上级栏目', blank=True, null=True)
    category_code = models.CharField('栏目代码', max_length=20, unique=True, primary_key=True)
    category_name = models.CharField('栏目名称', max_length=50)
    category_type = models.IntegerField('栏目类型', choices=CATEGORY_TYPE_CHOICES, default=1)
    link_url = models.URLField('链接地址', max_length=100, blank=True)
    link_target = models.CharField('打开方式', max_length=10, choices=TARGET_CHOICES, blank=True, null=True)
    sort_number = models.IntegerField('排序号', default=100)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '菜单'
        verbose_name_plural = verbose_name

    def category_tree_name(self):
        px = len(self.category_code)*10
        return format_html('<span style="padding-left:{px}px">┆┄┄{name}</span>'.format(
            px=px, name=self.category_name))

    category_tree_name.short_description = '栏目数'

    def __str__(self):
        return self.category_name


# 推荐位
class Position(models.Model):
    name = models.CharField('推荐位描述', max_length=100)

    class Meta:
        verbose_name = '推荐位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 文章
class Article(BaseSchema):
    REC_POS_CHOICES = (
        (1, '图片新闻'),
        (2, '新闻精选'),
    )

    category = models.ForeignKey(Category,
                                 limit_choices_to=Q(category_type=2),
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='栏目')
    info_date = models.DateField('日期', default=timezone.now)
    author = models.CharField('作者', max_length=100, blank=True, null=True,)
    title = models.CharField('标题', max_length=200)
    content = MDTextField('内容')
    keywords = models.CharField('关键字', max_length=500, blank=True, null=True)
    intro = models.CharField('简介', max_length=2000, blank=True, null=True)
    cover = models.ImageField('封面',
                              help_text='（图片格式：png，图片尺寸：400*300px）',
                              upload_to='cover/%Y/%m/%d/',
                              blank=True,
                              null=True,)
    position = models.ManyToManyField(Position, verbose_name='推荐位',
                                      blank=True,
                                      null=True)
    is_active = models.BooleanField('是否启用', default=False)
    views = models.IntegerField('浏览量', default=0)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 页面
class SinglePage(models.Model):
    category = models.ForeignKey(Category,
                                 limit_choices_to=Q(category_type=3),
                                 on_delete=models.CASCADE,
                                 default=None,
                                 verbose_name='栏目')
    content = MDTextField('内容')
    keywords = models.CharField('关键字', max_length=200, blank=True, null=True)
    intro = models.CharField('简介', max_length=2000, blank=True, null=True)
    views = models.IntegerField('浏览量', default=0)

    class Meta:
        verbose_name = '页面'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.category_name


# 轮播图
class Banner(models.Model):
    text = models.CharField('轮播标题', max_length=200, default='')
    image = models.ImageField('轮播图片',
                              help_text='（图片格式：png，图片尺寸：400*300px）',
                              upload_to='banner/')
    link_url = models.URLField('链接地址', max_length=200)
    sort_number = models.IntegerField('排序号', default=1)
    is_active = models.BooleanField('是否启用', default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
