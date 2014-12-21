#coding=gbk

import urllib2,re,os
from common import *
import getAllIdFromSina
import socket
from dbAPI import BaseDB
socket.setdefaulttimeout(3)

logging.basicConfig(filename = os.path.join(os.getcwd(), __file__[__file__.rfind('\\')+1:-3]+'.log'), \
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
                    level = logging.INFO)  
log = logging.getLogger('root')


DBCOL_NAME_BIG_HOLDERS = ['id','stockid','endtime','rank','name','count','rate','type']
DBCOL_NAME_HOLDER_INFO = ['id','stockid','endtime','pubtime','totalcount','avgcount']

DBCOL_TYPE_BIG_HOLDERS=['int primary key auto_increment','char(6)','date','int','char(50)','int','float','char(20)']
DBCOL_TYPE_HOLDER_INFO=['int primary key auto_increment','char(6)','date','date','int','int']

class SinaStockDetail(BaseDB):
    def __init__(self):
        self.urlStockHolder = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/%s.phtml'
        BaseDB.__init__(self, 'stockinfo')

        self.conn.select_db('stockinfo');  
        self.cursor = self.conn.cursor() 
        
        self.tblnameBigHolders = 'bigholders'
        self.tblnameHolderStats = 'holderstats'
        
        insertCols = "("
        for i in range(len(DBCOL_NAME_BIG_HOLDERS)-1):
            insertCols += "%s,"%(DBCOL_NAME_BIG_HOLDERS[1+i])
        
        self.insertSqlBigHolders = insertCols[0:-1]+')'
        
        insertCols = "("
        for i in range(len(DBCOL_NAME_HOLDER_INFO)-1):
            insertCols += "%s,"%(DBCOL_NAME_HOLDER_INFO[1+i])
        
        self.insertSqlHolderStats = insertCols[0:-1]+')'
        
    def createTable(self): 
        tablename = self.tblnameBigHolders
        sqlcols = ""
        for i in range(len(DBCOL_NAME_BIG_HOLDERS)):
            sqlcols += "%s %s,"%(DBCOL_NAME_BIG_HOLDERS[i], DBCOL_TYPE_BIG_HOLDERS[i])
        sqlcols += "key(%s,%s)"%(DBCOL_NAME_BIG_HOLDERS[1],DBCOL_NAME_BIG_HOLDERS[2])
        createsql = "create table if not exists %s(%s) "%(tablename, sqlcols)
        
        try:
            print self.cursor.execute(createsql)
        except Exception, e:
            #print "createsql",createsql,e
            return False
        
        tablename = self.tblnameHolderStats
        sqlcols = ""
        for i in range(len(DBCOL_NAME_HOLDER_INFO)):
            sqlcols += "%s %s,"%(DBCOL_NAME_HOLDER_INFO[i], DBCOL_TYPE_HOLDER_INFO[i])
        sqlcols += "key(%s,%s)"%(DBCOL_NAME_HOLDER_INFO[1],DBCOL_NAME_HOLDER_INFO[2])
        createsql = "create table if not exists %s(%s) "%(tablename, sqlcols)
        
        try:
            print self.cursor.execute(createsql)
        except Exception, e:
            #print "createsql",createsql,e
            return False
        
        return True
        
    def insertBigHolders(self, items):
        insertStockSql = "insert into %s"%(self.tblnameBigHolders)

        sql = insertStockSql+self.insertSqlBigHolders+''' values(%s,%s,%s,%s,%s)'''        

        try:
            n = self.cursor.execute(sql, items)
        except Exception, e:
            print insertStockSql
            print e,sql
            return False

        self.conn.commit()
        
        return True
    def insertHolderStats(self, items):
        insertStockSql = "insert into %s"%(self.tblnameHolderStats)

        sql = insertStockSql+self.insertSqlHolderStats+''' values(%s,%s,%s,%s,%s,%s,%s)'''        

        try:
            n = self.cursor.execute(sql, items)
        except Exception, e:
            print insertStockSql
            print e,sql
            return False

        self.conn.commit()
        
        return True
    
    def getUrlResponse(self, url):
        try:
            response = urllib2.urlopen(url)
        except Exception,e:
            print 'getUrlResponse error',e
            return None
    
        content = response.read()
        return content
        
    def getStockHolder(self, sid):
        '''主要股东
        http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/600815.phtml
        数据格式：
        <table width="100%" id="Table1">
        。。。
<tbody>
            <tr>
                <td width="15%"><a name="2014-06-30"></a><div align="center"><strong>截至日期</strong></div></td>
                <td colspan="4">2014-06-30</td>
            </tr>
            <tr>
                <td><div align="center"><strong>公告日期</strong></div></td>
                <td colspan="4">2014-08-30</td>
            </tr>
            <tr>
                <td><div align="center"><strong>股东总数</strong></div></td>
                <td colspan="4">68838<a href="/corp/go.php/vCI_StockHolderAmount/code/600815/type/amount.phtml" target="_blank">查看变化趋势</a></td>
            </tr>
            <tr>
                <td><div align="center"><strong>平均持股数</strong></div></td>
                <td colspan="4">
                    13932股(按总股本计算)                    <a href="/corp/go.php/vCI_StockHolderAmount/code/600815/type/average.phtml" target="_blank">查看变化趋势</a>
                </td>
            </tr>
            <tr>
                <td><div align="center"><strong>编号</strong></div></td>
                <td width="40%"><div align="center"><strong>股东名称</strong></div></td>
                <td width="15%"><div align="center"><strong>持股数量(股)</strong></div></td>
                <td width="15%"><div align="center"><strong>持股比例(%)</strong></div></td>
                <td width="15%"><div align="center"><strong>股本性质</strong></div></td>
            </tr>
                        <tr >
              <td><div align="center">1</div></td>
              <td><div align="center"><a href="/corp/view/vCI_HoldStockState.php?stockid=600815&stockholderid=80002449" target="_blank">厦门海翼集团有限公司</a></div></td>
              <td><div align="center"><a href="/corp/view/vCI_StockHolderAmount.php?stockid=600815&type=holdstocknum&code=80002449" target="_blank">393023000</a>&nbsp;</div></td>
              <td><div align="center"><a href="/corp/view/vCI_StockHolderAmount.php?stockid=600815&type=holdstockproportion&code=80002449" target="_blank">40.98</a>&nbsp;</div></td>
              <td><div align="center">流通A股</div></td>
              </tr>

        '''
        html = self.getUrlResponse(self.urlStockHolder%(sid))
        if html == None:
            return False
        
        cont = re.findall(r'<table[^T]*Table1">((<(?!/?table)[^>]*>|[^<>]*)*)</table>', html)

        if len(cont) == 0:
            print "no match table"
            return False

        tbody = re.findall(r'<tbody>((<(?!/?tbody)[^>]*>|[^<>]*)*)</tbody>', cont[0][0])
        if len(cont) == 0:
            print "no match tbody"
            return False
        
        log.debug("tbody=%s"%tbody[0][0])
        trs = re.findall(r'(<tr>|<tr >|<tr class="tr_2">)((<(?!/?tr)[^>]*>|[^<>]*)*)</tr>', tbody[0][0])
        
        totalTrLen = len(trs)
        print "totalTrLen",totalTrLen
        i = 0
        while i<totalTrLen-4:
            
            endTime = self.getEndTime(trs[i][1])      
            pubTime = self.getPubTime(trs[i+1][1])
            holdersCount = self.getHoldersCount(trs[i+3][1])
            avgStockCount = self.getAvgStockCount(trs[i+4][1])
            
            #self.insertHolderStats((endTime, pubTime, holdersCount, avgStockCount))
            
            i+=6
            for j in range(20):
                if i >= totalTrLen:
                    break
                
                bigHolder = self.getBigHolder(trs[i][1], 1+j)
                if bigHolder != None:
                    i+=1
                    name = bigHolder[0]
                    if '&nbsp;' == bigHolder[1][-6:]:
                        count = int(bigHolder[1][0:-6])
                    else:
                        count = int(bigHolder[1])
                    ratio = float(bigHolder[2])
                    types = bigHolder[3]
                    print "%dth: name=%s,count=%s,ratio=%s,type=%s"%(1+j, name,count,ratio,types)
                else:
                    break
                
            
            print "i=%d;endTime=%s;pubTime=%s;holdersCount=%s;avgStockCount=%s;"%(i,endTime, pubTime, holdersCount, avgStockCount)

            i+=1
            
        return True
    
    def getEndTime(self, tr):
        tds = re.findall(r'<td width="15%"><a name="([^\"]+)"></a><div align="center"><strong>截至日期</strong></div></td>', tr)
        if len(tds) > 0:
            return tds[0]
        else:
            log.warn("getEndTime Failed!"+tr)
            return None
        
    def getPubTime(self, tr):
        tds = re.findall(r'<td colspan="4">([^<]+)</td>', tr)
        if len(tds) > 0:
            return tds[0]
        else:
            log.warn("getPubTime Failed!"+tr)
            return '-'
        
    def getHoldersCount(self, tr):
        tds = re.findall(r'<td colspan="4">(\d+)<a', tr)
        count = -1
        if len(tds) > 0:
            count = int(tds[0])
        else:
            log.warn("getHoldersCount Failed!"+tr)
        return count
        
    def getAvgStockCount(self, tr):
        count = -1
        tds = re.findall(r'<td colspan="4">[^\d<]*(\d+)', tr)
        if len(tds) > 0:
            count = int(tds[0])
        else:
            log.warn("getAvgStockCount Failed!"+tr)
        return count
        
    def getBigHolder(self, tr, i):
        regexStr = r'<td><div align="center">%d</div></td>\s*<td><div align="center">(<a[^>]*>|)([^<]*)(</a>|)</div></td>\s*<td><div align="center">(<a[^>]*>|)([^<]*)(</a>|)[^<]*</div></td>\s*<td><div align="center">(<a[^>]*>|)([^<]*)(</a>|)[^<]*</div></td>\s*<td><div align="center">([^<]*)</div></td>'%i
        tds = re.findall(regexStr, tr)
        if len(tds) > 0:
            return (tds[0][1],tds[0][4],tds[0][7],tds[0][9])
        else:
            log.warn("getBigHolder Failed!"+tr+" regex="+regexStr+" tds=%d"%len(tds))
            return None
        
if __name__ == '__main__':

    idManager = getAllIdFromSina.sinaIdManage()
    a = SinaStockDetail()
    #a.createTable()
    idManager.initLocalData()
    for k,v in idManager.allstockmap.items():
        a.getStockHolder(k)
        #break
    
    

