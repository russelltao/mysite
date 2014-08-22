#coding:utf-8
import logging
from django.shortcuts import render,get_object_or_404  
from django.template.response import TemplateResponse  
from django.views.generic import ListView, DetailView
from myblog.settings import PAGE_NUM, RECENTLY_NUM, HOT_NUM, FIF_MIN
from django.core.paginator import Paginator
from django.db.models import Q
from myblog.stock.common import *
from myblog.stock.ReadLocalData import *
import myblog.stock.CreateDiagram as CreateDiagram
from django.views.generic.base import TemplateView
import getCurDataFromSina
from myblog.stock.models import OwnerStocks
import os

logger = logging.getLogger(__name__)

    
def COL(name):
    return name.decode('utf8')

class BaseStock(object):
    def __init__(self):
        self.allProcStocks = []
        self.owner = 'master'

    def get_context_data(self, *args, **kwargs):
        context = super(BaseStock, self).get_context_data(**kwargs)
        try:
            #logger.info(context['categories'])
            owner = kwargs.get("owner")
            if owner != '' and owner != None:
                self.owner = owner
            allrows = OwnerStocks.objects.all()
            ownerNav = []
            ownerDict = {}
            for row in allrows:
                if ownerDict.has_key(row.owner):
                    continue
                else:
                    ownerDict[row.owner] = True
                    active = False
                    if row.owner == self.owner:
                        active = True
                    ownerNav.append((row.owner,'/stocks/%s/'%(row.owner),''))
                    
            context['owners'] = ownerNav
            self.allProcStocks = OwnerStocks.objects.filter(owner=self.owner)

            sid = kwargs.get("sid",None)

            slist  = []
            resultmap = self.get_all_cur_info(context)
                
            i = 0
            for sitem in resultmap:
                #print sitem
                active = False
                if sid == self.allProcStocks[i].stockId:
                    active = True
                slist.append((sitem[COL("股票名称")],self.allProcStocks[i].costPrice,active,\
                              "/stock/%s/%s"%(self.owner,self.allProcStocks[i].stockId)))
                i+=1
            context['stocklist'] = slist
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)

        return context
    
    def get_all_cur_info(self, context):
        sinaIds = []
        for r in self.allProcStocks:
            sinaIds.append(stockIDforSina(r.stockId))

        sinadata = getCurDataFromSina.sinaStockAPI()
        resultmap = sinadata.getCurPriFromSina(sinaIds)
        print len(resultmap)

        totalearning = 0
        searnings = []
        i = 0
        for r in resultmap:
            #print r
            name = r[COL('股票名称')]       
            curpri = float(r[COL('当前价格')])
            stockCount = float(self.allProcStocks[i].stockCount)
            initPri = float(self.allProcStocks[i].costPrice)
            income = (curpri-initPri)*stockCount
            searnings.append((name, initPri, curpri, stockCount, income, income>0))
            totalearning+=income
            print 'currentpri',curpri,stockCount,income,initPri
            i+=1
            
        context['allStocksIncome'] = searnings
        context['totalincome'] = totalearning
        context['isTotalEarn'] = totalearning>0
        
        return resultmap

class StockDetailView(BaseStock, TemplateView):
    template_name = "StockDetail.html"

    def get_context_data(self, **kwargs):
        context = super(StockDetailView, self).get_context_data(**kwargs)

        sid = kwargs.get("sid",None)
        sinaId = stockIDforSina(sid)
        sinadata = getCurDataFromSina.sinaStockAPI()
        resultmap = sinadata.getCurPriFromSina([sinaId])

        context['stockInfoInTime'] = self.constructInfoInTime(resultmap[0])
        context["dailyurl"]="http://image.sinajs.cn/newchart/daily/n/%s.gif"%(sinaId)
        context["minuteurl"]="http://image.sinajs.cn/newchart/min/n/%s.gif"%(sinaId)
        context["weekurl"]="http://image.sinajs.cn/newchart/weekly/n/%s.gif"%(sinaId)
        context["monthurl"]="http://image.sinajs.cn/newchart/monthly/n/%s.gif"%(sinaId)

        return context
    
    def constructInfoInTime(self, infodict):
        stockInfoInTime = []
        cur = ['当前价格',"成交量","成交金额"]
        sell5 = ['卖五成交价','卖五成交量','卖四成交价','卖四成交量','卖三成交价','卖三成交量','卖二成交价','卖二成交量',]
        buy5 = ["买一成交量","买一成交价","买二成交量","买二成交价","买三成交量","买三成交价","买四成交量","买四成交价","买五成交量","买五成交价"]
        sell5.extend(cur)
        sell5.extend(buy5)
        self.appendNameValue(stockInfoInTime, sell5, infodict)
        
        return stockInfoInTime


    def appendNameValue(self, list, names, infodict):
        for name in names:
            list.append((name,infodict[COL(name)]))
    
class EarningsOverView(BaseStock, TemplateView):
    template_name = "EarningOverview.html"

    def get_context_data(self, **kwargs):
        context = super(EarningsOverView, self).get_context_data(**kwargs)
        data = ReadLocalData()

        sids = []
        for ones in self.allProcStocks:
            sids.append(ones.stockId)
            
        lastdays = kwargs.get("days", None)
        if lastdays == None or lastdays == '':
            lastdays = 150
        else:
            lastdays = int(lastdays)
            
        today = datetime.date.today()
        fromday = today-datetime.timedelta(days=lastdays)
        filename = 'earn_%s_%s_to_%s.jpg'%(self.owner, fromday, today)
        imgUrl = '/stockimage/'+filename
        imgLoc = "/mnt/myblog/stock/"+filename
        context['earningHistoryUrl'] = imgUrl
        xAxisTitle = 'from %s to %s'%(fromday, today)
        yAxisTitle = 'RMB'
        
        if os.path.exists(imgLoc):
            return context
        
        allrows = []
        procInfo = []
        j = 0
        for ones in sids:
            rows = data.getLocalData(ones)
            if len(rows) == 0:
                print ones,"not exist"
            else:
                allrows.append(rows)
                procInfo.append(self.allProcStocks[j])
                
            j+=1
        
        allrows = data.getSameData(allrows, fromday, today)
        print "allrows",len(allrows)
        
        totalearningHistory = []
        days = []
        for rows in allrows:
            i=0
            totalearning = 0
            for row in rows:
                stockCount = float(procInfo[i].stockCount)
                initPri = float(procInfo[i].costPrice)
                curPri = float(row[DATE_COL_CLOSE])
                income = (curPri-initPri)*stockCount
                totalearning+=income
                i+=1
                
            totalearningHistory.append(totalearning)
            days.append(str(rows[0][DATE_COL_DATE]))
            #print "totalearning",totalearning,rows[0][DATE_COL_DATE]

        CreateDiagram.makeSymbolChart("earn", [totalearningHistory], days, ['totalearning'], \
                                      imgLoc, xAxisTitle,yAxisTitle)
        
        return context
    
    
    