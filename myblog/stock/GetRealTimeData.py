#coding=gbk
import ADline,licaizhe
from common import *
#import threading, thread
import time, getCurDataFromSina
from getAllIdFromSina import *



class realtime():
    def __init__(self):
        self.getLastJiaoyiri()
        self.goodStocks = {}
        self.sinaobj = getCurDataFromSina.sinaStockAPI()
        self.licai = licaizhe.licaizhe()
    
        self.sinaIdManage = sinaIdManage()
        self.sinaIdManage.initLocalData()  
            
    def getLastJiaoyiri(self):
        t = datetime.datetime.now()
        t -= datetime.timedelta(days=1)
        while isJiaoyiri(t) != True:
            t -= datetime.timedelta(days=1)
            
        self.lastJiaoyiri = t
    
    def initPast(self):
        storeFolder = getLatestDataFolder()
        i = 0
    
        if os.path.isdir(storeFolder): 
            sfile=os.listdir(storeFolder)
        else:
            return
        
        total = len(sfile)
        lastPercent = 0

        for ssfile in sfile:
            sid = ssfile[0:-7]
            if DPshzhongzhi==ssfile[0:-4] or DPszchenzhi==ssfile[0:-4] or DPhs300==ssfile[0:-4]:
                continue        

            i+=1

            perc = 100*i/total
            if perc > lastPercent:
                print "%%%d complete"%perc
                lastPercent = perc
                
            if self.licai.datamap.has_key(sid):
                pass
            else:
                continue
            
            safe = self.licai.datamap[sid][0]
            jgkp = self.licai.datamap[sid][1]
            if safe <= 0:
                continue
            elif safe <= 3:
                pass
            else:
                continue

            fname = storeFolder + "/%s"%ssfile
            
            reader = csv.reader(open(fname, 'rb'))
        
            listTime,listOpen,listClose,listHigh,listLow,listVol = [],[],[],[],[],[]
            j = 0
            pDay = -1
            for row in reader:
                if re.match(r'\d{4}-\d+-\d+', row[DATE_COL_DATE]) == None:
                    continue
    
                thisDate = datetime.datetime.strptime(row[DATE_COL_DATE], '%Y-%m-%d')
                if j == 0:
                    if thisDate.day >= self.lastJiaoyiri.day \
                    and thisDate.month == self.lastJiaoyiri.month \
                    and thisDate.year == self.lastJiaoyiri.year:
                        pDay = j
                    else:
                        print "last day no data!",sid,thisDate
                        break
                    
                j+=1
                    
                listTime.insert(0, thisDate)
                listOpen.insert(0, float(row[DATE_COL_OPEN]))
                listClose.insert(0, float(row[DATE_COL_CLOSE]))
                listHigh.insert(0, float(row[DATE_COL_HIGH]))
                listLow.insert(0, float(row[DATE_COL_LOW]))
                listVol.insert(0, float(row[DATE_COL_VOL]))
        
            if pDay == -1 or j < 60:
                continue
            
            s = ADline.stock(sid)
            s.initData(listTime, listOpen, listClose, listHigh, listLow, listVol)
            if s.checkAboveAveLine(j-1) == False:
                continue
             
            value = s.checkLatestNormalDays(j-1)
            if value == 0:
                continue
            
            lines = s.getADline()
            if 0 == float(lines[0]):
                continue
            
            self.goodStocks[sid] = (safe,jgkp,float(lines[0]),float(lines[1]),value)


        i = 0
        for colstock in self.goodStocks.items():
            i+=1
            print "good: ",i, colstock
            if self.sinaIdManage.sToHyMap.has_key(colstock[0]):
                print self.sinaIdManage.hyNameList[self.sinaIdManage.sToHyMap[colstock[0]]]

        print "total:",i

        
    def realtimeRun(self):
        while True:
            t = datetime.datetime.now()
            
            if isJiaoyishijian(t) == True:
                sidList = []
                for colstock in self.goodStocks.items():
                    sidList.append(colstock[0])
                res = self.sinaobj.getCurPriFromSina(sidList)
                i = 0

                if res == None:
                    print "get sina None!",len(sidList)
                else:
                    print "---------------%s-----------------------"%t
                    showmap = {}
                    for pri in res:
                        if pri == None:
                            continue
                        
                        curpri = float(pri[2])
                        
                        if curpri > self.goodStocks[sidList[i]][2]:
                            hyid = self.sinaIdManage.sToHyMap[sidList[i]]
                            if showmap.has_key(hyid):
                                pass
                            else:
                                showmap[hyid] = []
                                
                            value = self.goodStocks[sidList[i]]
                            showmap[hyid].append((sidList[i], value, pri))
                            

                        i+=1
                    
                    for sitem in showmap.items():
                        slist = sitem[1]
                        hyid = sitem[0]
                        self.checkLocalHY(hyid)  
                        
                        for slistitem in slist:
                            sid = slistitem[0]
                            value = slistitem[1]
                            pri = slistitem[2]
                            curpri = float(pri[2])
                            lastclose = float(pri[1])
                            todayopen = float(pri[0])
                            high = float(pri[3])
                            low = float(pri[4])          
                                       
                            print "sid=%s,safe=%d,jgkp=%d,curpri=%.2f,attack=%f,attaoccu=%d,latestnorm=%d,inc=%%%.2f,lastclose=%.2f,todayopen=%.2f,high=%.2f,low=%.2f"%\
                            (sid, value[0], value[1], curpri, value[2], value[3], value[4],100*(curpri-todayopen)/todayopen,lastclose,todayopen,high,low)         
                            
            
            time.sleep(60)

        
    def checkLocalHY(self, hyid):
        getSlist = self.sinaIdManage.hyToSMap[hyid]
        #print "len hy:",len(getSlist)
        res = self.sinaobj.getCurPriFromSina(getSlist)
        if res == None or len(getSlist) > len(res):
            print self.sinaIdManage.hyNameList[hyid],"checkLocalHY get sina None!!"
            return
        i = 0
        
        slist = []
        totalPerc = float(0)
        for pri in res:
            if pri == None:
                i+=1
                continue
            if len(pri) < 5:
                #print "Error get pri:",getSlist[i]
                i+=1
                continue
            curpri = float(pri[2])
            lastclose = float(pri[1])
            todayopen = float(pri[0])
            high = float(pri[3])
            low = float(pri[4])
            
            if todayopen == 0:
                i+=1
                continue
            
            perc = 100*(curpri-todayopen)/todayopen
            totalPerc += perc
            slist.append((getSlist[i], float(perc)))
            i+=1
            

        sortedlist = sorted(slist, key=lambda student: student[1])
        print self.sinaIdManage.hyNameList[hyid],len(sortedlist),"average: ",totalPerc/i,"1:%s %.2f;"%sortedlist[-1],"2:%s %.2f;"%sortedlist[-2],"3:%s %.2f;"%sortedlist[-3]


if __name__ == "__main__":
    
    rt = realtime()
    t = datetime.datetime.now()
    rt.initPast()
    t2 = datetime.datetime.now()
    print "init past cost time:",t2-t
    rt.realtimeRun()
    
    