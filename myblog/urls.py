from django.conf.urls import patterns, include, url  
from django.contrib import admin  
admin.autodiscover()  
  
urlpatterns = patterns('',  
    url(r'^$', 'blog.views.home', name='home'),  
    # url(r'^blog/', include('blog.urls')),  
    url(r'^blog/(?P<slug>[-\w]+)/$','blog.views.blog',name='home'),  
    url(r'^admin/', include(admin.site.urls)),  
)  