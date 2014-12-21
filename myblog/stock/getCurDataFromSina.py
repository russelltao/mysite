#coding=gbk
import re
import urllib2
#from urlgrabber.keepalive import HTTPHandler
import datetime, time
import common,csv
import os
from dbAPI import getStockIdDB,stockDB
import getAllIdFromSina

sinaStockCol=("股票名称", "今日开盘价", "昨日收盘价", "当前价格","今日最高价","今日最低价",\
"竞买价","竞卖价","成交量","成交金额","买一成交量","买一成交价",\
"买二成交量","买二成交价","买三成交量","买三成交价","买四成交量","买四成交价",
"买五成交量","买五成交价","卖一成交量","卖一成交价",\
"卖二成交量","卖二成交价","卖三成交量","卖三成交价","卖四成交量","卖四成交价",
"卖五成交量","卖五成交价","日期","时间",)

        
class sinaStockAPI():
    intervalMinutes=30
    initSinaUrl="http://hq.sinajs.cn/list="
    
    def parseOneData(self, oneData, id, name, lastUpdateTime, dbObj):

        #print oneData    
        check = re.findall(r'var hq_str_([^=]*)=\"(.*)\"', oneData)
        temp = check[0]
        if len(temp) == 2:
            print temp[0], temp[1]
            if temp[0] != id:
                print temp[0],"!=",id
                return False
        else:
            if temp != id:
                print temp,"!=",id
            return False
        
        stockResultArray = oneData.split("\"")
        if len(stockResultArray) <= 2:
            return False
        stockValues = stockResultArray[1].split(",")
        count=0
        if len(stockValues) == len(sinaStockCol):
            print "stockValues[3]=", stockValues[3], type(stockValues[3])
            if stockValues[3] == "0.00" or stockValues[3] == "0.0":
                return False
            
            dateTime = stockValues[30]+" "+stockValues[31]
            #print dateTime, lastUpdateTime
            lastTime = datetime.datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
            if lastUpdateTime:
                delta = lastTime - lastUpdateTime
                if delta < datetime.timedelta(minutes=self.intervalMinutes):
                    print "stock", id, ": time",lastTime,"is same with last update time",lastUpdateTime
                    return False
                
            if name != stockValues[0]:
                print "update stock summary"
                try:
                    dbObj.updateStockSummary(id, stockValues[0], "")
                except Exception, e:
                    print "updateStockSummary exception", e
            #print id, name
            dbitems = []
            dbitems.append(dateTime)
            
            for i in range(29):
                dbitems.append(float(stockValues[i+1]))
                #print sinaStockCol[count],value
                #dbObj.updateStockSummary(id, name, "")
                count+=1
            #print dbitems
            try:
                #print "ready insertStock", id[2:len(id)], dbitems
                dbObj.insertStock(id[2:len(id)], dbitems)
                #print "updateStockSummaryTime", id, dateTime
                dbObj.updateStockSummaryTime(id[2:len(id)], dateTime)
            except Exception, e:
                print "insertStock except", e
        #print "parseOneData",count
        
        return True
    
    def parseDapan(self, oneData, dbobj, curTime):
        check = re.findall(r'var hq_str_([^=]*)=\"(.*)\"', oneData)
        temp = check[0]
        city = 'sh'
        if len(temp) == 2:
            #print temp[0], temp[1]
            if temp[0] == "s_sh000001":
                city = 'sh'
            elif temp[0] == "s_sz399001":
                city = 'sz'
            else:
                temp[0]
                return False
        else:
            return False
        
        stockResultArray = oneData.split("\"")
        if len(stockResultArray) <= 2:
            return False
        stockValues = stockResultArray[1].split(",")
        count=0
        insertval = [str(curTime)]
        if len(stockValues) == 6:
            for i in range(5):
                insertval.append(stockValues[i+1])
        else:
            print "error"   
            return False
        
        dbobj.insertDapan(city, insertval)

    
    def getDapan(self, curTime,dbObj):
        dapanUrl = self.initSinaUrl+"s_sh000001,s_sz399001"
        
        tm = dbObj.getDapanLatestTime("sz")
        delta = curTime - tm[0][0]
        if delta < datetime.timedelta(minutes=self.intervalMinutes):
            print "<%d min"%self.intervalMinutes
            return False        

        req = urllib2.Request(dapanUrl)   
        try:    
            response = urllib2.urlopen(req)
        except:
            #print "http connection error."
            return       
        strResult = str(response.read())
        allDatas = strResult.split("\n")
        for oneData in allDatas:
            if oneData == "":
                break

            #print n, len(allDatas), len(comList)
            self.parseDapan(oneData,dbObj, curTime)

    def getCurPriFromSina(self, sidList):
        curPriList = []
        
        batchGetSidList = []
        i = 0
        for sid in sidList:
            i+=1
            batchGetSidList.append(sid)
            if len(batchGetSidList) < 100 and i < len(sidList):
                continue
            else:
                if len(batchGetSidList) > 0:
                    self.getCurDataBatch(batchGetSidList, curPriList)
                    batchGetSidList = []
        
        return curPriList
    
    def getCurDataBatch(self, sidList, curPriList):
        sinaUrl = self.initSinaUrl

        for sid in sidList:
            sinaUrl += common.stockIDforSina(sid)
            sinaUrl += ","
  
        #print "request:",sinaUrl
        req = urllib2.Request(sinaUrl)   
        try:    
            response = urllib2.urlopen(req)
            strResult = str(response.read())    
        except:
            #print "http connection error."
            return None      
        
        #print strResult
        allDatas = strResult.split(";\n")
        i = 0
        for oneData in allDatas:
            i+=1
            if i > len(sidList):
                print "Waring:",i,len(sidList)
                break
            check = re.findall(r'var hq_str_([^=]*)=\"(.*)\"', oneData)
            if len(check) == 0:
                curPriList.append(None)
                continue

            temp = check[0]
            if len(temp) == 2:
                pass
                #print temp[0], temp[1]
            else:
                print temp,"!=",id
                curPriList.append(None)
                continue
            
            stockResultArray = oneData.split("\"")
            if len(stockResultArray) <= 2:
                print "error"
                curPriList.append(None)
                continue
            
            stockValues = stockResultArray[1].split(",")
            
            meaning = {}
            j = 0
            for key in sinaStockCol:
                meaning[key.decode('gbk')]=stockValues[j].decode('gbk')
                j+=1
            curPriList.append(meaning)
            print stockValues[0]
            #curPriList.append(stockValues[1:6])
            
        if len(curPriList) != len(sidList):
            print "getCurPriFromSina error:",sinaUrl,strResult
            #print "curPriList",curPriList
            pass
        return curPriList

    def getInfoFromSina(self, idList, dbObj, curTime):
        sinaUrl = self.initSinaUrl
        
        
        comList = []

        for id in idList:
            #print id
            #print id[2],type(id[2])
            
            if id[2]:
                delta = curTime - id[2]
                if delta < datetime.timedelta(minutes=self.intervalMinutes):
                    continue

            sinaUrl += id[0]
            sinaUrl += ","
            comList.append(id)

        keepalive_handler = HTTPHandler()
        opener = urllib2.build_opener(keepalive_handler)
        urllib2.install_opener(opener)
          
        #req = urllib2.Request( sinaUrl)   
        try:    
            #response = urllib2.urlopen(req)
            req = urllib2.urlopen(sinaUrl)
        except:
            #print "http connection error."
            return       
        strResult = str(response.read())
        #print strResult
        allDatas = strResult.split("\n")
        n = 0
        for oneData in allDatas:
            if oneData == "":
                break

            #print n, len(allDatas), len(comList)
            self.parseOneData(oneData,comList[n][0], comList[n][1], comList[n][2], dbObj)
            n+=1



class CollectSinaData():
    def __init__(self, intervalSec = 10):
        self.initSinaUrl = "http://hq.sinajs.cn/list="
        self.intervalSec = intervalSec
        self.maxStockOnce = 860

        self.columns = ["time","curpri","vol","compbuy","compsell"]
        

        for i in range(5):
            self.columns.append("%dsellvol"%(5-i))
            self.columns.append("%dspri"%(5-i))
        for i in range(5):
            self.columns.append("%dbuyvol"%(i+1))
            self.columns.append("%dbpri"%(i+1))
            
    def getOnceData(self, idlist, stockdb):
        time1 = datetime.datetime.now()
        result = []
        if False == self.getData(idlist, result):
            time.sleep(self.intervalSec)
            return 0

        n = 0
        failCount = 0
        notTodayCount = 0
        sameLastTimeCount = 0
        successCount = 0
        dbErrorCount = 0
        for row in result:
            id = idlist[n]
            n+=1
            
            if row is None:
                failCount+=1
                continue

            try:
                thistime = datetime.datetime.strptime(row[0]+" "+row[1], '%Y-%m-%d %H:%M:%S')
            except Exception,e:
                print e,row,"len=",len(row)
                failCount+=1
                continue
            
            if self.lasttime.has_key(id):
                #print dateTime, lastUpdateTime
                if self.lasttime[id] == thistime:
                    #print "same time as ",self.lasttime[id],id
                    sameLastTimeCount += 1
                    continue
                #row[8] == row[8] - self.lastvol[id]
                
            if thistime.day != time1.day or time1.month != thistime.month:
                #print thistime,"!=",time1
                notTodayCount+=1
            else:
                self.lasttime[id] = thistime
                
                if not stockdb.insertStock(id, row):
                    dbErrorCount+=1
                else:
                    successCount+=1
            #print id, row
            
        time2 = datetime.datetime.now()
        print len(idlist),"cost:",time2-time1,"failCount:",failCount,"notTodayCount:",notTodayCount\
        ,"sameLastTimeCount:",sameLastTimeCount,"successCount:",successCount,"dbErrorCount:",dbErrorCount
        return successCount
        
    def startLoop(self, idlist):

        filelist = {}
        csvlist = {}
        self.lasttime = {}
        self.lastvol = {}
        
        onceCount = 0
        allIdList = []
        onceIdList = []
        print "start to get lasttime from db",datetime.datetime.now()
        stockdb = stockDB()
        for id in idlist:
            onceCount+=1
            onceIdList.append(id)
            lasttime = stockdb.getLastDate(id)
            if lasttime != None:
                self.lasttime[id] = lasttime
            
            if onceCount < self.maxStockOnce:
                pass
            else:
                allIdList.append(onceIdList)
                onceIdList = []
                onceCount = 0
              
        allIdList.append(onceIdList)
        
        print "start to loop",datetime.datetime.now()
        while True:
            curTime = datetime.datetime.now()
            res = common.secToMarcketOpen(curTime) - 60
            if res > 0:
                print "sleep secondes:",res
                stockdb.close()
                time.sleep(res)
                stockdb.connect()
                continue
            
            successCount = 0
            for onceIds in allIdList:
                successCount+=self.getOnceData(onceIds, stockdb)
                time.sleep(0.8)
            
            sleepSec = self.intervalSec
            if successCount == 0:
                if sleepSec < 60:
                    print "All failed, sleep 1 minutes"
                    sleepSec = 60
            #time.sleep(sleepSec)
        
    def validate(self, items):
        if len(items) < 30:
            return False
        if items[3] == "0.00" or items[3] == "0.0":
            #print "error 2",stockValues
            return False

        for i in range(26):
            try:
                if int(items[i+3]) == 0:
                    return False
            except:
                pass

        return True
    
    def parse(self, sid, oneData, realtimeData):
        #print "parse=",oneData    
        check = re.findall(r'var hq_str_([^=]*)=\"(.*)\"', oneData)
        
        stockResultArray = oneData.split("\"")
        if len(stockResultArray) <= 2:
            print "error 1"
            return False
        stockValues = stockResultArray[1].split(",")
        count=0
        zeroFailCount = 0
        if len(stockValues) >= len(sinaStockCol):
            #print "stockValues[3]=", stockValues[3], type(stockValues[3])

            if not self.validate(stockValues):
                #print "error 2",stockValues
                return False
            
            #date
            realtimeData.append(stockValues[30])
            #time
            realtimeData.append(stockValues[31])
            #openprice
            realtimeData.append(stockValues[1])
            
            for i in range(27):
                realtimeData.append(stockValues[3+i])
                
        else:
            print "parse",len(stockValues), ">=", len(sinaStockCol),stockValues
            return False
            
        return True
    
    def getData(self, idList, resultTable):
        sinaUrl = self.initSinaUrl

        for id in idList:
            #print id
            sinaUrl += common.stockIDforSina(id)
            sinaUrl += ","

        #print "sinaUrl",sinaUrl
        req = urllib2.Request(sinaUrl)
        try:    
            response = urllib2.urlopen(req)
        except:
            print "http connection error."
            return False
        
        strResult = str(response.read())
        print "idCount=%d,response=%d,request=%d"%(len(idList),len(strResult),len(sinaUrl))
    
        allDatas = strResult.split("\n")
        n = 0
        failCount = 0
        if len(idList) > len(allDatas):
            print allDatas
            print "idCount:%d, valueCount:%d"%(len(idList), len(allDatas))
            return False
        
        for oneData in allDatas:
            if oneData == "":
                break
            elif n >= len(idList):
                break

            #print n, len(allDatas),oneData
            realtimeData = []
            totalData = []
            if True == self.parse(idList[n],oneData, realtimeData):
                resultTable.append(realtimeData)
            else:
                resultTable.append(None)
                failCount+=1

            n+=1
        #if failCount > 0:
            #print "getData fail stock count:",failCount
        return True

def getAllData():
    a = getAllIdFromSina.sinaIdManage()
    #a.initFromSinaHy()
    a.initLocalData()

    sinaobj = CollectSinaData(6)
    sids = []
    for id,v in a.allstockmap.items():
        sids.append(id)

    res = sinaobj.startLoop(sids)

def getMasterPetData():
    idDB = getStockIdDB()
    rows = idDB.getAllSid()
    idDB.close()
    sids = []
    for row in rows:
        sids.append(str(row[0]))
    print sids
    sinaobj = CollectSinaData(3)
    #sidList = ["300078","601808","600815","600835","000858","600005","600030","600062","600396","600469","600479","601111","601398","000027","000402","000777"]
    res = sinaobj.startLoop(sids)
    print "RESULT:",res
    
if __name__ == "__main__":
    getAllData()

    
    
    
