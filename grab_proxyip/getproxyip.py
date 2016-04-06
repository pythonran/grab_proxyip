#date:2015.12.11
#the author:Amior Khan
#coding:utf-8
import urllib2
from httplib import HTTPResponse
from  urllib2 import  OpenerDirector,Request,ProxyHandler,URLError,HTTPError,BaseHandler
import re
##import PyQt4
import threading
import chardet
import zlib
import time

url="http://www.youdaili.net/Daili/http/3937"
weburllist = []
proxyiplist = []
checkedproxyip = []
grabthreadlist = []
checkthreadlist = []
timeout = 1
headers = {}
headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
headers['Accept-Encoding']='gzip, deflate, sdch'
headers['Accept-Language']='zh-CN,zh;q=0.8'
headers['Cache-Control']='no-cache'
headers['Connection']='keep-alive'
headers['Cookie']='Hm_lvt_f8bdd88d72441a9ad0f8c82db3113a84=1449819861; Hm_lpvt_f8bdd88d72441a9ad0f8c82db3113a84=1449819967'
headers['Host']='www.youdaili.net'
headers['Pragma']='no-cache'
headers['Upgrade-Insecure-Requests']='1'
headers['User-Agent']='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'

for i in range(6):
    s = url
    if i >= 1:
        s += '_' + str(i+1) +'.html'
    else:
        s += '.html'
    weburllist.append(s)
# get unchecked proxy_ip
class grabproxyip(threading.Thread):
    ''' Grab the "www.youdaili.net" http proxy_ip

    '''
    def __init__(self,url):
        self.url = url
        self.regular = re.compile(r"\d+\.\d+\.\d+\.\d+:\d+")
        self.header = {}
        self.header["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0"
        self.header["Accept-Encoding"]="gzip,deflate"
        threading.Thread.__init__(self)
        pass

    def getproxyweb(self):
        request = Request(self.url,headers=self.header)
        urlopens = urllib2.urlopen(request)
        urlheaders = urlopens.headers.dict
        gzipflag = False
        if urlheaders["content-encoding"] == "gzip":
                gzipflag = True
        urlopeninfo = urlopens.read()

        if gzipflag == True:
            urlopeninfo = zlib.decompress(urlopeninfo,16+zlib.MAX_WBITS)

        urlopeninfo = urlopeninfo.decode("utf-8")

        ipurl = self.regular.findall(urlopeninfo)

        if ipurl != []:
            proxyiplist.append(ipurl)

    def run(self):
        self.getproxyweb()
        pass

def splitelist(listip):
    biglist = []
    for i in range(len(listip)):
        biglist.extend(listip[i])
    return biglist

def getproxyip():
    for i in range(6):
        print("thread-%d-----url is:%s"%(i+1,weburllist[i]))
        t = grabproxyip(weburllist[i])
        grabthreadlist.append(t)
    for t in grabthreadlist:
        t.start()
    for t in grabthreadlist:
        t.join()
    print "\n-------grab done!----%d ips can be checked!-----------\n" % len(splitelist(proxyiplist))
    return splitelist(proxyiplist)

# check proxy_ip
class checkproxyip(threading.Thread):
    def __init__(self,singlegroupnumber,timeout=1):
        self.singlegroupnumber = singlegroupnumber
        self.templist = splitelist(proxyiplist)
        self.uncheckedlist = []
        self.timeout = timeout
        self._divideiptolist()
        threading.Thread.__init__(self)
        pass
    # divide into 20 groups and 1 groups to check the ip
    def _divideiptolist(self):
        length = len(self.templist) // 20
        i = 0
        while i <= 20:
            self.uncheckedlist.append(self.templist[i*length:i*length+length-1])
            i += 1
        self.uncheckedlist.append(self.templist[-(len(self.templist)%20)-2:])
        #print self.uncheckedlist,'========\n%d===%d===='% (len(self.uncheckedlist),len(splitelist(self.uncheckedlist)))
    # single groups test by access the "www.baidu.com"
    # then count the using-time to pick up the proper ips to append checkedproxyip[]
    def _access(self):
        print("==================",len(self.uncheckedlist[self.singlegroupnumber]))
        for url in self.uncheckedlist[self.singlegroupnumber]:
            currentcheckip = "http://" + url
            print '\n======',currentcheckip,'===============\n'
            proxyheader = ProxyHandler({"http":currentcheckip})
            proxyopener = urllib2.build_opener(proxyheader)
            baseheader = BaseHandler()
            baseheader.add_parent(headers)
            try:
                testresponse = proxyopener.open("http://www.baidu.com",timeout = self.timeout)
            except:
                print currentcheckip , "------>droped!"
            else:
                print("++++++++++++++add one+++++++++++")
                checkedproxyip.append(currentcheckip)
    def run(self):
        self._access()

def input_test_timeout():
    global  timeout
    timeout = input("Please input the test timeout:")

def check_whole_ip():
    input_test_timeout()
    for i in range(22):
        t = checkproxyip(i,timeout)
        checkthreadlist.append(t)
    for t in checkthreadlist:
        t.start()
    for t in checkthreadlist:
        t.join()
    print "\n============checked done! %d ips can be used to proxy==============\n"%len(checkedproxyip)
    return checkedproxyip

def EnableIP():
     getproxyip()
     return check_whole_ip()

if __name__ =="__main__":
    getproxyip()
    print '\n',check_whole_ip(),'\n'

