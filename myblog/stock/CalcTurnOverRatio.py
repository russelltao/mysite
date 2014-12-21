#coding=gbk

import re,os
from common import *
import getAllIdFromSina
from ReadLocalData import ReadLocalData
from dbAPI import BaseDB
import datetime


RATE_COL_ID = 0
RATE_COL_LONGRATE = 1
RATE_COL_MIDRATE = 2
RATE_COL_SHORTRATE = 3
RATE_COL_LASTRATE = 4
RATE_COL_TOTAL_NUM = 5
RATE_COL_MKTCAP = 6
RATE_COL_LASTDAY = 7
RATE_COL_0PRI = 8
RATE_COL_1PRI = 9
RATE_COL_2PRI = 10
RATE_COL_3PRI = 11

DBCOL_NAME_TURNOVER_RATE = ['id','stockid','longrate','midrate','shortrate','lastrate','totalcount','mktcap','lastday','pri0','pri1','pri2','pri3']

DBCOL_TYPE_TURNOVER_RATE = ['int primary key auto_increment','char(6)','float','float','float','float','int','float','date','float','float','float','float',]

class CalcTurnOverRate(BaseDB):
    def __init__(self):
        self.localDataObj = ReadLocalData()
        self.longDayNum = 90
        self.middleDayNum = 60
        self.shortDayNum = 30
       
        BaseDB.__init__(self, 'stockinfo')

        self.conn.select_db('stockinfo');  
        self.cursor = self.conn.cursor() 
        
        self.tblname = 'turnoverrate'
        
        insertCols = "("
        insertValues = " values("
        for i in range(len(DBCOL_NAME_TURNOVER_RATE)-1):
            insertCols += "%s,"%(DBCOL_NAME_TURNOVER_RATE[1+i])
            insertValues += "%s,"
        
        self.insertSqlTurnoverRate = insertCols[0:-1]+')'
        self.insertSqlValues = insertValues[0:-1]+')'
        
    def createTable(self): 
        tablename = self.tblname
        
        self.cursor.execute("drop table if exists %s"%(tablename))
        self.conn.commit()
        
        sqlcols = ""
        for i in range(len(DBCOL_NAME_TURNOVER_RATE)):
            sqlcols += "%s %s,"%(DBCOL_NAME_TURNOVER_RATE[i], DBCOL_TYPE_TURNOVER_RATE[i])
        sqlcols += "key(%s,%s)"%(DBCOL_NAME_TURNOVER_RATE[2],DBCOL_NAME_TURNOVER_RATE[4])
        createsql = "create table if not exists %s(%s) "%(tablename, sqlcols)
        
        try:
            print self.cursor.execute(createsql)
        except Exception, e:
            #print "createsql",createsql,e
            return False
        
        return True
            
    def insert(self, items):
        insertStockSql = "insert into %s"%(self.tblname)

        sql = insertStockSql+self.insertSqlTurnoverRate+self. insertSqlValues      

        try:
            n = self.cursor.execute(sql, items)
        except Exception, e:
            print insertStockSql
            print e,sql
            return False

        self.conn.commit()
        
        return True
    
    def getHighRate(self, idManager, n):

        allresult = []
        startDay = None
        endDay = None

        i=0
        for k,v in idManager.allstockmap.items():
            mktcap = float(v[getAllIdFromSina.SCOL_MKTCAP])
            line = self.calc(k, mktcap)
            if line != None:
                if startDay == None:
                    startDay = line[RATE_COL_LASTDAY]
                if endDay == None:
                    endDay = line[RATE_COL_LASTDAY]
                    
                if startDay > line[RATE_COL_LASTDAY]:
                    startDay = line[RATE_COL_LASTDAY]
                if endDay < line[RATE_COL_LASTDAY]:
                    endDay = line[RATE_COL_LASTDAY]
                #print "id=%s,90=%%%.2f,60=%%%.2f,30=%%%.2f,today=%%%.2f,scount=%d,mktcap=%f,firstday=%s"%line
                allresult.append(line)
                
                i+=1
                #if i > 100:
                    #break

        allowDay = endDay + datetime.timedelta(days=-10)
        invalidCount = 0
        alldatas = []
        self.createTable()
        for line in allresult:
            if line[RATE_COL_LASTDAY] < allowDay:
                invalidCount+=1
            else:
                alldatas.append(line)
                self.insert(line)
                
        alldatas.sort(key = lambda x:x[1], reverse = True)

        userdata = alldatas[0:n]
        print startDay, endDay, allowDay, invalidCount
        return userdata
    
    def select(self, condition):
        sql = "select * from %s"%(self.tablePrefix+id)  

        try:
            count = self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print "getAllData except", e
            return None
        
        return rows 
    
    def calc(self, id, mktcap):
        longRateSum, middleRateSum, shortRateSum = 0,0,0
        lines = self.localDataObj.getLocalData(id, self.longDayNum)
        dayNum = len(lines)
        
        if dayNum < self.longDayNum:
            return None
        i = 0
        totalStockNum = 10000*mktcap/float(lines[-1][DATE_COL_CLOSE])
        for line in lines:
            vol = int(line[DATE_COL_VOL])
            longRateSum += vol
            if i >= self.longDayNum - self.middleDayNum:
                middleRateSum += vol
                if i >= self.longDayNum - self.shortDayNum:
                    shortRateSum += vol
            #print i,line
            i+=1
            
        result = (id, \
                  100*longRateSum/totalStockNum, 100*middleRateSum/totalStockNum, 100*shortRateSum/totalStockNum, 100*float(lines[-1][DATE_COL_VOL])/totalStockNum,\
                  totalStockNum, mktcap,lines[0][DATE_COL_DATE],\
                  float(lines[0][DATE_COL_CLOSE]),\
                  float(lines[self.longDayNum - self.middleDayNum][DATE_COL_CLOSE]),\
                  float(lines[self.longDayNum - self.shortDayNum][DATE_COL_CLOSE]), \
                  float(lines[-1][DATE_COL_CLOSE]))
        
        return result

        
if __name__ == '__main__':

    idManager = getAllIdFromSina.sinaIdManage()
    a = CalcTurnOverRate()
    idManager = getAllIdFromSina.sinaIdManage()
    idManager.initLocalData()
    datas = a.getHighRate(idManager, 100)
    #a.createTable()


    