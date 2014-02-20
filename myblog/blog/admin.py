#coding:utf-8
from django.contrib import admin
#from django.contrib.markup.templatetags.markup import restructuredtext
from rstify import rstify
from .models import Post,Category,Page,Widget

from django.contrib import admin  
  
from django.db.models import TextField  

class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'alias')
    fields = ('content', 'summary', 'title', 'alias', 'tags', 'status',
              'category', 'is_top', 'is_old', 'pub_time')
    list_display = ('preview', 'title', 'category', 'is_top', 'pub_time')
    ordering = ('-pub_time', )
    save_on_top = True

    def preview(self, obj):
        return u'''
                    <span><a href="/%s.html" target="_blank">预览</a></span>
                    <span><a href="/admin/blog/post/%s/" target="_blank">编辑</a></span>
                ''' % (obj.alias, obj.id)

    preview.short_description = u'操作'
    preview.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        print "save user",obj.author
        if not obj.summary:
            obj.summary = obj.content

        
        if not obj.is_old:
            print "ready to convert rst to html"
            #print "1:",obj.content
            obj.content_html = rstify(obj.content)
            #print "2:",obj.content_html
            #obj.content_html = restructuredtext(obj.content)
        else:
            obj.content_html = obj.content.replace('\r\n', '<br/>')
            import re
            obj.content_html = re.sub(r"\[cc lang='\w+?'\]", '<pre>', obj.content_html)
            obj.content_html = obj.content_html.replace('[/cc]', '</pre>')
        obj.save()


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'alias')
    list_display = ('name', 'rank', 'is_nav', 'status', 'create_time')


class PageAdmin(admin.ModelAdmin):
    search_fields = ('name', 'alias')
    fields = ('title', 'alias', 'link', 'content', 'is_html', 'status', 'rank')
    list_display = ('title', 'link', 'rank', 'status', 'is_html')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        if obj.is_html:
            obj.content_html = obj.content
        else:
            obj.content_html = rstify(obj.content)
        obj.save()


class WidgetAdmin(admin.ModelAdmin):
    search_fields = ('name', 'alias')
    fields = ('title', 'content', 'rank', 'hide')
    list_display = ('title', 'rank', 'hide')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Widget, WidgetAdmin)



