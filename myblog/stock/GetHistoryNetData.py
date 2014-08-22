#coding=gbk
import urllib
import datetime
import sys,os
import csv
import re
from common import *
from getAllIdFromSina import *

#from pychartdir import *
#from Tkinter import *  

initYahooUrl="http://table.finance.yahoo.com/table.csv?s="

def urlcallback(a,b,c):
    return


chartcolors = ['0xcf4040', '0x40cf40','0x663300','0x9900ff','0xff0000','0xc06666ff','0x808080']

class processYahooData():
    def __init__(self):
        self.today = datetime.datetime.now()

        self.sinaIdManage = sinaIdManage()
        self.sinaIdManage.initLocalData()  
        
    def getLocalData(self, sid):
        datafolder = getLatestDataFolder()
        sfile=os.listdir(datafolder)
        for ssfile in sfile:
            print ssfile
        
    def getMissingFromYahoo(self, storeFolder):
        tmpExistStock = {}
        
        
        if os.path.isdir(storeFolder): 
            sfile=os.listdir(storeFolder)
            print sfile
            for ssfile in sfile:
                if DPshzhongzhi==ssfile[0:-4] or DPszchenzhi==ssfile[0:-4] or DPhs300==ssfile[0:-4]:
                    continue
                tmpExistStock[ssfile[0:-4]] = 1
        else:
            print "Error! %s is not dir"%(storeFolder),os.stat(storeFolder)
            return False
        
        self.getDapanData(storeFolder)
        
        newAdd = 0
        notNeedUpdate = 0
        keep = 0
        
        t1 = datetime.datetime.now()
        print "getMissingFromYahoo start,allstockmap size=",len(self.sinaIdManage.allstockmap)
        totallen = len(self.sinaIdManage.allstockmap.items())
        i = 0
        lastPerc = 0
        for item in self.sinaIdManage.allstockmap.items():
            percent = 100*i/totallen
            if percent > lastPerc:
                print "getMissingFromYahoo %%%.2d complete"%percent
            lastPerc = percent
            
            i += 1
            id = stockIDforYahoo(item[0])
            #print item[0]
            if tmpExistStock.has_key(id):
                #print "already exist", id
                keep += 1
                continue
            else:
                url = initYahooUrl + id
                subfix = id[-2:]
                #print subfix
                if subfix != 'sz' and subfix != 'ss' and subfix != 'SZ':
                    #print "not",subfix
                    notNeedUpdate += 1
                    continue
                csvfilename = "%s/%s.csv"%(storeFolder,id)     
                try:   
                    urllib.urlretrieve(url,csvfilename,urlcallback)   
                except IOError as e:
                      print "get %s error. %s"%(url, e)
                newAdd += 1   
        

        
        t2 = datetime.datetime.now()
        print "getMissingFromYahoo cost time %s. keep:%d,add:%d,unavailable:%d"\
            %(t2-t1, keep, newAdd, notNeedUpdate)
        
        return True
        
    def getDapanData(self, storeFolder):
        #get dapan data
        url = initYahooUrl + DPshzhongzhi
        csvfilename = "%s/%s.csv"%(storeFolder,DPshzhongzhi)
        urllib.urlretrieve(url,csvfilename,urlcallback)   
    
        url = initYahooUrl + DPszchenzhi
        csvfilename = "%s/%s.csv"%(storeFolder,DPszchenzhi)
        urllib.urlretrieve(url,csvfilename,urlcallback)   
        
        url = initYahooUrl + DPhs300
        csvfilename = "%s/%s.csv"%(storeFolder,DPhs300)
        urllib.urlretrieve(url,csvfilename,urlcallback)   
                    
    def updateData(self, storeFolder):
        if os.path.isdir(storeFolder): 
            pass
        else:
            return False
        
        sfile=os.listdir(storeFolder)
        
        allfolders = []
        self.today = datetime.datetime.now()
        for ssfile in sfile:
            if ssfile[0:2] == '20':
                allfolders.append(datetime.datetime.strptime(ssfile, '%Y%m%d'))
                
        newdays = sorted(allfolders)
        laststoreday = self.today
        if len(newdays) < 1:
            print "no initial data"
        else:
            laststoreday = newdays[-1]
        
            if laststoreday.year == self.today.year \
                and laststoreday.month == self.today.month \
                and laststoreday.day == self.today.day:
                
                if len(newdays) < 2:
                    print "last update day is today, nothing done"
                    return
                laststoreday = newdays[-2]            
            
        
        laststorefolder =  storeFolder + "/%.2d%.2d%.2d"%(laststoreday.year, laststoreday.month, laststoreday.day)
        todaystorefolder = storeFolder + "/%.2d%.2d%.2d"%(self.today.year, self.today.month, self.today.day)
        print "laststorefolder",laststorefolder
        if os.path.exists(todaystorefolder):
            print "today folder %s exist! "%(todaystorefolder)
        else:
            os.mkdir(todaystorefolder)   
            print "mkdir",todaystorefolder

        self.getMissingFromYahoo(laststorefolder)
        
        t1 = datetime.datetime.now()
        sfile=os.listdir(laststorefolder)
        getRecent = 0
        existNew = 0
        notGetRecent = 0
        
        totallen = len(sfile)
        i = 0
        lastPerc = 0        
        for ssfile in sfile:
            percent = 100*i/totallen
            if percent > lastPerc:
                print "update from latest sina data %%%.2d complete"%percent
            lastPerc = percent
            i += 1
                        
            id = ssfile[0:-4]

            if os.path.exists(todaystorefolder+'/'+ssfile):
                #print "exist, ",ssfile
                existNew += 1
                continue

            if DPshzhongzhi==id or DPhs300==id:
                recentData = None
            else:
                try:
                    recentData = getDayData(id[0:-3])
                except:
                    recentData = None
                if recentData == None:
                    notGetRecent += 1
                else:
                    getRecent += 1
                
            self.updateExcelData(laststorefolder+"/"+ssfile, recentData, todaystorefolder)

        t2 = datetime.datetime.now()
        print "update from latest sina data cost time %s. get:%d,getNone:%d,notNeedGet:%d"\
            %(t2-t1, getRecent, notGetRecent, existNew)
        
    def updateExcelData(self, filename, recentData, newStoreFolder):
        if filename[-3:] != "csv":
            return
        t = filename.split('/')
        storeWriteFile = newStoreFolder+'/'+t[len(t)-1]

        reader = csv.reader(open(filename, 'rb'))
        
        tmp = {}
        
        rows = []
        first = True

        for line in reader:
            if first == True:
                if line[DATE_COL_DATE] == 'Date':
                    continue
                
                if line[DATE_COL_DATE][0:2] == '<!':
                    recentData = None

                    print "error page from sina"
                    return                    

                t1 = datetime.datetime.strptime(line[DATE_COL_DATE], '%Y-%m-%d')
                
                if recentData == None:
                    delta = self.today - t1
                    if delta < datetime.timedelta(days=7):
                        print filename,"the latest update date is",t1
                    else:
                        print "strange",filename,"the latest update date is",t1
                        return
                else:
                    for item in recentData:
                        time = item[0]
                        t2 = datetime.datetime.strptime(time, '%Y-%m-%d')
                        openpri = item[1]
                        highpri = item[2]
                        closepri = item[3]
                        lowpri = item[4]
                        vol = item[5]
                        exchange = item[6]
                        
                        if t2 > t1:
                            #rows.insert(0, (time, openpri, highpri, lowpri, closepri, vol, closepri))
                            rows.append((time, openpri, highpri, lowpri, closepri, vol, closepri))
                        else:
                            tmp[time] = (openpri, highpri, lowpri, closepri, vol)
                            
                first = False

            if len(line) < 6:
                continue
            if float(line[DATE_COL_VOL]) == 0:
                #print "0 dfd", line
                continue
            
            #rows.insert(0, line)
            rows.append(line)
        
        if len(rows) > 0:
            t1 = datetime.datetime.strptime(rows[0][DATE_COL_DATE], '%Y-%m-%d')
            delta = self.today - t1
            if delta > datetime.timedelta(days=20):
                print filename," complete wrong. the latest update date is",t1
                return
        else:
            return
            
        spamWriter = csv.writer(open(storeWriteFile, 'wb'))
        for row in rows:
            spamWriter.writerow(row)
            
def getDayData(id):
    urlinit = 'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/'
    url = urlinit + id + '.phtml'
    
    sock = urllib.urlopen(url)

    htmlPage = sock.read()
    #print htmlPage
    sock.close()                     
         
    reg = "<a target='_blank'\s+href='http://vip.stock.finance.sina.com.cn/.*&date=\d{4}-\d{2}-\d{2}'>\s*([^\s]+)\s+</a>\s*</div></td>\s*<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+"
    items = re.findall(reg, htmlPage)
    if items:
        return items
    else:
        #print "none match"
        return None
    
            
if __name__ == "__main__":     
    yahoo = processYahooData()
    yahoo.updateData(gOrigDataFolder)


