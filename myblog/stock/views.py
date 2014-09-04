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
import MySQLdb
from dbAPI import getStockIdDB,stockDB

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
            allbuyrows = OwnerStocks.objects.all()
            ownerNav = []
            ownerDict = {}
            for row in allbuyrows:
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
            sinaId = stockIDforSina(sid)
            context["dailyurl"]="http://image.sinajs.cn/newchart/daily/n/%s.gif"%(sinaId)
            context["minuteurl"]="http://image.sinajs.cn/newchart/min/n/%s.gif"%(sinaId)
            context["weekurl"]="http://image.sinajs.cn/newchart/weekly/n/%s.gif"%(sinaId)
            context["monthurl"]="http://image.sinajs.cn/newchart/monthly/n/%s.gif"%(sinaId)
        
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
            print 'get_all_cur_info',r

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
            #print 'currentpri',curpri,stockCount,income,initPri
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
        sdb = stockDB()
        
        alldays = sdb.getAllDate(sid)
        showday = alldays[-1][0]
        print "getAllDate",alldays,showday
        
        filename = 'pankou_%s_%s.jpg'%(sid, showday)
        imgUrl = '/stockimage/'+filename
        imgLoc = "/mnt/myblog/stock/"+filename
        context['pankouVolUrl'] = imgUrl
        xAxisTitle = 'showday %s'%(showday)
        yAxisTitle = 'VOL'
        #if os.path.exists(imgLoc):
            #return context
        
        rows = sdb.getDayData(sid,showday)

        times = []
        for row in rows:
            times.append(str(row[1]))
        linenames = []
        for i in range(5):
            linenames.append("buy%d"%(i+1))
        for i in range(5):
            linenames.append("sell%d"%(1+i))
            
        voldatas = []

        for i in range(5):
            line1 = []
            line2 = []
            for row in rows:
                line1.append(int(row[29-2*i-1]))
                line2.append("%.2f"%(row[29-2*i]))
            voldatas.append(line1)

        curprices = []
        vols = []
        for row in rows:
            vols.append(int(row[8]))

        line = []
        for row in rows:
            line.append("%.2f"%row[3])
        curprices.append(line)
        
        for i in range(5):
            line1 = []
            line2 = []
            for row in rows:
                line1.append(int(row[10+2*i]))
                line2.append("%.2f"%(row[10+2*i+1])) 
            voldatas.append(line1)
        
        colors=['0x00CED1','0x00C5CD','0x008B8B','0x00688B','0x0000CD',\
                '0xEEA2AD','0xEE82EE','0xEE7942','0xEE6A50','0xEE3B3B']

        
        chart = CreateDiagram.SelfDefStockChart()
        
        chart.addXYChart("pankouVol", voldatas, times, linenames, \
                                      colors, xAxisTitle,yAxisTitle)
        c = chart.addXYChart("pankouVol", curprices, times, ['curpri'], \
                                      ['0xff9999'], xAxisTitle,yAxisTitle)
        #chart.addBar(c, vols, times)
        chart.makeChart(imgLoc)

        return context
    
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
        filename = 'earn_%s_%d_%s_to_%s.jpg'%(self.owner, lastdays, fromday, today)
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
        
        allrowsInit = data.getSameData(allrows, fromday, today)
        allrows = data.reduceData(allrowsInit)
        print "allrows",len(allrows),len(allrowsInit)
        
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
    
    
    