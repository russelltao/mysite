# -*- coding: utf-8 -*-
import urllib,urllib2
import json,os
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

register_openers()
def urlcallback(a,b,c):
    return

jsonkey='{"expires_in":2592000,"refresh_token":"22.3f846482fb97b9253ab1185c2a7846af.315360000.1732936060.3674485908-2269615","access_token":"21.f6077f3ea82ce158b42d5d20adab2ed1.2592000.1420168060.3674485908-2269615","session_secret":"af3210ebacb159165d30b61283638a88","session_key":"9mnRItV3SMtmjQZINGWw5KiBszz+0y+7eeaO5GXVWy2Xdl05G4HuaPAD6lfkDZ0fKrhMP9AyHyVloFqmyhumhJcNghKjO5Qjlg==","scope":"basic netdisk"}'
baiduAccessKey = json.JSONDecoder().decode(jsonkey)  


baseUrl = 'https://pcs.baidu.com/rest/2.0/pcs/%s?%s'


class BaiduPan():
    def __init__(self):
        self.allfiles = {}
        self.appPrefix = '/apps/videoshare/books'
        
    def printAllFiles(self):
        for k,v in self.allfiles.items():
            print k,v
        print "total files:",len(self.allfiles)
        
    def getUseSpace(self):
        paras = 'method=info&access_token='+baiduAccessKey['access_token']
        url = baseUrl%('quota', paras)
        response = urllib2.urlopen(url)
    
        html = response.read()  
        info = json.JSONDecoder().decode(html)  
        print info
        
        
    def listFolder(self, rootpath='/', recursive=False):
        if not recursive:
            self.allfiles = {}
        if rootpath[0] != '/':
            rootpath ='/'+rootpath
        if rootpath[-1] != '/':
            rootpath +='/'
        encodepath = self.appPrefix+rootpath
        try:
            urlencodepath = urllib.quote(str(encodepath), '')
        except urllib2.URLError,e:
            print e.code, e.reason
    
        #print urlencodepath
        paras = 'method=list&access_token=%s&path=%s'%(baiduAccessKey['access_token'],urlencodepath)
        url = baseUrl%('file', paras)
        #print "url=",url
        response = urllib2.urlopen(url)
        
        result = {}
    
        html = response.read()
        #print "rootpath=",rootpath,'self.appPrefix=',self.appPrefix
        info = json.JSONDecoder().decode(html)
        for fitem in info['list']:
            exactpath = fitem['path'][len(self.appPrefix):]
            logicpath = exactpath[len(rootpath):]
            isFolder = False
            if fitem['isdir'] == 1:
                isFolder = True
            #print logicpath,fitem['size'],fitem['isdir'],exactpath
            
            result[logicpath] = {"size":fitem['size'],"isFolder":isFolder,"exactPath":exactpath}
            self.allfiles[fitem['path'].decode('utf8')] = fitem['isdir']
            if fitem['isdir'] and recursive:
                self.listFolder(fitem['path'], recursive)
                
        return result
        
    def getInfo(self, path):
        print 'getInfo',path
        encodepath = path.decode('gbk').encode('utf8')
        urlencodepath = urllib.quote(encodepath, '')
        paras = 'method=meta&path=%s&access_token=%s'%(urlencodepath,baiduAccessKey['access_token'])
        url = baseUrl%('file', paras)
        print "url=",url
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError,e:
            print e.code, e.reason
            return False
    
        html = response.read()  
        info = json.JSONDecoder().decode(html)  
        print info
        for fitem in info['list']:
            for k,v in fitem.items():
                print k,v
        return True
    
    def uploadFile(self, localfile, remotelocation):
        #flocal = open(localfile)
        encodepath = remotelocation.decode('gbk').encode('utf8')
        print encodepath
        urlencodepath = urllib.quote(str(encodepath), '')
        
        datagen, headers = multipart_encode({"image1": open(localfile, "rb")})
    
        paras = 'method=upload&path=%s&access_token=%s'%(urlencodepath,baiduAccessKey['access_token'])
        
        print paras
        url = baseUrl%('file', paras)
        #response = urllib2.urlopen(url)
        
        #req = urllib2.Request(url)  
        request = urllib2.Request(url, datagen, headers)
        # 瀹為檯鎵ц璇锋眰骞跺彇寰楄繑鍥�
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
        try:
            #response = opener.open(req, flocal.read())  
            response = urllib2.urlopen(request)
        except urllib2.URLError,e:
            print 'uploadFile failed!',e.code, e.reason
            #flocal.close()
            return False
        
        html = response.read()  
        info = json.JSONDecoder().decode(html)  
        print info
        
        #flocal.close()
        
        return True
        
    def mkDir(self, path):
        print path
        encodepath = path.decode('gbk').encode('utf8')
        print encodepath
        urlencodepath = urllib.quote(encodepath, '')
        print urlencodepath
        paras = 'method=mkdir&path=%s&access_token=%s'%(urlencodepath,baiduAccessKey['access_token'])
        url = baseUrl%('file', paras)
        print "url=",url
        response = urllib2.urlopen(url)
    
        html = response.read()  
        info = json.JSONDecoder().decode(html)  
        print info
        
    def delete(self, path):
        encodepath = path.decode('gbk').encode('utf8')
        urlencodepath = urllib.quote(encodepath, '')
        print urlencodepath
        paras = 'method=delete&path=%s&access_token=%s'%(urlencodepath,baiduAccessKey['access_token'])
        url = baseUrl%('file', paras)
        print "url=",url
        response = urllib2.urlopen(url)
    
        html = response.read()  
        info = json.JSONDecoder().decode(html)  
        print info
        
    def download(self, path,localfile):
        encodepath = path.decode('gbk').encode('utf8')
        urlencodepath = urllib.quote(encodepath, '')
        print urlencodepath
        paras = 'method=download&path=%s&access_token=%s'%(urlencodepath,baiduAccessKey['access_token'])
        url = baseUrl%('file', paras)
        print "url=",url
        urllib.urlretrieve(url,localfile,urlcallback)   
    
        
    def walkFolderAndUpload(self, folderpath):
        #getInfo('/apps/videoshare/'+folderpath[len('D:/鐧惧害浜�'):])
        i = 0
        alllist = os.walk(folderpath)
        for root,folders,files in alllist:
            for folder in folders:
                i+=1
            for f in files:
                i+=1
        totaltask = i
        print totaltask
        alllist = os.walk(folderpath)
        i = 0
        for root,folders,files in alllist:
            print root,"%d/%d"%(i,totaltask)
            tmproot = root.replace('\\','/')
            
            self.listFolder('/apps/videoshare/'+tmproot[len('D:/鐧惧害浜�'):], False)
            for folder in folders:
                remotepath = '/apps/videoshare/'+tmproot[len('D:/鐧惧害浜�'):]+'/'+folder
                #print remotepath
                i+=1
                if self.allfiles.has_key(remotepath.decode('gbk')):
                    #print "exist",remotepath
                    pass
                else:
                    print "not exist",remotepath
                    self.mkDir(remotepath);
            for f in files:
                i+=1
                localpath = root+'/'+f
                remotepath = '/apps/videoshare/'+tmproot[len('D:/鐧惧害浜�'):]+'/'+f
                
                if self.allfiles.has_key(remotepath.decode('gbk')):
                    #print "exist",remotepath
                    pass
                else:
                    print "not exist",remotepath
                    self.uploadFile(localpath, remotepath);
            
        return
    
if __name__ == "__main__":     
    pan = BaiduPan()
    #uploadFile('D:/鐧惧害浜�鐗囨柇/new/Brooklyn_Daniels_in_Catch_Me_As_I_go_Limp_HD__all.rmvb','鐗囨柇/new/Brooklyn_Daniels_in_Catch_Me_As_I_go_Limp_HD__all.rmvb')
    #pan.listFolder('/apps/videoshare/books')
    #pan.printAllFiles()
    #download('/apps/videoshare/鐗囨柇/smotheredlove-abc.rmvb','e:/smotheredlove-abc.rmvb')
    
    #mkDir('/apps/videoshare/鐗囨柇')
    #getInfo('%2Ftechnology')
    
    