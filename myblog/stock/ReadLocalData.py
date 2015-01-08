#coding:utf-8
from common import *
import datetime
import csv


class ReadLocalData():
    def __init__(self):
        self.today = datetime.datetime.now()
        
    def getLocalData(self, sid=DPshzhongzhi, mostDays=-1, startDay=None):
        datafolder = getLatestDataFolder()
        sfile=os.listdir(datafolder)
        rows = []
        print "getLocalData",datafolder
        
        for ssfile in sfile:
            #print sid,ssfile
            if ssfile[0:len(sid)] == sid:

                reader = csv.reader(open(datafolder+'/'+ssfile, 'rb'))
                for line in reader:
                    try:
                        line[DATE_COL_DATE] = datetime.datetime.strptime(line[DATE_COL_DATE], "%Y-%m-%d").date()
                    except ValueError,e:
                        print e,line[DATE_COL_DATE],line
                        continue
                    if mostDays == -1:
                        if startDay == None:
                            rows.insert(0, line)
                        elif line[DATE_COL_DATE] >= startDay:
                            rows.insert(0, line)
                    elif i < mostDays:
                        rows.insert(0, line)
                    else:
                        break

        return rows
    
    def reduceData(self, allrows):
        rowCount = len(allrows)
        if rowCount <= 200:
            return allrows
        
        steps = rowCount/100
        result = []
        i = 0
        for i in xrange(0,rowCount,steps):
            result.append(allrows[i])
        
        return result
    
    def getSameData(self, allrows, fromDay, toDay):
        indexes = []

        for ones in allrows:
            indexes.append(0)

        step = datetime.timedelta(days=1)
        curday = fromDay
        result = []
        while curday<=toDay:
            allhas = True
            
            for i in range(len(indexes)):
                while curday > allrows[i][indexes[i]][DATE_COL_DATE]:
                    if (indexes[i] < len(allrows[i])-1):
                        indexes[i]+=1
                    else:
                        break
                if curday != allrows[i][indexes[i]][DATE_COL_DATE]:
                    allhas = False
                    #print curday,allrows[i][indexes[i]]
                    break
                
            if allhas:
                oneDayData = []
                for i in range(len(indexes)):
                    #print allrows[i][indexes[i]]
                    oneDayData.append(allrows[i][indexes[i]])
                    
                result.append(oneDayData)
            
            curday+=step
            
        return result
            
            
if __name__ == "__main__":     
    data = ReadLocalData()
    rows = data.getLocalData()
    print "rows",len(rows)
    
        
        