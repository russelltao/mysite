from django.contrib import admin  
from blog.models import Blog  
  
from django.db.models import TextField  
from file_picker.wymeditor.widgets import WYMeditorWidget  
  
class BlogAdmin(admin.ModelAdmin):  
    prepopulated_fields={'slug':('title',)}  
    list_display=('title','time')  
    formfield_overrides={TextField:{'widget':WYMeditorWidget({}) }}  
    class Media:  
        js=('http://libs.baidu.com/jquerytools/1.2.7/jquery.tools.min.js',)  
  
admin.site.register(Blog,BlogAdmin)  