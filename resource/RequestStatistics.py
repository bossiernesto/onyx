from useful.singleton import Singleton
from useful.observableMixin import Observer
import thread
from useful.common import goodStatusCode,toMB,formatBlock

class RequestStatistics(Singleton,Observer):

    def __init__(self):
        self.initStatistics()
        Singleton.__init__(self)

    def initStatistics(self):
        self.lock=thread.allocate_lock()
        self.status_codes=[]
        self.servers=set()
        self.downloaded=0
        self.last_click=None
        self.redirects=0
        self.hits=0
        self.goodhits=0

    def update(self, subject):
        self.lock.acquire()
        self.status_codes.append(subject.status_code)
        self.last_click=subject.info.getheader('Date')
        self.servers.add(subject.info.getheader('Server'))
        self.updateTransmited(subject.total_size)
        if len(subject.history)>1:
            self.redirects+=1
        self.updateHit(subject.status_code)
        self.lock.release()

    def updateValues(self, subject,*args,**kwargs):
        self.status_codes.append(kwargs['status_code'])
        self.updateHit(kwargs['status_code'])
        self.last_click=kwargs['timestamp']

    def updateHit(self,code):
        self.hits+=1
        if  goodStatusCode(code):
            self.goodhits+=1

    def updateTransmited(self,transmitedBytes):
        self.downloaded+=transmitedBytes

    def clearStatistics(self):
        self.initStatistics()

    def getPrintDebug(self):
        statisticsResumee='''
                       ############### Statistics ################
                       Hits= {0}
                       goodHits = {1}
                       Downloaded = {2} Mb
                       Redirections = {3}
                       Servers = {4}
                       '''.format(self.hits,self.goodhits,toMB(self.downloaded),self.redirects,list(self.servers))
        return formatBlock(statisticsResumee)