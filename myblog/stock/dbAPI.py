#coding=gbk
import MySQLdb
import time
import datetime
import getAllIdFromSina

DBCOL_NAMELIST = ['date','time','openpri','curpri','highpri','lowpri',\
                  'comp_buy','comp_sell','exch_vol','exch_amount','1buy_vol','1buy_pri'\
                  ,'2buy_vol','2buy_pri','3buy_vol','3buy_pri','4buy_vol','4buy_pri','5buy_vol','5buy_pri'\
                  ,'1sell_vol','1sell_pri','2sell_vol','2sell_pri','3sell_vol','3sell_pri'\
                  ,'4sell_vol','4sell_pri','5sell_vol','5sell_pri','id']
SQL_TABLE_COL=['date','time','float','float','float','float',\
               'float','float','int','float','int','float',\
               'int','float','int','float','int','float','int','float',\
               'int','float','int','float','int','float',\
               'int','float','int','float','int primary key auto_increment']
DBCOL_DATE = 0
DBCOL_TIME = 1
DBCOL_OPEN_PRI = 2
DBCOL_CUR_PRI = 3
DBCOL_HIGH_PRI = 4
DBCOL_LOW_PRI = 5
DBCOL_COMP_BUY_PRI = 6
DBCOL_COMP_SELL_PRI = 7
DBCOL_EXCH_VOL = 8
DBCOL_EXCH_AMOUNT = 9
DBCOL_BUY1_VOL = 10
DBCOL_BUY1_PRI = 11
DBCOL_BUY2_VOL = 12
DBCOL_BUY2_PRI = 13
DBCOL_BUY3_VOL = 14
DBCOL_BUY3_PRI = 15
DBCOL_BUY4_VOL = 16
DBCOL_BUY4_PRI = 17
DBCOL_BUY5_VOL = 18
DBCOL_BUY5_PRI = 19
DBCOL_SELL1_VOL = 20
DBCOL_SELL1_PRI = 21
DBCOL_SELL2_VOL = 22
DBCOL_SELL2_PRI = 23
DBCOL_SELL3_VOL = 24
DBCOL_SELL3_PRI = 25
DBCOL_SELL4_VOL = 26
DBCOL_SELL4_PRI = 27
DBCOL_SELL5_VOL = 28
DBCOL_SELL5_PRI = 29
DBCOL_AUTO_ID = 30

OLD_TABLE_PREFIX="sid_"
NEW_TABLE_PREFIX="stock_"
#大盘数据： 指数名称，当前点数，当前价格，涨跌率，成交量（手），成交额（万元）

#600、601开头上证A股
#000、001开头深证A股
#400、420、430开头三板A股。400、420为两个交易所的退市股票。430为中关村股票，是国家为扶持高科技企业圈钱而放到三板交易的。三板股票仅周五交易，有帐户就能买，单风险极大
#002开头中小股。是A股一种，盘子小、深交所上市
#900开头上证B股
#200开头深证B股
def stockIDforSina(id):
    strId = str(id)
    if strId[0:3] == "600" or strId[0:3] == "601" or strId[0:3] == "900":
        return "sh"+strId
    elif strId[0:3] == "000" or strId[0:3] == "001" or strId[0:3] == "200" or strId[0:3] == "300":
        return "sz"+strId
    elif strId[0:3] == "002":
        return "sz"+strId  
    else:
        return strId

class BaseDB():
    def __init__(self, dbname="stockdata"):
        
        self.tablePrefix = NEW_TABLE_PREFIX
        self.db = dbname
        self.connect()
        
    def connect(self):
        self.conn=MySQLdb.connect(host="localhost",user="root",passwd="iamtaohui",db=self.db,unix_socket='/data/mysql/mysql.sock')
        self.isConnected = True
        self.cursor = self.conn.cursor()  
        
    def close(self):
        if self.isConnected:
            self.conn.close()
            self.cursor.close()
            self.isConnected = False
            
    def setTablenamePrefix(self, prefix):
        self.tablePrefix = prefix
        
    def __del__(self):
        self.close()

class getStockIdDB(BaseDB):
    def __init__(self):
        BaseDB.__init__(self)

        self.conn.select_db('blog');  
        self.cursor = self.conn.cursor() 
        
    def getAllSid(self): 
        count = self.cursor.execute('select stockId from stock_ownerstocks;')
        results = self.cursor.fetchall()
        return results
        
class stockDB(BaseDB):
    def __init__(self):
        BaseDB.__init__(self)
        
        try:
            self.cursor.execute("""create database if not exists stockdata""")
        except:
            pass
        insertCols = "("
        for i in range(len(DBCOL_NAMELIST)-1):
            insertCols += "%s,"%(DBCOL_NAMELIST[i])
        
        self.insertCols = insertCols[0:-1]+')'
              
        self.conn.select_db('stockdata');  
        self.cursor = self.conn.cursor()  
        
    def createTable(self, id):
        tablename = self.tablePrefix+id
        sqlcols = ""
        for i in range(len(DBCOL_NAMELIST)):
            sqlcols += "%s %s,"%(DBCOL_NAMELIST[i], SQL_TABLE_COL[i])
        sqlcols += "key(%s,%s)"%(DBCOL_NAMELIST[0],DBCOL_NAMELIST[1])
        createsql = "create table if not exists %s(%s) "%(tablename, sqlcols)
        
        try:
            print self.cursor.execute(createsql)
        except Exception, e:
            #print "createsql",createsql,e
            return False
        
        return True
        
    def dropTable(self, id):
        tablename = self.tablePrefix+id
        self.cursor.execute("drop table %s"%(tablename))
        self.conn.commit()
        
    def getLastDate(self, id):
        count = self.getLineCount(id)
        if count > 0:
            sql = "select date,time from %s limit %d,%d"%(self.tablePrefix+id,count-1,count)
            n = self.cursor.execute(sql)
            row = self.cursor.fetchone()
            d = str(row[0])+" "+str(row[1])
            dd=datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S')
            return dd
        
        return None
            
    def getLineCount(self, id):
        sql = "select count(*) from %s"%(self.tablePrefix+id)  
        n = self.cursor.execute(sql)
        row = self.cursor.fetchone()
        #print "getLineCount id %s has %d rows"%(id, n),row
        
        return row[0]
    
     
    def insertStock(self, id, items):
        insertStockSql = "insert into %s"%(self.tablePrefix+id)

        sql = insertStockSql+self.insertCols+''' values(\
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\
)'''        

        try:
            n = self.cursor.execute(sql, items)
        except Exception, e:
            print insertStockSql
            print e,sql
            return False

        self.conn.commit()
        
        return True
        
    def getAllData(self, id):
        sql = "select * from %s"%(self.tablePrefix+id)  

        try:
            count = self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print "getAllData except", e
            return None
        
        return rows     
    
    def getDayData(self, id,day):
        sql = "select * from %s where date='%s'"%(self.tablePrefix+id,day)    
        print sql
        try:
            count = self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print "getDayData except", e
            return None
        
        return rows   
       
    def getAllDate(self, id):
        sql = "select distinct date from %s"%(self.tablePrefix+id)    

        try:
            count = self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print "getAllData except", e
            return None

        return rows

def moveData(old, new):
    dbobj = getStockIdDB()
    rows = dbobj.getAllSid()

    sdb = stockDB()
    newdb = stockDB()
    newdb.setTablenamePrefix(NEW_TABLE_PREFIX)
    for row in rows:
        id = str(row[0])
        print id
        #sdb.getLastDate(str(row[0]))
        newdb.dropTable(id)
        newdb.createTable(id)
        lines = sdb.getAllData(id)
        print len(lines)
        lastDate = None
        n = 0
        newrows = []
        recordDic = {}
        for line in lines:
            d = str(line[DBCOL_DATE])+" "+str(line[DBCOL_TIME])
            dd=datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S')
            if lastDate == None:
                pass
            else:
                if dd == lastDate:
                    if not recordDic.has_key(dd):
                        recordDic[dd] = 0
                    else:
                        recordDic[dd]+=1
                    #print "Error:",dd,lastDate,n
                elif dd < lastDate:
                    print dd,lastData,"Error"
                else:
                    newrows.append(line)
                    
            lastDate = dd
            n+=1
            
        print id, len(newrows),len(lines)
        for k,v in recordDic.items():
            if v > 0:
                print k,v
        
        for newdata in newrows:        
            newdb.insertStock(id, newdata)
        #newdb.createTable(id)
        
def createAllTable():
    a = getAllIdFromSina.sinaIdManage()
    #a.initFromSinaHy()
    a.initLocalData()
    newdb = stockDB()
    newAdds = []
    for id,v in a.allstockmap.items():

        if newdb.createTable(id):
            count = newdb.getLineCount(id)
            newAdds.append(id)
    print "createTable success:", newAdds
        
if __name__ == "__main__":
    dbobj = getStockIdDB()
    rows = dbobj.getAllSid()
    
    createAllTable()

    for row in rows:
        id = str(row[0])
        
        #newdb.dropTable(id)
        


    


 