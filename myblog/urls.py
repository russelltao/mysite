from django.conf.urls import patterns, include, url  
from django.contrib import admin  
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  
from myblog.blog.views import (PostDetailView,CategoryListView,
                               PageDetailView,IndexView,TagsListView)
from myblog.stock.views import StockDetailView,EarningsOverView
                               
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import views as sitemap_views
from sitemap import PostSitemap
from feeds import LatestEntriesFeed

from django.views.generic import TemplateView

admin.autodiscover()  
  

urlpatterns = patterns('',  
    (r'^accounts/', include('userena.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', IndexView.as_view(), name='home'),
    
    url(r'^feed|rss/$', LatestEntriesFeed()),
    
    url(r'^admin/', include(admin.site.urls), name='admin'),  
    url(r'^sitemap\.xml$', cache_page(60 * 60 * 12)(sitemap_views.sitemap ), {'sitemaps': {'posts': PostSitemap}}),
    url(r'^tag/(?P<tag>[\w|\.|\-]+)/$', TagsListView.as_view()),
    
    url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc', {}, 'xmlrpc'),
    
    (r'^stock/(?P<owner>\w+)/(?P<sid>.*)', StockDetailView.as_view()),
    (r'^stocks/(?P<owner>\w*)/(?P<days>\d*)', EarningsOverView.as_view()),
    (r'^stocks', EarningsOverView.as_view()),
     
    url(r'^category/(?P<alias>\w+)/', CategoryListView.as_view()),
    url(r'^(?P<slug>[\w|\-|\d|\W]+?).html$', PostDetailView.as_view()),
    url(r'^(?P<slug>\w+)/$', PageDetailView.as_view()),
    
)  

urlpatterns += staticfiles_urlpatterns() 

