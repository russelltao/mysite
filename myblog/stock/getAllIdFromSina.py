#coding=gbk

import urllib2,re,os
from common import *


HYCOL_ID = 0
HYCOL_NAME = 1
HYCOL_NUM = 2
HYCOL_RISE_VALUE = 3
HYCOL_RISE_RATE = 4

SCOL_NAME = 0
SCOL_PB = 1
SCOL_MKTCAP = 2
SCOL_NMC = 3
SCOL_PER = 4
SCOL_TURNOVERRATIO = 5


logging.basicConfig(filename = os.path.join(os.getcwd(), __file__[__file__.rfind('\\')+1:-3]+'.log'), \
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
                    level = logging.INFO)  
log = logging.getLogger('root')



class sinaIdManage():
    def __init__(self):
        datafolder = "%s/hy"%globalTopFolder
        self.allstockFilename = "%s/allstocks.txt"%globalTopFolder
        log.info("sinaIdManage allstockFilename:%s"%self.allstockFilename)
        self.curhyFilename = "%s/curhy.txt"%datafolder
        self.sinahyFolder = "%s/sina"%datafolder
        self.allstockmap = {}
        self.sToHyMap = {}
        self.hyToSMap = {}
        self.hyNameList = []
        try:
            os.makedirs(datafolder)
        except:
            pass
        try:
            os.makedirs(self.sinahyFolder)
        except:
            pass    
            
    def getOneSinaHy(self, hyid, pagenum=1, onepagenum=80):
        url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%d&num=%d&sort=symbol&asc=1&node=%s&_s_r_a=page'%(pagenum, onepagenum, hyid)
        response = urllib2.urlopen(url)
    
        html = response.read()  
        #print "html=",html
        '''
        {symbol:"sh600089",code:"600089",name:"特变电工",trade:"10.160",pricechange:"-0.160",changepercent:"-1.550",buy:"10.150",sell:"10.160",settlement:"10.320",open:"10.260",high:"10.350",low:"10.150",volume:"30421096",amount:"311046848",ticktime:"12:19:12",per:20.159,pb:1.717,mktcap:3291975.824976,nmc:3216567.593776,turnoverratio:0.96089}
        '''
        sids = re.findall(r"code:\"([^\"]+)\",name:\"([^\"]+)\"[^}]+,per:([^,]+),pb:([^,]+),mktcap:([^,]+),nmc:([^,]+),turnoverratio:([^,}]+)", html)

        return sids,html,url
         
    def initFromSinaHy(self):
        log.info('start to initFromSinaHy %s'%(datetime.datetime.now()))

        t1 = datetime.datetime.now()
        url = 'http://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php'
        response = urllib2.urlopen(url)
    
        html = response.read()
        #print html   

        cont = re.findall(r"\"([^\"]+)\":\"([^\"]+)\"", html)
        if cont != None:
            if len(cont) == 0:
                print "safe error response:",cont
                return None
            else:
                #print len(cont)
                log.info('open idfile %s'%self.allstockFilename)
                fAllStocks = open(self.allstockFilename,'w')
                fCurSinaHy = open(self.curhyFilename,'w')
                
                for t in cont:
                    print "t[1]=",t[1]
                    hyitems = re.findall(r"([^,]+)", t[1])
                    hyid = hyitems[0]
                    hyname = hyitems[1]
                    hynum = int(hyitems[2])
                    hyZhangValue = hyitems[4]
                    hyZhangRate = hyitems[5]
                    onepagenum = 80
                    
                    fCurSinaHy.write("%s %s %d %s %s\n"%(hyid,hyname,hynum,hyZhangValue,hyZhangRate))
                    
                    print "hyid=",hyid, "hyname=",hyname, "hynum=",hynum
                    oneHyIdMap = {}
                    
                    trytime = 0
                    while trytime < 3:
                        page = 1
                        responseList = []
                        while hynum > (page-1)*onepagenum:
                            sids, response, url = self.getOneSinaHy(hyid, page, onepagenum)
                            
                            if sids != None:
                                #print len(sids)
                                #print "tt",sids
                                for sitem in sids:
                                    sid = sitem[0]
                                    sname = sitem[1]
                                    per = sitem[2]
                                    pb = sitem[3]
                                    mktcap = sitem[4]
                                    nmc = sitem[5]
                                    turnoverratio = sitem[6]
                                    #print sid, sname, pb, mktcap, nmc, per, turnoverratio
                                    oneHyIdMap[sid] = sname
                                    self.allstockmap[sid] = (sname, pb, mktcap, nmc, per, turnoverratio)
                                responseList.append((response, len(sids), url))
                                
                            page+=1
    
                        trytime += 1
                        if len(oneHyIdMap) < hynum:
                            log.debug("%d not equal %d"%(len(oneHyIdMap) ,hynum))
                            for r in responseList:
                                log.debug("url:%s, parse %d, html=%s"%(r[2], r[1],r[0]))
                            continue
                        else:
                            log.info("equal %s", hynum)  
                            break
                    
                    fhy = open("%s/%s.txt"%(self.sinahyFolder, hyname), 'w')
                    for s in oneHyIdMap.items():
                        fhy.write("%s\n"%s[0])        
                    fhy.close()
                
                fCurSinaHy.close()
                    
        try:
            log.info('allstockmap length:%d'%len(self.allstockmap))
            for s in self.allstockmap.items():
                pb, mktcap, nmc, per, turnoverratio = s[1][1],s[1][2],s[1][3],s[1][4],s[1][5]
                if pb[0] == '"':
                    pb = pb[1:-1]
                if mktcap[0] == '"':
                    mktcap = mktcap[1:-1]
                if nmc[0] == '"':
                    nmc = nmc[1:-1]
                if per[0] == '"':
                    per = per[1:-1]
                if turnoverratio[0] == '"':
                    turnoverratio = turnoverratio[1:-1]
                log.debug("write line:%s:%s:%s:%s:%s:%s:%s"%(s[0],s[1][0],pb, mktcap, nmc, per, turnoverratio))

                fAllStocks.write("%s:%s:%s:%s:%s:%s:%s\n"%(s[0],s[1][0],pb, mktcap, nmc, per, turnoverratio))
        except Exception,e:
            log.error('write allstockfile exception:%s'%e)

        fAllStocks.close()
        
        t2 = datetime.datetime.now()
        print "initFromSinaHy excecute cost:",t2-t1
    
    def initLocalData(self):
        f = open(self.allstockFilename,'r')
        lines = f.readlines()
        print "initLocalData lines=",len(lines)
        for line in lines:
            if line[-1] == '\n':
                line = line[0:-1]
            #print line
            t = line.split(':')

            try:
                self.allstockmap[str(t[0])] = (t[1],float(t[2]),float(t[3]),float(t[4]),float(t[5]),float(t[6]))
            except Exception,e:
                log.error('initLocalData read id %s error, line=%s'%(t[0], line)) 
        f.close()
        
        self.getSinaHy(self.sToHyMap, self.hyToSMap, self.hyNameList)
        print "total sid:",len(self.allstockmap)
             
    def getSinaHy(self, sToHyMap, hyToSMap, hyNameList):
        sfiles = os.listdir(self.sinahyFolder)
        regex = '(\d{6})[^\n]*'
        i = 0
        for sfile in sfiles:
            #print sfile
            hyNameList.append(sfile[0:-4])
            f = open(self.sinahyFolder+'/'+sfile)
            c = f.read()
            #print c
            items = re.findall(regex, c)
            
            if items:
                hyToSMap[i] = []
                for item in items:
                    
                    #print item
                    sToHyMap[item] = i
                    hyToSMap[i].append(item)
        
            f.close()
            
            i += 1        
        
if __name__ == '__main__':
    a = sinaIdManage()
    
    a.initLocalData()
    a.initFromSinaHy()
    print len(a.sToHyMap), len(a.hyToSMap), len(a.hyNameList), len(a.allstockmap), 
    
    #for k,v in a.allstockmap.items():
        #print k,v
    
