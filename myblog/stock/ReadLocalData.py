#coding:utf-8
from common import *
import datetime
import csv


class ReadLocalData():
    def __init__(self):
        self.today = datetime.datetime.now()
        
    def getLocalData(self, sid):
        datafolder = getLatestDataFolder()
        sfile=os.listdir(datafolder)
        rows = []
        print "getLocalData",datafolder
        
        for ssfile in sfile:
            if ssfile[0:6] == sid:
                print ssfile
                reader = csv.reader(open(datafolder+'/'+ssfile, 'rb'))
                for line in reader:
                    line[DATE_COL_DATE] = datetime.datetime.strptime(line[DATE_COL_DATE], "%Y-%m-%d").date()
                    rows.insert(0, line)

        return rows
    
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
    sids = ['600815','600835','000858']
    today = datetime.date.today()
    fromday = today-datetime.timedelta(days=365)
    data.getSameData(sids, fromday, today)
    
        
        