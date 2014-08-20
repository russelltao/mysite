#coding=gbk
import re
import urllib2
#from urlgrabber.keepalive import HTTPHandler
import datetime, time
import common,csv
import os

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
            print temp[0], temp[1]
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
        
        print strResult
        allDatas = strResult.split("\n")
        i = 0
        for oneData in allDatas:
            i+=1
            if i > len(sidList):
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
            i = 0
            for key in sinaStockCol:
                meaning[key]=stockValues[i]
                i+=1
            curPriList.append(meaning)
            #print len(sinaStockCol), len(stockValues),stockValues
            #curPriList.append(stockValues[1:6])
            
        if len(curPriList) != len(sidList):
            #print "getCurPriFromSina error:",sinaUrl,strResult
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
        self.glabalFolder = "d:/everbox/data/"
        if os.path.exists(self.glabalFolder):
            pass
        else:
            os.mkdir(self.glabalFolder)

        self.columns = ["time","curpri","vol","compbuy","compsell"]

        for i in range(5):
            self.columns.append("%dsellvol"%(5-i))
            self.columns.append("%dspri"%(5-i))
        for i in range(5):
            self.columns.append("%dbuyvol"%(i+1))
            self.columns.append("%dbpri"%(i+1))
            
    def startLoop(self, idlist):

        filelist = {}
        csvlist = {}
        lasttime = {}
        lastvol = {}
        while True:
            curTime = datetime.datetime.now()
            res = common.secToMarcketOpen(curTime) - 60
            if res > 0:
                print "sleep secondes:",res
                time.sleep(res)
                continue
        	
            result = []
            if False == self.getData(idlist, result):
            	time.sleep(self.intervalSec)
            	continue

	    n = 0
            for row in result:
                id = idlist[n]
                n+=1
                
                if row is None:
                    print "get data error:",idlist[n]
                    continue
                
                tmpfolder = self.glabalFolder + id
                if os.path.exists(tmpfolder):
                    pass
                else:
                    os.mkdir(tmpfolder)
                    
                filename = tmpfolder+"/%s_%.2d%.2d%.2d.csv"%(id, curTime.year, curTime.month, curTime.day)
                
                if os.path.exists(filename):
                    if not filelist.has_key(id):
                        print "open file", filename
                        filelist[id] = open(filename, 'ab')
                        csvlist[id] = csv.writer(filelist[id])
                else:
                    if filelist.has_key(id):
                        filelist[id].close()
                    print "create file",filename
                    filelist[id] = open(filename, 'wb')
                    csvlist[id] = csv.writer(filelist[id])
                    csvlist[id].writerow(self.columns)

                #print "row=",row
                if lasttime.has_key(id):
                    if lasttime[id] == row[0]:
                        print "same time as ",lasttime[id],id
                        continue
                    row[2] == row[2] - lastvol[id]
                    
                csvlist[id].writerow(row)
                lasttime[id] = row[0]
                lastvol[id] = row[2]
                filelist[id].flush()

            time.sleep(self.intervalSec)
        
    def parse(self, oneData, realtimeData):
        #print "parse=",oneData    
        check = re.findall(r'var hq_str_([^=]*)=\"(.*)\"', oneData)
        
        stockResultArray = oneData.split("\"")
        if len(stockResultArray) <= 2:
            print "error 1"
            return False
        stockValues = stockResultArray[1].split(",")
        count=0
        if len(stockValues) >= len(sinaStockCol):
            print "stockValues[3]=", stockValues[3], type(stockValues[3])

            if stockValues[3] == "0.00" or stockValues[3] == "0.0":
                print "error 2"
                return False

            #time
            realtimeData.append(stockValues[31])
            #curprice
            realtimeData.append(float(stockValues[3]))
            #curvol
            realtimeData.append(int(stockValues[8]))
            #compete buy price
            realtimeData.append(float(stockValues[6]))
            #compete sell price
            realtimeData.append(float(stockValues[7]))
            #5sell5 vol + price -> 5sell1
            for i in range(5):
                realtimeData.append(int(stockValues[29-2*i-1]))
                realtimeData.append(float(stockValues[29-2*i]))
            for i in range(5):
                realtimeData.append(int(stockValues[10+2*i]))
                realtimeData.append(float(stockValues[10+2*i+1]))
            #print realtimeData
            
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
        #print strResult
    
        allDatas = strResult.split("\n")
        n = 0
        for oneData in allDatas:
            if oneData == "":
                break

            #print n, len(allDatas), len(comList)
            realtimeData = []
            totalData = []
            if True == self.parse(oneData, realtimeData):
                resultTable.append(realtimeData)
            else:
                resultTable.append(None)

            n+=1
            
        return True


if __name__ == "__main__":
    sinaobj = CollectSinaData(3)
    sidList = ["300078","601808","600815","600835","000858","600005","600030","600062","600396","600469","600479","601111","601398","000027","000402","000777"]
    res = sinaobj.startLoop(sidList)
    print "RESULT:",res

    
    
    
