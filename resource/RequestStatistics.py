from useful.singleton import Singleton
from useful.observableMixin import Observer
import _thread
from useful.common import goodStatusCode, toMB, format_block


class RequestStatistics(Singleton, Observer):
    def __init__(self):
        self.init_statistics()
        Singleton.__init__(self)

    def init_statistics(self):
        self.lock = _thread.allocate_lock()
        self.status_codes = []
        self.servers = set()
        self.downloaded = 0
        self.last_click = None
        self.redirects = 0
        self.hits = 0
        self.goodhits = 0

    def update(self, subject):
        self.lock.acquire()
        self.status_codes.append(subject.status_code)
        self.last_click = subject.info.getheader('Date')
        self.servers.add(subject.info.getheader('Server'))
        self.update_transmited(subject.total_size)
        if len(subject.history) > 1:
            self.redirects += 1
        self.update_hit(subject.status_code)
        self.lock.release()

    def update_values(self, subject, *args, **kwargs):
        self.status_codes.append(kwargs['status_code'])
        self.update_hit(kwargs['status_code'])
        self.last_click = kwargs['timestamp']

    def update_hit(self, code):
        self.hits += 1
        if goodStatusCode(code):
            self.goodhits += 1

    def update_transmited(self, transmitedBytes):
        self.downloaded += transmitedBytes

    def clear_statistics(self):
        self.init_statistics()

    def get_debug_print(self):
        statisticsResumee = '''
                       ############### Statistics ################
                       Hits= {0}
                       goodHits = {1}
                       Downloaded = {2} Mb
                       Redirections = {3}
                       Servers = {4}
                       '''.format(self.hits, self.goodhits, toMB(self.downloaded), self.redirects, list(self.servers))
        return format_block(statisticsResumee)