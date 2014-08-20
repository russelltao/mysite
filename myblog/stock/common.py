#coding=gbk
import os,datetime,re,csv,time


globalTopFolder = "/mnt/data"

gOrigDataFolder = globalTopFolder+"/original" 
#gHyOriginalFolder = globalTopFolder+"/��ҵ/������ҵ"
gHgMiningFolder = globalTopFolder+"/hg" 
gStockidFile = globalTopFolder+"/yahooStockIdList.txt"

DPshzhongzhi = "000001.ss"
DPszchenzhi = "399001.SZ"
DPhs300 = "000300.ss"

DATE_COL_DATE = 0
DATE_COL_OPEN = 1
DATE_COL_HIGH = 2
DATE_COL_LOW = 3
DATE_COL_CLOSE = 4
DATE_COL_VOL = 5
DATE_COL_ADJCLOSE = 6

def getLatestDataFolder():
    if os.path.isdir(gOrigDataFolder): 
        pass
    else:
        return None
    
    sfile=os.listdir(gOrigDataFolder)
    
    allfolders = []

    for ssfile in sfile:
        if ssfile[0:2] == '20':
            allfolders.append(datetime.datetime.strptime(ssfile, '%Y%m%d'))
            
    newdays = sorted(allfolders)
    if len(newdays) < 1:
        print "no initial data"
        return None
    laststoreday = newdays[-1]
    
    return "%s/%.2d%.2d%.2d"%(gOrigDataFolder, laststoreday.year, laststoreday.month, laststoreday.day)


#�������ݣ� ָ�����ƣ���ǰ��������ǰ�۸��ǵ��ʣ��ɽ������֣����ɽ����Ԫ��

#600��601��ͷ��֤A��
#000��001��ͷ��֤A��
#400��420��430��ͷ����A�ɡ�400��420Ϊ���������������й�Ʊ��430Ϊ�йش��Ʊ���ǹ���Ϊ���ָ߿Ƽ���ҵȦǮ���ŵ����彻�׵ġ������Ʊ�����彻�ף����ʻ������򣬵����ռ���
#002��ͷ��С�ɡ���A��һ�֣�����С���������
#900��ͷ��֤B��
#200��ͷ��֤B��
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
        
def stockIDforYahoo(id):
    strId = str(id)
    #�Ͻ���001��������ծ�ֻ���110������120��������ҵծȯ��129������100��������ת��ծȯ��201��������ծ�ع���310��������ծ�ڻ���500������550����������600������A�ɣ�700��������ɣ�710������ת��ɣ�701������ת�������ɣ�711������ת�����ת��ɣ�720������������730�������¹��깺��735�������»����깺��737�������¹����ۡ�900������B�ɣ�
    #����A
    if strId[0:2] == "60":
        return strId+".ss"
    #����A
    elif strId[0:2] == "00":
        return strId+".sz"
    #��ҵ��
    elif strId[0:3] == "300":
        return strId+".sz"    
    #����B
    elif strId[0:3] == "900":
        return strId+".ss"    
    #����B
    elif strId[0:3] == "200":
        return strId+".sz"       
    #��С��
    elif strId[0:3] == "002":
        return strId+".sz"
    #������ɴ���
    elif strId[0:3] == "031":
        return strId+".sz"    
    else:
        print "stockIDforYahoo unknown stock id:",strId
        return strId

def secToMarcketOpen(t):
    marcketOpen = datetime.datetime(t.year, t.month, t.day, 9, 30, 0)
    
    if isJiaoyiri(t) == True:
        if t < marcketOpen:
            return (marcketOpen-t).seconds

        marcketHalfClose = datetime.datetime(t.year, t.month, t.day, 11, 30, 0)
        if t < marcketHalfClose:
            return 0

        marcketHalfOpen = datetime.datetime(t.year, t.month, t.day, 13, 0, 0)
        if t < marcketHalfOpen:
            return (marcketHalfOpen - t).seconds

        marcketClose = datetime.datetime(t.year, t.month, t.day, 15, 0, 0)
        if t < marcketClose:
            return 0

    nextday = 1
    if t.weekday() > 4:
        nextday = 7-t.weekday()
    
    expect = marcketOpen + datetime.timedelta(days=nextday)

    return (expect - t).seconds

        
def isJiaoyiri(t):
    if t.weekday() >= 0 and t.weekday() <= 4 :
        return True
    else:
        return False
        
def isJiaoyishijian(t):
    if isJiaoyiri(t) == False:
        return False
    
    if (t.hour == 9 and t.minute >= 30) or t.hour == 10 or (t.hour == 11 and t.minute <= 30):
        return True
    elif t.hour == 13 or t.hour == 14:
        return True
    else:
        return False
    
class readHgHy():
    def __init__(self):
        self.sToHyMap = {}
        self.hyToSMap = {}
        self.hyNameList = []  
        
        self.hgData = {}
        
    def init(self, startDate):
        getSinaHy(self.sToHyMap, self.hyToSMap, self.hyNameList)
        

        sfile=os.listdir(gHgMiningFolder)
        for ssfile in sfile:

            items = re.findall('(\d+)_([^.]*).csv', ssfile)
        
            if items:
                hyid = int(items[0][0])
                #print "hyid=",hyid
                self.hgData[hyid] = {}

                reader = csv.reader(open(gHgMiningFolder+"/"+ssfile, 'rb'))
                for line in reader:
                    t = datetime.datetime.strptime(line[0],'%Y-%m-%d')
                    if startDate > t:
                        continue
                    self.hgData[hyid][t] = line
      
        
    def readHy(self, sid, theday):
        if self.sToHyMap.has_key(sid):
            pass
        else:
            print sid,"hy has no this stock",sid
            return None
        hyid = self.sToHyMap[sid]
        
        if self.hgData.has_key(hyid):
            if self.hgData[hyid].has_key(theday):
                return self.hgData[hyid][theday]
            else:
                print sid,"has no this date",theday,type(theday)     
                #for t in self.hgData[hyid].items():
                 #   print t[0]    
                return None
        else:
            print "sid,hg data has no this hyid",hyid,type(hyid)
            return None
    
if __name__ == "__main__":
    curtime = datetime.datetime.now()
    t = secToMarcketOpen(curtime)
    print t

    '''t = datetime.datetime.strptime('2011-7-5','%Y-%m-%d')
    hy = readHgHy()
    hy.init(t)
    t = datetime.datetime.strptime('2011-7-5','%Y-%m-%d')
    r = hy.readHy('002357', t)
    print "data:",r'''
    
        
        
        
