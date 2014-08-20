#coding=gbk

import urllib2,re,os
from common import *


class sinaIdManage():
    def __init__(self):
        datafolder = "%s/hy"%globalTopFolder
        self.allstockFilename = "%s/allstocks.txt"%globalTopFolder
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
        print "html=",html
        sids = re.findall(r"code:\"([^\"]+)\",name:\"([^\"]+)\"[^}]+,pb:([^,]+),mktcap:([^,]+),nmc:([^,]+)", html)

        return sids
         
    def initFromSinaHy(self):
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
                print len(cont)
                
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
                        while hynum > (page-1)*onepagenum:
                            sids = self.getOneSinaHy(hyid, page, onepagenum)
                            
                            if sids != None:
                                print len(sids)
                                print "tt",sids
                                for sitem in sids:
                                    sid = sitem[0]
                                    sname = sitem[1]
                                    pb = sitem[2]
                                    mktcap = sitem[3]
                                    nmc = sitem[4]
                                    print sid, sname, pb, mktcap, nmc
                                    oneHyIdMap[sid] = sname
                                    self.allstockmap[sid] = (sname, pb, mktcap, nmc)
                                
                            page+=1
    
                        trytime += 1
                        if len(oneHyIdMap) < hynum:
                            print "not equel", len(oneHyIdMap) ,hynum
                            continue
                        else:
                            print "equal",hynum      
                            break
                    
                    fhy = open("%s/%s.txt"%(self.sinahyFolder, hyname), 'w')
                    for s in oneHyIdMap.items():
                        fhy.write("%s\n"%s[0])        
                    fhy.close()
                
                fCurSinaHy.close()
                    
        print "total:",len(self.allstockmap)
        for s in self.allstockmap.items():
            pb, mktcap, nmc = s[1][1],s[1][2],s[1][3]
            if pb[0] == '"':
                pb = pb[1:-1]
            if mktcap[0] == '"':
                mktcap = mktcap[1:-1]
            if nmc[0] == '"':
                nmc = nmc[1:-1]
            print s[0],s[1][0],s[1][1],s[1][2],s[1][3]
            fAllStocks.write("%s:%s:%s:%s:%s\n"%(s[0],s[1][0],pb, mktcap, nmc))
        fAllStocks.close()
    
    def initLocalData(self):
        f = open(self.allstockFilename,'r')
        lines = f.readlines()
        for line in lines:
            if line[-1] == '\n':
                line = line[0:-1]
            #print line
            t = line.split(':')
            self.allstockmap[str(t[0])] = (t[1],float(t[2]),float(t[3]),float(t[4]))
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
    a.initFromSinaHy()
    #a.initLocalData()
    
