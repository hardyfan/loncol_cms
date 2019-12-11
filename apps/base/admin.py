from django.contrib import admin
from django.db.models import Max
from .models import *
from django.utils.text import capfirst
from django.forms import Textarea, TextInput, forms


def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count


def index_decorator(func):
    def inner(*args, **kwargs):
        templateresponse = func(*args, **kwargs)
        for app in templateresponse.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return templateresponse

    return inner


admin.site.site_header = 'Loncol CMS 1.0'
admin.site.site_title = 'Loncol CMS'
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_code', 'category_tree_name', 'category_name', 'category_type', 'link_url', 'link_target',
                    'sort_number', 'is_active')
    list_editable = ('category_name', 'category_type', 'link_url', 'link_target', 'sort_number', 'is_active')
    search_fields = ('category_code', 'category_name')
    list_per_page = 20
    ordering = ('category_code', )
    fields = ('parent', 'category_name', 'category_type', 'link_url', 'link_target',
              'sort_number', 'is_active')

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width:200px'})},
    }

    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = ()
        if hasattr(obj, 'category_code'):
            if len(obj.category_code) > 0:
                self.readonly_fields = ('parent', )
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            obj.parent = self.model.objects.get(pk=obj.pk).parent
        else:
            parent = obj.parent
            max_code = self.model.objects.filter(parent=parent).aggregate(Max('category_code'))
            if max_code is None or max_code['category_code__max'] is None:
                new_code = '01'
            else:
                new_code = max_code['category_code__max']
                new_code = str(int(new_code[-2:]) + 1).rjust(2, '0')

            if parent is not None:
                new_code = parent.category_code + new_code

            obj.category_code = new_code
        super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    class CategoryFilter(admin.SimpleListFilter):
        title = '栏目'
        parameter_name = 'code'

        def lookups(self, request, model_admin):
            cate = Category.objects.filter(category_type=2)
            res = []
            for c in cate:
                res.append((c.category_code, c.category_name))
            return res

        def queryset(self, request, queryset):
            cate = request.GET
            if 'code' in cate:
                return Article.objects.filter(category_id=cate['code'])
            else:
                return queryset

    list_display = ('category', 'title', 'info_date', 'author', 'views', 'is_active')
    list_editable = ('is_active', )
    search_fields = ('title', )
    list_filter = (CategoryFilter, 'creator',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    ordering = ('-updated_at',)
    list_display_links = ('title',)
    actions_on_top = True
    actions_on_bottom = True
    fields = (('category', 'info_date', 'author'), ('title', 'is_active'), 'content', 'keywords', 'intro', 'cover',
              'position', ('views', 'creator', 'created_at'))
    #filter_horizontal = ('position',)
    raw_id_fields = ("position",)
    readonly_fields = ('views', 'creator', 'created_at')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ArticleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['author', ]:
            formfield.widget = TextInput(attrs={'style': 'width:100px'})
            formfield.initial = 'hardy'
        if db_field.name in ['title', 'keywords']:
            formfield.widget = TextInput(attrs={'style': 'width:600px'})
        if db_field.name in ['intro']:
            formfield.widget = Textarea(attrs={'rows': 3, 'cols': 110})
        return formfield

    def save_model(self, request, obj, form, change):
        if change:
            pass
        else:
            obj.creator = request.user
        super(ArticleAdmin, self).save_model(request, obj, form, change)


@admin.register(SinglePage)
class SinglePageAdmin(admin.ModelAdmin):
    list_display = ('category', 'views')
    ordering = ('category',)
    list_display_links = ('category',)
    fields = ('category', 'content', 'keywords', 'intro', 'views')
    readonly_fields = ('views', )

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = ('views', )
        if hasattr(obj, 'category'):
            if len(obj.page_category.category_code) > 0:
                self.readonly_fields = ('category', 'views')
        return self.readonly_fields

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(SinglePageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['keywords']:
            formfield.widget = TextInput(attrs={'style': 'width:500px'})
        if db_field.name in ['intro']:
            formfield.widget = Textarea(attrs={'rows': 3, 'cols': 110})
        return formfield

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            sps = SinglePage.objects.select_related('category')
            cts = set()
            for e in sps:
                cts.add(e.category.category_code)
            kwargs["queryset"] = Category.objects.filter(category_type=3).exclude(category_code__in=cts)

        return super(SinglePageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            obj.page_category = self.model.objects.get(pk=obj.pk).page_category
        else:
            pass
        super(SinglePageAdmin, self).save_model(request, obj, form, change)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'image', 'link_url', 'sort_number', 'is_active']
    list_editable = ['sort_number', 'text', 'image', 'link_url', 'is_active']
    ordering = ('sort_number',)
    list_display_links = ['id']

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BannerAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['text']:
            formfield.widget = Textarea(attrs={'rows': 2, 'cols': 50})
        return formfield


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']