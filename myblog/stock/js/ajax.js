/*
html5����ͼ��
author:yukaizhao
blog:http://www.cnblogs.com/yukaizhao/
��ҵ�򹫿���������ϵ��yukaizhao@gmail.com
*/
var Ajax = {};
Ajax.request = function (method, url, callback, canvasId, showLoading) {
    showLoading = showLoading == undefined ? true : showLoading;
    //�������ݵ���Painter��ͼ
    var client = (window.ActiveXObject ? new ActiveXObject('Microsoft.XMLHTTP') : (window.XMLHttpRequest ? new XMLHttpRequest() : false));
    var canvas = document.getElementById(canvasId);
    if (canvas && showLoading) {
        canvas.loadingObj = new loading(canvas);
//setDebugMsg('canvas.loadingObj.show begin');
        canvas.loadingObj.show();
//setDebugMsg('canvas.loadingObj.show end');
    }
    client.onreadystatechange = function () {
//setDebugMsg('client.readyState = ' + client.readyState + ',client.status = ' + client.status);
        if (client.readyState == 4 && client.status == 200) {
            if (canvas && showLoading) canvas.loadingObj.hide();
            callback(client);
        }
//setDebugMsg('finish callback');
    };
//setDebugMsg('client.open begin');
    client.open(method || "POST", url, true);
//setDebugMsg('client.open end');
    if (client.overrideMimeType)client.overrideMimeType("text/xml");
//setDebugMsg('client.overrideMimeType');
    client.send();
//setDebugMsg('client.send()');
};

Ajax.get = function (url, callback, canvasId, showLoading) {
    Ajax.request('GET', url,callback, canvasId, showLoading);
};

Ajax.post = function (url, callback, canvasId, showLoading) {
    Ajax.request('POST', url,callback, canvasId, showLoading);
};