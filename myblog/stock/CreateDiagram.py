from common import *
from FinanceChart import *

import csv,re,datetime

chartcolors = ['0x0000ff','0xff00ff','0x008000','0x99ff99','0x006060','0xc06666ff','0xff9999','0x99ff99']
class stockChart():
    def __init__(self):
        self.c = None
        
    def initMainData(self, title, listTime, sOpenPri, sClosePri, sHighPri, sLowPri, sVol):
        #print "initMainData from %s to %s"%(listTime[0],listTime[-1])
        self.listChartTime = []
        for thisday in listTime:
            self.listChartTime.append(chartTime(thisday.year, thisday.month, thisday.day))        

        self.s_open_pri = sOpenPri
        self.s_close_pri = sClosePri
        self.s_high_pri = sHighPri
        self.s_low_pri = sLowPri
        self.s_vol = sVol
        
        self.createMainDiagram(title)
        
    def addSlowStochastic(self):
        self.c.addSlowStochastic(75, 14, 3, '0x006060', '0x606000')
        
    def addNPVI(self):
        self.c.addNVI(75, 30, '0x0000ff', '0xff00ff') 
        self.c.addPVI(75, 30, '0xff00ff', '0x008000')
        
    def addOBV(self):   
        self.c.addOBV(63, '0xff00ff') 
        
    def addMainChart(self):
        # Add the main chart with 240 pixels in height
        self.c.addMainChart(350)
        
        # Add a 10 period simple moving average to the main chart, using brown color
        #c.addSimpleMovingAvg(50, '0x663300')
        
        # Add a 20 period simple moving average to the main chart, using purple color
        #c.addSimpleMovingAvg(200, '0x9900ff')
        
        # Add candlestick symbols to the main chart, using green/red for up/down days
        self.c.addCandleStick('0xff0000', '0x00ff00')
        
        # Add 20 days donchian channel to the main chart, using light blue (9999ff) as the
        # border and semi-transparent blue (c06666ff) as the fill color
        self.c.addDonchianChannel(20, '0x9999ff', '0xc06666ff')
        
        # Add a 75 pixels volume bars sub-chart to the bottom of the main chart, using
        # green/red/grey for up/down/flat days
        self.c.addVolBars(120, '0xff9999', '0x99ff99', '0x808080')   
              
    def createMainDiagram(self, title):
        self.c = FinanceChart(12.5*len(self.listChartTime))
        # Add a title to the chart
        self.c.addTitle(title)
        # Set the data into the finance chart object
        self.c.setData(self.listChartTime, self.s_high_pri, self.s_low_pri,self.s_open_pri,self.s_close_pri,self.s_vol, 1)

    def addMACD(self):
        self.c.addMACD(75, 26, 12, 9, '0x0000ff', '0xff00ff', '0x008000')
    
    def addRSI(self):
        self.c.addRSI(75, 9, '0x0000ff', 15, '0xff00ff', '0x008000')
    def addCCI(self):
        self.c.addCCI(75, 9, '0x0000ff', 15, '0xff00ff', '0x008000')

    def add1LineIndicator(self,listData,name):
        self.c.addLineIndicator(100, listData, '0xff00ff', name) 
    def add2LineIndicator(self,listData1,name1,listData2,name2):
        hyChart = self.c.addLineIndicator(200, listData1, '0x0000ff', name1)
        self.c.addLineIndicator2(hyChart, listData2, '0xff00ff', name2) 
    def add3LineIndicator(self,listData1,name1,listData2,name2,listData3,name3):
        #print "add3LineIndicator",listData2[0],listData2[-1]
        hyChart = self.c.addLineIndicator(200, listData1, '0x0000ff', name1)
        self.c.addLineIndicator2(hyChart, listData2, '0xff00ff', name2) 
        self.c.addLineIndicator2(hyChart, listData3, '0x008000', name3) 
    
    def makeChart(self,chartFileName):
        self.c.makeChart(chartFileName)
        
    def createAttackDefendDiagram(self, sid,chartFileName, listTime, sOpenPri, sClosePri, sHighPri, sLowPri, sVol, listAttack, listDefend):  
        title = "%.2d%.2d%.2d-%.2d%.2d%.2d_%s"%(listTime[0].year,listTime[0].month, listTime[0].day,listTime[-1].year,listTime[-1].month, listTime[-1].day,sid)
        self.initMainData(title,listTime, sOpenPri, sClosePri, sHighPri, sLowPri, sVol)
        self.addMainChart()
        self.add3LineIndicator(listAttack, 'attack',listDefend,'defend',sClosePri,'close')
        self.makeChart(chartFileName)

    
    def createFinanceDiagram(title, sFileName, start, end):
        reader = csv.reader(open(sFileName, 'rb'))
    
        j = 0
        sOpenPri = []
        sClosePri = []
        sHighPri = []
        sLowPri = []
        sVol = []
        listTime = []
        for line in reader:
            
            thisday = datetime.datetime.strptime(line[DATE_COL_DATE], '%Y-%m-%d')
            if thisday < start or start > end:
                continue
            else:
                listTime.insert(0, chartTime(thisday.year, thisday.month, thisday.day))
                sOpenPri.insert(0, line[DATE_COL_OPEN])
                sClosePri.insert(0, line[DATE_COL_CLOSE])
                sHighPri.insert(0, line[DATE_COL_HIGH])
                sLowPri.insert(0, line[DATE_COL_LOW])
                sVol.insert(0, line[DATE_COL_VOL])
                j += 1
    
        # Add a title to the chart
        c = createMainDiagram(title, listTime, sOpenPri, sClosePri, sHighPri, sLowPri, sVol)
        
        return c
def createStockDiagram(stockid, startDate, endDate):
    storeDataFolder = getLatestDataFolder()
    sFileName = "%s/%s.csv"%(storeDataFolder, stockIDforYahoo(stockid))
    
    start = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    end = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    
    print start, end, sFileName

            
    sToHyMap = {}
    hyToSMap = {}
    hyNameList = []
    getSinaHy(sToHyMap, hyToSMap, hyNameList)
    hyFileName = "%s/%s_%s.csv"%(gHgMiningFolder, sToHyMap[stockid],hyNameList[sToHyMap[stockid]])
    print hyFileName

    reader = csv.reader(open(hyFileName, 'rb'))
    increasePerc = []
    increaseVolPerc = []
    incPriPerc = []
    avePriPerc = []
    
    for line in reader:
        thisday = datetime.datetime.strptime(line[0], '%Y-%m-%d')
        if thisday < start or thisday > end:
            continue
        else:
            #listTime.insert(0, chartTime(thisday.year, thisday.month, thisday.day))
            increasePerc.insert(0, line[1])
            increaseVolPerc.insert(0, line[2])
            incPriPerc.insert(0, line[3])
            avePriPerc.insert(0, line[4])
    
    print increasePerc
    print increaseVolPerc
    print incPriPerc
    print avePriPerc
             
    title = stockIDforYahoo(stockid)
    c = createFinanceDiagram(title, sFileName, start, end)         

    # Append a MACD(26, 12) indicator chart (75 pixels high) after the main chart, using
    # 9 days for computing divergence.
    c.addMACD(75, 26, 12, 9, '0x0000ff', '0xff00ff', '0x008000')
    hyChart = c.addLineIndicator(75, increasePerc, '0x0000ff', 'increasePerc') 
    #c.addLineIndicator2(hyChart, increaseVolPerc, '0xff00ff', 'increaseVolPerc') 
    #c.addLineIndicator2(hyChart, incPriPerc, '0x008000', 'incPriPerc') 
    #c.addLineIndicator2(hyChart, avePriPerc, '0xff9999', 'avePriPerc') 

    c.addRSI(75, 9, '0x0000ff', 15, '0xff00ff', '0x008000')
    c.addCCI(75, 9, '0x0000ff', 15, '0xff00ff', '0x008000')
    
    # Output the chart
    c.makeChart(globalTopFolder+"/test/%s.png"%(title))



    
def makeSymbolChart(title, datas, labels, linenames, imagefile, xAxisTitle, yAxisTitle):
    totalShowColNum = len(datas)
    
    for row in datas:
        print len(row)
    
    if totalShowColNum == 0 or totalShowColNum > 7:
        print "datas column error",  totalShowColNum
        
    length = len(datas[0])*10
    
    print "totalShowColNum",totalShowColNum, "length", length, len(labels)
    # Create a XYChart object of size 300 x 180 pixels, with a pale yellow (0xffffc0)
    # background, a black border, and 1 pixel 3D border effect.
    c = XYChart(length, 600, '0xffffc0', '0x000000', 1)
    c.setRoundedFrame()
    
    # Set the plotarea at (45, 35) and of size 240 x 120 pixels, with white background.
    # Turn on both horizontal and vertical grid lines with light grey color (0xc0c0c0)
    c.setPlotArea(60, 20, length-100, 550, '0xffffff', -1, -1, '0xc0c0c0', -1)
    # Add a legend box at (50, 30) (top of the chart) with horizontal layout. Use 9
    # pts Arial Bold font. Set the background and border color to Transparent.
    c.addLegend(50, 30, 0, "arialbd.ttf", 9).setBackground(Transparent)
    #c.addLegend(45, 12, 0, "", 8).setBackground(Transparent)
    c.addTitle(title, "arialbd.ttf", 9, '0xffffff').setBackground(c.patternColor(['0x004000', '0x008000'], 2))

    c.yAxis().setTitle(yAxisTitle)
    # Set the labels on the x axis
    c.xAxis().setLabels(labels)
    c.xAxis().setLabelStep(len(datas[0])/10)
    # Add a title to the x axis
    c.xAxis().setTitle(xAxisTitle)
    
    # Add a line layer to the chart
    layer = c.addSplineLayer()
    layer.setLineWidth(2)
    
    colnum = 0
    
    # Add the first line. Plot the points with a 7 pixel square symbol
    for rows in datas:
        layer.addDataSet(rows, chartcolors[colnum], linenames[colnum]).setDataSymbol(CircleSymbol, 6, 0xffff00)
        colnum+=1

    #layer.setDataLabelFormat("{value|0}%")
    
    # Output the chart
    c.makeChart(imagefile)
    
    return imagefile


if __name__ == "__main__":
    data0 = [100, 125, 245, 147, 67]
    data1 = [85, 156, 179, 211, 123]
    data2 = [97, 87, 56, 267, 157]
    
    names = ["0", "1", "2","3","4"]
    datas = [data0]
    makeSymbolChart("title", datas, "labels", names, "../test.png")
    
    