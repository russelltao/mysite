#coding:utf-8
import logging
from django.shortcuts import render,get_object_or_404  
from django.template.response import TemplateResponse  
from myblog.blog.models import Post,Page,Category,Widget
from django.views.generic import ListView, DetailView
from myblog.utils.cache import LRUCacheDict, cache
from myblog.settings import PAGE_NUM, RECENTLY_NUM, HOT_NUM, FIF_MIN
from django.core.paginator import Paginator
from django.db.models import Q
from myblog.stock.common import *
from django.views.generic.base import TemplateView
import time, getCurDataFromSina


logger = logging.getLogger(__name__)

stockMonitorList = [('600815', 9.13,3900),('600835',8.71,1500),('000858', 31.002,300)]


class BaseStock(object):

    def get_context_data(self, *args, **kwargs):
        context = super(BaseStock, self).get_context_data(**kwargs)
        try:
            #logger.info(context['categories'])
            context['pages'] = Page.objects.filter(status=0)
            sid = kwargs.get("sid",None)
            useDefault = False
            if sid == None or sid == "":
                print "sid==None"
                sid = stockMonitorList[0][0]
                useDefault = True
    
            print "sid=",sid
            context['stockid'] = sid
            
            slist  = []
                
            for sitem in stockMonitorList:
                active = False
                if sid == sitem[0]:
                    active = True
                slist.append((sitem[0],sitem[1],active,"/stock/%s"%(sitem[0])))
            context['stocklist'] = slist
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)

        return context

class StockDetailView(BaseStock, TemplateView):
    template_name = "StockDetail.html"

    def get_context_data(self, **kwargs):
        context = super(StockDetailView, self).get_context_data(**kwargs)

        sid =  context['stockid']
        sinaId = stockIDforSina(sid)
        sinadata = getCurDataFromSina.sinaStockAPI()
        resultmap = sinadata.getCurPriFromSina([sinaId])
        desc = ''
        for r in resultmap[0].items():
            print r[0],'=',r[1]
            info = "%s=%s   "%(r[0].decode('gbk'),r[1].decode('gbk'))
            desc+=info
        print desc
        context['curpri'] = desc
        context["dailyurl"]="http://image.sinajs.cn/newchart/daily/n/%s.gif"%(sinaId)
        context["minuteurl"]="http://image.sinajs.cn/newchart/min/n/%s.gif"%(sinaId)
        context["weekurl"]="http://image.sinajs.cn/newchart/weekly/n/%s.gif"%(sinaId)
        context["monthurl"]="http://image.sinajs.cn/newchart/monthly/n/%s.gif"%(sinaId)

        return context
    
class EarningsOverView(BaseStock, TemplateView):
    template_name = "EarningOverview.html"

    def get_context_data(self, **kwargs):
        context = super(EarningsOverView, self).get_context_data(**kwargs)

        sinaIds = []
        for r in stockMonitorList:
            sinaIds.append(stockIDforSina(r[0]))

        sinadata = getCurDataFromSina.sinaStockAPI()
        resultmap = sinadata.getCurPriFromSina(sinaIds)
        desc = ''
        for r in resultmap[0].items():
            print r[0],'=',r[1]
            info = "%s=%s   "%(r[0].decode('gbk'),r[1].decode('gbk'))
            desc+=info
        print desc

        return context
    