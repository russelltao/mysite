
function line(ctx, x0, y0, x1, y1, color, width) {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.strokeStyle = color;
    ctx.lineWidth = width || 1;
    ctx.stroke();
}

function getMinTime(minIndex) {
    //上午09：30-11：30
	//下午13：00-15：00
	var d = new Date();
	if (minIndex <= 120) {
	    d.setHours(9, 30, 30);
	    d = new Date(d.getTime() + (minIndex) * 60 * 1000);
	} else {
	    d.setHours(13, 0, 0);
	    d = new Date(d.getTime() + (minIndex - 120) * 60 * 1000);
	}
	
	
	var hour = d.getHours() > 9 ? new String(d.getHours()) : '0' + d.getHours();
	var minutes = d.getMinutes() > 9 ? new String(d.getMinutes()) : '0' + d.getMinutes();
	var seconds = '30';
	return hour + '' + minutes + seconds;
}

function Tip(options) {
    this.options = options;
    this.canvas = options.canvas;
    this.canvas.tip = this;
}

Tip.prototype = {
    show: function (relativePoint, html) {
        var dc = this.dataContext;
        var painter = this.canvas.painter;
        if (dc) {
            if (dc.isNewQuote) painter.fillTopText(dc.data);
            else painter.fillTopText(dc.data, dc.index);
        }
    },
    update: function (relativePoint, html) {
        this.show(relativePoint, html);
    },
    hide: function () {
        var dc = this.dataContext;
        var painter = this.canvas.painter;
        if (dc) {
            painter.fillTopText(dc.data);
        }
    }
};

function minsChart(canvasId, options) {
    extendObject(options, this);
    this.canvas = $id(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.canvas.painter = this;
}

minsChart.prototype = {
	    /*
	data format like :{
	quote: {
	time: 20111214150106,
	open: 2241.390,
	preClose: 2248.590,
	highest: 2256.740,
	lowest: 2224.730,
	price: 2228.530,
	volume: 4407982200,
	amount: 38621178573
	},
	mins: [
	{price:2239.45,volume:49499299,amount:459279327,time:10:00:00}
	]
	}
	*/
	paint: function (data) {
	    this.fillTopText(data);
	    this.paintChart(data);
	    this.paintxAxis();
	    this.fillBottomText(data);
	    this.paintVolume(data);
	},

	paintVolume: function (data) {
	    var ctx = this.ctx;
	    var options = this.volume;
	    ctx.beginPath();
	    ctx.rect(options.region.x, options.region.y, options.region.width, options.region.height);
	    ctx.strokeStyle = options.borderColor;
	    ctx.stroke();
	    line(ctx, options.region.x, options.region.y + options.region.height / 2, options.region.x + options.region.width, options.region.y + options.region.height / 2, options.splitLineColor);
	    options.getDataLength = function () { return this.data.items.length; };
	    options.maxDotsCount = this.maxDotsCount;
	    var volumePainterImp = new volumePainter(options);
	    var painter = new Painter(this.canvas.id, volumePainterImp, { items: data.mins });
	    painter.paint();
	
	    var max = painter.maxVolume;
	    var unit;
	    if (max / 1000000 > 1000) {
	        max = max / 1000000;
	        unit = '百万';
	    } else {
	        max = max / 10000;
	        unit = '万';
	    }
	    var scalers = [max.toFixed(2), (max / 2).toFixed(2), '(' + unit + ')'];
	    var yscaler = new yAxis(this.volume.yScaler);
	    var painter = new Painter(this.canvas.id, yscaler, scalers);
	    painter.paint();
	},
	
	fillBottomText: function (data) {
	    if (!this.bottomText) return;
	    //高9999 低9999 成交888999
	    var ctx = this.ctx;
	    var txt = '高';
	    var options = this.bottomText;
	    ctx.font = options.font;
	    ctx.fillStyle = options.color;
	    var w = ctx.measureText(txt).width;
	    ctx.fillText(txt, options.region.x, options.region.y);
	    var x = options.region.x + w;
	    var quote = data.quote;
	    var me = this;
	    function getTxtColor(val) { return val > quote.preClose ? me.riseColor : (val == quote.preClose ? me.normalColor : me.fallColor); }
	    var highColor = getTxtColor(quote.highest);
	    var high = toMoney(quote.highest);
	    ctx.fillStyle = highColor;
	    w = ctx.measureText(high).width;
	    ctx.fillText(high, x, options.region.y);
	    x += w;
	    txt = ' 低';
	    ctx.fillStyle = options.color;
	    w = ctx.measureText(txt).width;
	    ctx.fillText(txt, x, options.region.y);
	    x += w;
	    var lowColor = getTxtColor(quote.lowest);
	    var low = toMoney(quote.lowest);
	    w = ctx.measureText(low).width;
	    ctx.fillStyle = lowColor;
	    ctx.fillText(low, x, options.region.y);
	    x += w;
	    ctx.fillStyle = options.color;
	    var amount = ' 成交' + bigNumberToText(quote.amount);
	    ctx.fillText(amount, x, options.region.y);
	},
	
	paintxAxis: function () {
	    var xAxisImpl = new xAxis(this.xScaler);
	    var xAxisPainter = new Painter(this.canvas.id, xAxisImpl, this.xScaler.data);
	    xAxisPainter.paint();
	},

	paintChart: function (data) {
	    var minsChartOptions = this.minsChart;
	    var region = this.minsChart.region;
	    var ctx = this.ctx;
	    ctx.beginPath();
	    ctx.strokeStyle = minsChartOptions.borderColor;
	    ctx.rect(region.x, region.y, region.width, region.height);
	    ctx.stroke();
	
	    //水平线
	    var middleIndex = (this.minsChart.horizontalLineCount + this.minsChart.horizontalLineCount % 2) / 2;
	    var splitCount = this.minsChart.horizontalLineCount + 1;
	    for (var i = 1; i <= this.minsChart.horizontalLineCount; i++) {
	        var color = (i == middleIndex ? minsChartOptions.middleLineColor : minsChartOptions.otherSplitLineColor);
	        var y = region.y + region.height * i / splitCount;
	        line(ctx, region.x, y, region.x + region.width, y, color);
	    }
	    //垂直线 
	    splitCount = this.minsChart.verticalLineCount + 1;
	    for (var i = 1; i <= this.minsChart.verticalLineCount; i++) {
	        var x = region.x + region.width * i / splitCount;
	        line(ctx, x, region.y, x, region.y + region.height, minsChartOptions.otherSplitLineColor);
	    }
	
	    //价格线
	    var lineOptions = {
	        region: region,
	        maxDotsCount: this.maxDotsCount,
	        getDataLength: function () { return this.data.items.length; },
	        getItemValue: function (item) { return item.price; },
	        middleValue: data.quote.preClose, //通常是昨收
	        lineColor: minsChartOptions.priceLineColor
	    };
	    var linePainterImp = new linePainter(lineOptions);
	    var priceLinePainter = new Painter(this.canvas.id, linePainterImp, { items: data.mins });
	    priceLinePainter.paint();
	
	    //y轴
	    var yOptions = this.minsChart.yScalerLeft;
	    var preClose = data.quote.preClose;
	    var me = this;
	    yOptions.color = function (val) {
	        return val > preClose ? me.riseColor : (val == preClose ? me.normalColor : me.fallColor);
	    };
	    var scalersLeft = [];
	    var scalersRight = [];
	    var min = preClose - priceLinePainter.maxDiff;
	    var space = priceLinePainter.maxDiff * 2 / (this.minsChart.horizontalLineCount + 1);
	    for (var i = this.minsChart.horizontalLineCount + 1; i >= 0; i--) {
	        var val = min + i * space;
	        scalersLeft.push(val.toFixed(2));
	        var percent = (val - preClose) * 100 / preClose;
	        scalersRight.push(percent.toFixed(2) + '%');
	    }
	    var yx = new yAxis(yOptions);
	    var yAxisPainter = new Painter(this.canvas.id, yx, scalersLeft);
	    yAxisPainter.paint();
	
	    var yPercentOptions = this.minsChart.yScalerRight;
	    yPercentOptions.color = function (val) {
	        return (val == '0.00%' ? 'black' : (val.charAt(0) == '-' ? 'green' : 'red'));
	    };
	    var yxPercent = new yAxis(yPercentOptions);
	    var yxPercentPainter = new Painter(this.canvas.id, yxPercent, scalersRight);
	    yxPercentPainter.paint();
	
	
	    //均线
	    if (this.needPaintAvgPriceLine) {
	        //生成移动均线数据
	        var items = [];
	        var totalVolume = 0;
	        var totalAmount = 0;
	        data.mins.each(function (item) {
	            totalVolume += item.volume;
	            totalAmount += item.amount;
	            items.push(totalAmount / totalVolume);
	        });
	        lineOptions.lineColor = minsChartOptions.avgPriceLineColor;
	        lineOptions.getItemValue = function (item) { return item; };
	        linePainterImp = new linePainter(lineOptions);
	        var painterAvg = new Painter(this.canvas.id, linePainterImp, { items: items });
	        painterAvg.paint();
	    }
	
	    var me = this;
	    var chartRegion = me.minsChart.region;
	
	    function getY(x) {
	        var index = Math.ceil((x - me.minsChart.region.x) * me.maxDotsCount / me.minsChart.region.width);
	        var val;
	        var isNewQuote;
	        if (index >= 0 && index < data.mins.length) {
	            val = data.mins[index].price;
	            isNewQuote = false;
	        } else {
	            val = data.quote.price;
	            isNewQuote = true;
	        }
	
	        if (me.canvas.tip) me.canvas.tip.dataContext = { data: data, isNewQuote: isNewQuote, index: index };
	        var diff = val - preClose;
	        var middleY = (me.minsChart.region.y + me.minsChart.region.height / 2);
	        return middleY - diff * me.minsChart.region.height / 2 / priceLinePainter.maxDiff;
	    }
	
	    //添加鼠标事件
	    addCrossLinesAndTipEvents(this.canvas, {
	        getCrossPoint: function (ev) { return { x: ev.offsetX, y: getY(ev.offsetX) }; },
	        triggerEventRanges: { x: chartRegion.x, y: chartRegion.y, width: chartRegion.width, height: me.volume.region.y + me.volume.region.height - chartRegion.y },
	        tipOptions: {
	            getTipHtml: function (ev) { return null; },
	            position: { x: false, y: false }
	        },
	        crossLineOptions: {
	            color: 'black'
	        }
	    });
	},

	fillTopText: function (data, minIndex) {
	    var quote = data.quote;
	    var ctx = this.ctx;
	    var topText = this.topText;
	    var region = topText.region;
	    ctx.clearRect(region.x, region.y, region.width, region.height);
	    var price;
	    var time;
	    var txtTime = "minIndex undefined";
	    pankouIndex = topText.datanum-1;
	    if (typeof minIndex == 'undefined') {
	        price = quote.price;
	        time = quote.day;
	        
	        txtTime = new String(time);
	    } else {
	        price = data.mins[minIndex].price;
	        txtTime = data.mins[minIndex].time;
	        pankouIndex = minIndex;
	    }
	
	    ctx.fillStyle = topText.color;
	    ctx.font = topText.font;
	    if (topText.textBaseline) ctx.textBaseline = topText.textBaseline;
	    var txt = '最新' + toMoney(price);
	    var width = ctx.measureText(txt).width;
	    ctx.fillText(txt, topText.region.x, topText.region.y);
	
	    var isRise = price > quote.preClose;
	    var isEqual = price == quote.preClose;
	    var isFall = price < quote.preClose;
	    var diff = toMoney(price - quote.preClose);
	    var txtRiseFall = (isRise ? '↑' : (isFall ? '↓' : '')) + diff
	+ ('(')
	+ toMoney(diff * 100 / quote.preClose)
	+ '%)';
	
	    var x = topText.region.x + width;
	    ctx.fillStyle = isRise ? this.riseColor : (isFall ? this.fallColor : this.normalColor);
	    ctx.fillText(txtRiseFall, x, topText.region.y);
	
	    ctx.fillStyle = topText.color;
	    var timeWidth = ctx.measureText(txtTime).width;
	    ctx.fillText(txtTime, topText.region.x + topText.region.width - timeWidth, topText.region.y);
	    
	    //for pankou show
	    pankouregion = topText.pankouRegion;
	    ctx.clearRect(pankouregion.x, pankouregion.y, pankouregion.width, pankouregion.height);
	    lineH = pankouregion.height / 15
	    ctx.fillStyle = topText.color;

	    var py = pankouregion.y;
	    var pankouText = "5档盘口";
	    var volWidth = 80;
	    ctx.fillText(pankouText, pankouregion.x, py);
	    
	    for (var i=0; i<5; i++){
		    py += lineH;
		    pankouText = "卖"+(5-i)+"  "+data.mins[pankouIndex].pankou[20-2*i-2];
		    ctx.fillText(pankouText, pankouregion.x, py);
		    pankouText = data.mins[pankouIndex].pankou[20-2*i-1];
		    ctx.fillText(pankouText, pankouregion.x + volWidth, py);
	    }
	    
	    py += lineH;
	    py += 3;
	    line(ctx, pankouregion.x, py, pankouregion.x+pankouregion.width, py, 'red', 1);
	    py -= 10;
	    
	    for (var i=0; i<5; i++){
		    py += lineH;
		    pankouText = "买"+(1+i)+"  "+data.mins[pankouIndex].pankou[2*i];
		    ctx.fillText(pankouText, pankouregion.x, py);
		    pankouText = data.mins[pankouIndex].pankou[2*i+1];
		    ctx.fillText(pankouText, pankouregion.x + volWidth, py);
	    }
	    
	    py += lineH;
	    py += 3;
	    line(ctx, pankouregion.x, py, pankouregion.x+pankouregion.width, py, 'green', 1);
	    py += 10;
	    
	    pankouText = "竞买："+data.mins[pankouIndex].compbuy;
	    ctx.fillText(pankouText, pankouregion.x, py);
	    pankouText = "竞卖："+data.mins[pankouIndex].compsell;
	    py += lineH;
	    ctx.fillText(pankouText, pankouregion.x, py);
	    pankouText = "总成交金额："+data.mins[pankouIndex].amount;
	    py += lineH;
	    ctx.fillText(pankouText, pankouregion.x, py);
	    pankouText = "当前成交量："+data.mins[pankouIndex].volume;
	    py += lineH;
	    ctx.fillText(pankouText, pankouregion.x, py);
	}
};
