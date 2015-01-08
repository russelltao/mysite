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
from myblog.stock.models import Operations
import os, datetime
import MySQLdb,dbAPI,getAllIdFromSina
import CalcTurnOverRatio

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
            pass
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)

        return context

class OneStock(BaseStock):
    def get_context_data(self, *args, **kwargs):
        context = super(OneStock, self).get_context_data(**kwargs)
        try:
            #logger.info(context['categories'])
            self.sid = self.request.GET.get('s')
            if self.sid == None or self.sid == '':
                return context
            
            sinaId = stockIDforSina(self.sid)
            context["dailyurl"]="http://image.sinajs.cn/newchart/daily/n/%s.gif"%(sinaId)
            context["minuteurl"]="http://image.sinajs.cn/newchart/min/n/%s.gif"%(sinaId)
            context["weekurl"]="http://image.sinajs.cn/newchart/weekly/n/%s.gif"%(sinaId)
            context["monthurl"]="http://image.sinajs.cn/newchart/monthly/n/%s.gif"%(sinaId)
            
            sdb = dbAPI.stockDB()
            
            alldays = sdb.getAllDate(self.sid)
            if len(alldays) == 0:
                print "no data"
                return context
            showday = alldays[-1][0]
            pankouDays = []
            for row in alldays:
                print "day:",row
                pankouDays.append((row[0], '/stock/'+row[0].strftime('%Y%m%d')+"?s="+self.sid))
            print "getAllDate",alldays,showday
            context['pankouDays'] = pankouDays
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)

        return context
    
class StockKLView(OneStock, TemplateView):
    template_name = "StockKL.html"

    def get_context_data(self, **kwargs):
        context = super(StockKLView, self).get_context_data(**kwargs)

        if not self.sid:
            return context
        
        KLdatas = []
        hisData = ReadLocalData()
        rows = hisData.getLocalData(self.sid)
        for row in rows:
            KLdata = [row[DATE_COL_DATE].strftime('%Y%m%d'),0,row[DATE_COL_OPEN],row[DATE_COL_HIGH],row[DATE_COL_LOW],row[DATE_COL_CLOSE],\
                            row[DATE_COL_VOL], float(row[DATE_COL_CLOSE])*int(row[DATE_COL_VOL])]
            KLdatas.append(KLdata)
            #print 'KLdata',KLdata
        context['KLdatas'] = KLdatas
        
        return context
    
    
class StockDetailView(OneStock, TemplateView):
    template_name = "StockDetail.html"

    def get_context_data(self, **kwargs):
        context = super(StockDetailView, self).get_context_data(**kwargs)

        showday = kwargs.get("day",None)

        if showday == None or not self.sid:
            return context
        
        context['KLurl'] = 'http://taohui.org.cn/stockKL/?s='+self.sid
        sdb = dbAPI.stockDB()
        
        filename = 'pankou_%s_%s.jpg'%(self.sid, showday)
        imgUrl = '/stockimage/'+filename
        imgLoc = "/mnt/myblog/stock/"+filename
        context['pankouVolUrl'] = imgUrl
        xAxisTitle = 'showday %s'%(showday)
        yAxisTitle = 'VOL'

        rows = sdb.getDayData(self.sid, datetime.datetime.strptime(showday, '%Y%m%d').date())
        if len(rows) == 0:
            print len(rows),sid,showday[0:4],showday[4,2],showday[6,2]
            return context

        pankouDatas = []
        times = []
        lastVol = rows[0][dbAPI.DBCOL_EXCH_VOL]
        for row in rows:
            times.append(str(row[1]))
            
            pline = [row[dbAPI.DBCOL_CUR_PRI],row[dbAPI.DBCOL_EXCH_VOL]-lastVol,\
                     row[dbAPI.DBCOL_EXCH_AMOUNT],row[dbAPI.DBCOL_TIME],\
                     row[dbAPI.DBCOL_COMP_BUY_PRI],row[dbAPI.DBCOL_COMP_SELL_PRI] ]
            for i in range(20):
                pline.append(row[10+i])
            pankouDatas.append(pline)
            lastVol = row[dbAPI.DBCOL_EXCH_VOL]
            
        idManager = getAllIdFromSina.sinaIdManage()
        idManager.initLocalData()
        print idManager.allstockmap[self.sid]
                
        context['pankouDatas'] = pankouDatas
        context['dataLen'] = len(pankouDatas)
        context['highest'] = rows[-1][dbAPI.DBCOL_HIGH_PRI]
        context['lowest'] = rows[-1][dbAPI.DBCOL_LOW_PRI]
        context['open'] = rows[-1][dbAPI.DBCOL_OPEN_PRI]
        context['price'] = rows[-1][dbAPI.DBCOL_CUR_PRI]
        context['day'] = rows[-1][dbAPI.DBCOL_DATE].strftime('%Y%m')
        context['volume'] = rows[-1][dbAPI.DBCOL_EXCH_VOL]
        context['amount'] = rows[-1][dbAPI.DBCOL_EXCH_AMOUNT]
        
        if os.path.exists(imgLoc):
            print imgLoc,'picfile exist!'
            return context
            
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
    
    def showFormat(self, t):
        return "%d%.2d%.2d"%(t.year,t.month,t.day)
    
    def showDayInfo(self, hisrow, totalStockNum):
        return "%s\n开盘：%s\n最高：%s\n最低：%s\n收盘：%s\n换手：%.2f"%\
( hisrow[DATE_COL_DATE], hisrow[DATE_COL_OPEN], hisrow[DATE_COL_HIGH], hisrow[DATE_COL_LOW], hisrow[DATE_COL_CLOSE],100*float(hisrow[DATE_COL_VOL])/totalStockNum )

    def showCurDayInfo(self, currdata, totalStockNum):
        return "%s\n开盘：%s\n最高：%s\n最低：%s\n收盘：%s\n换手：%.2f"%\
( currdata[COL('日期')], currdata[COL('今日开盘价')], currdata[COL('今日最高价')], \
  currdata[COL('今日最低价')], currdata[COL('当前价格')],100*float(currdata[COL('成交量')])/totalStockNum )

    def analysisTrade(self, alltrade, currdata, tabledata, alreadyHolderDatas, detailinfo, shDapanDict):
        moneypool = 0
        curHoldCount = 0
        
        stockId = alltrade[0].stockId
        name = currdata[COL('股票名称')]
        KLurl = '/stockKL?s='+stockId
        sinaUrl = "http://vip.stock.finance.sina.com.cn/moneyflow/#!ssfx!"+stockIDforSina(stockId)
        
        nextTime = datetime.datetime.strptime(currdata[COL('日期')],'%Y-%m-%d')
        
        op = '无操作'
        kdataproc = ReadLocalData()
        hisrows = kdataproc.getLocalData(stockId, -1, alltrade[0].time)
        print 'hisrows=',len(hisrows)
        newPrice = float(currdata[COL('当前价格')])
        if newPrice == 0.0:
            if len(hisrows) > 1:
                newPrice = float(hisrows[-1][DATE_COL_CLOSE])
            else:
                print name
                return (0,0)
            
        nextPrice = newPrice
        
        totalStockNum = 10000*detailinfo[getAllIdFromSina.SCOL_MKTCAP]/newPrice
        currDayInfo = self.showCurDayInfo(currdata, totalStockNum)
        for i in range(len(alltrade)):
            trade = alltrade[i]
            
            curTime = trade.time
            curPri = float(trade.costPrice)
            stockCount = trade.stockCount
            
            cc = trade.costPrice*trade.stockCount
            moneyIncrease = 0
            if trade.operation == 0:
                #买入
                op = "买%d"%(trade.stockCount)
                moneypool -= cc
                curHoldCount += stockCount
            elif trade.operation == 1:
                #卖出
                op = "卖%d"%(trade.stockCount)
                moneypool += cc
                curHoldCount -= stockCount
                stockCount=-stockCount
            else:
                print "error",trade.operation
                
            
            if i == len(alltrade)-1:
                nextTime = datetime.datetime.strptime(currdata[COL('日期')],'%Y-%m-%d').date()
                nextPrice = newPrice
            else:
                nextTime = alltrade[i+1].time
                nextPrice = float(alltrade[i+1].costPrice)
                
            priIncreasePercent = 100*(nextPrice-curPri)/curPri
            moneyIncrease = stockCount*(nextPrice-curPri)

            curEarningInfo = ''
            curEarn = 0
            if curHoldCount == 0:
                curEarningInfo = "若仍然持有，那么将盈利%d%%"%(priIncreasePercent)
            else:
                curEarn = moneyIncrease
                curEarningInfo = "盈利%d%%"%(priIncreasePercent)
            
            print stockId,curTime,"curPri=",curPri,'nextPrice=',nextPrice,nextTime
            hisHighPri,hisHighInfo = nextPrice,currDayInfo
            hisHighVol,hisHighVolInfo = int(currdata[COL('成交量')]),currDayInfo
            hisLowPri,hisLowInfo = nextPrice,currDayInfo

            dayCount = 0
            volSum = 0
            nextDayInfo = currDayInfo
            thisDayInfo = ''
            dapanStrong,dapanWeak = 0,0
            for i in range(len(hisrows)):
                hisrow = hisrows[i]
                histime = hisrow[DATE_COL_DATE]
                if histime == nextTime:
                    nextDayInfo = self.showDayInfo(hisrow, totalStockNum)
                elif histime == curTime:
                    thisDayInfo = self.showDayInfo(hisrow, totalStockNum)
                    
                if histime > curTime and histime < nextTime:
                    dayCount+=1
                    
                    hisclosepri = float(hisrow[DATE_COL_CLOSE])
                    hisopenpri = float(hisrow[DATE_COL_OPEN])
                    hisvol = int(hisrow[DATE_COL_VOL])
                    volSum+=hisvol
                    if hisclosepri > hisHighPri:
                        hisHighPri = hisclosepri
                        hisHighInfo = self.showDayInfo(hisrow, totalStockNum)
                    if hisclosepri < hisLowPri:
                        hisLowPri = hisclosepri
                        hisLowInfo = self.showDayInfo(hisrow, totalStockNum)
                    if hisvol > hisHighVol:
                        hisHighVol = hisvol
                        hisHighVolInfo = self.showDayInfo(hisrow, totalStockNum)
                        
                    lastClosePri = float(hisrows[i-1][DATE_COL_CLOSE])
                    #print hisrows[i-1][DATE_COL_DATE]
                    if False== shDapanDict.has_key(hisrows[i-1][DATE_COL_DATE]):
                        #print "dapan not find",hisrows[i-1][DATE_COL_DATE]
                        continue
                    if False== shDapanDict.has_key(hisrows[i][DATE_COL_DATE]):
                        #print "dapan not find",hisrows[i][DATE_COL_DATE]
                        continue
                    lastSHClose = float(shDapanDict[hisrows[i-1][DATE_COL_DATE]][DATE_COL_CLOSE])
                    thisSHClose = float(shDapanDict[hisrows[i][DATE_COL_DATE]][DATE_COL_CLOSE])

                    if (thisSHClose-lastSHClose)/lastSHClose > (hisclosepri-lastClosePri)/lastClosePri:
                        dapanStrong+=1
                    else:
                        dapanWeak+=1
  
                       
            avgVol = 0 
            avgTurnover = 0
            if dayCount > 0:
                avgVol = float(volSum)/dayCount
                avgTurnover = 100*avgVol/totalStockNum
                hisHighVolInfo+=("\n日均换手：%.2f"%(avgTurnover))
            else:
                print "get nothing:",stockId
                
            tableLine = [name, sinaUrl, self.showFormat(curTime), thisDayInfo,\
                       trade.costPrice, op, "金额：%d"%(trade.costPrice*trade.stockCount),\
                       curHoldCount, "持有金额：%d"%(trade.costPrice*curHoldCount), nextDayInfo,\
                       nextPrice, curEarn, curEarningInfo, \
                       "%.2f"%(hisHighPri), hisHighInfo,\
                       "%.2f"%(hisLowPri), hisLowInfo,\
                       "%.2f"%(100*hisHighVol/totalStockNum), hisHighVolInfo,\
                       "%d/%d"%(dapanWeak,dapanStrong),
                       trade.info]
            tabledata.append(tableLine)
        
        if curHoldCount != 0:
            moneypool += newPrice*curHoldCount
            alreadyHolderDatas.append([stockId, KLurl, name, sinaUrl, \
                        curHoldCount, moneypool, newPrice])
            
        mycost = -moneypool
        
        return (mycost, moneypool)

    def get_context_data(self, **kwargs):
        try:
            context = super(EarningsOverView, self).get_context_data(**kwargs)

            kdataproc = ReadLocalData()
            shDapanRows = kdataproc.getLocalData(DPshzhongzhi)
            shDapanDict = {}
            print 'shDapanRows=',len(shDapanRows)
            for row in shDapanRows:
                shDapanDict[row[DATE_COL_DATE]]=row
        
            allOperRows = Operations.objects.all()
            ownerDict = {}
            
            sinaIds = []
            for row in allOperRows:
                if ownerDict.has_key(row.owner):
                    if ownerDict[row.owner].has_key(row.stockId):
                        ownerDict[row.owner][row.stockId].append(row)
                    else:
                        ownerDict[row.owner][row.stockId] = [row]
                        sinaIds.append(stockIDforSina(row.stockId))
                else:
                    ownerDict[row.owner] = {row.stockId:[row]}
                    sinaIds.append(stockIDforSina(row.stockId))
            
            sinadata = getCurDataFromSina.sinaStockAPI()
            resultmap = sinadata.getCurPriFromSina(sinaIds)
            realSinaData = {}

            for i in range(len(sinaIds)):
                realSinaData[sinaIds[i]] = resultmap[i]
            
            allOwnerInfo = []
            idManager = getAllIdFromSina.sinaIdManage()
            idManager.initLocalData()

            for owner, stockrows in ownerDict.items():
                totalCost = 0  

                i = 0
                totalearning = 0
                listTableDatas = []
                alreadyHolderDatas = []
                for sid, onestock in stockrows.items():
                    detailinfo = idManager.allstockmap[sid]
                    sortdata = sorted(onestock,key = lambda x:x.time,reverse = False) 
                    #print onestock,'--',sortdata
                    thiscost,thisearning = self.analysisTrade(sortdata, realSinaData[stockIDforSina(sid)], listTableDatas, alreadyHolderDatas, detailinfo, shDapanDict)
                    totalCost += thiscost
                    totalearning += thisearning
      
                allOwnerInfo.append([owner, listTableDatas,alreadyHolderDatas,totalCost, totalearning])
                    
            context['allOwnerInfo'] = allOwnerInfo
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)
            
        return context
    
class TurnoverRatioView(BaseStock, TemplateView):
    template_name = "TurnoverRate.html"

    def get_context_data(self, **kwargs):
        try:
            context = super(TurnoverRatioView, self).get_context_data(**kwargs)
            
            idManager = getAllIdFromSina.sinaIdManage()
            a = CalcTurnOverRatio.CalcTurnOverRate()
            idManager = getAllIdFromSina.sinaIdManage()
            idManager.initLocalData()
            datas = a.getHighRate(idManager, 100)
            slist = []
            for line in datas:
                stockId = line[CalcTurnOverRatio.RATE_COL_ID]
                detailinfo = idManager.allstockmap[stockId]
                
                KLurl = '/stockKL?s='+stockId
                sinaUrl = "http://vip.stock.finance.sina.com.cn/moneyflow/#!ssfx!"+stockIDforSina(stockId)
                onedata = [stockId,KLurl,detailinfo[getAllIdFromSina.SCOL_NAME],sinaUrl]
                onedata.append("%.2f"%(line[CalcTurnOverRatio.RATE_COL_LONGRATE]-line[CalcTurnOverRatio.RATE_COL_MIDRATE]))
                onedata.append("%.2f"%((line[CalcTurnOverRatio.RATE_COL_1PRI]-line[CalcTurnOverRatio.RATE_COL_0PRI])/line[CalcTurnOverRatio.RATE_COL_0PRI]))
                onedata.append("%.2f"%(line[CalcTurnOverRatio.RATE_COL_MIDRATE]-line[CalcTurnOverRatio.RATE_COL_SHORTRATE]))
                onedata.append("%.2f"%((line[CalcTurnOverRatio.RATE_COL_2PRI]-line[CalcTurnOverRatio.RATE_COL_1PRI])/line[CalcTurnOverRatio.RATE_COL_1PRI]))
                onedata.append("%.2f"%(line[CalcTurnOverRatio.RATE_COL_SHORTRATE]))
                onedata.append("%.2f"%((line[CalcTurnOverRatio.RATE_COL_3PRI]-line[CalcTurnOverRatio.RATE_COL_2PRI])/line[CalcTurnOverRatio.RATE_COL_2PRI]))
                onedata.append(detailinfo[getAllIdFromSina.SCOL_PB])
                onedata.append("%.2f"%(float(detailinfo[getAllIdFromSina.SCOL_MKTCAP])/10000))
                onedata.append("%.2f"%(float(detailinfo[getAllIdFromSina.SCOL_NMC])/10000))
                onedata.append(detailinfo[getAllIdFromSina.SCOL_PER])
                onedata.append(detailinfo[getAllIdFromSina.SCOL_TURNOVERRATIO])
                
                slist.append(onedata)
                
            context['listStocks'] = slist
        except Exception as e:
            logger.exception(u'加载基本信息出错[%s]！', e)
            
        return context
    

    
    