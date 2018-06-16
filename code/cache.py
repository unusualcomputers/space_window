import threading

class SynchronisedCache:
    def __init__(self, size):
        self.cache_size=size
        self.cache = []
        self.lock=threading.Lock()

    def get(self, key):
        self.lock.acquire()
        if len(self.cache)!=0:
            for k,val in self.cache:
                if k==key:
                    self.lock.release()
                    return val
        self.lock.release()
        return None

    def add(self, key, val):
        if self.get(key) is None:
            self.lock.acquire()
            if len(self.cache)>self.cache_size:
                self.cache=self.cache[:-1]
            self.cache.insert(0,(key,val))
            self.lock.release()


class Cache:
    def __init__(self, size):
        self.cache_size=size
        self.cache = []

    def get(self, key):
        if len(self.cache)!=0:
            for k,val in self.cache:
                if k==key:
                    return val
        return None

    def add(self, key, val):
        if self.get(key) is None:
            if len(self.cache)>self.cache_size:
                self.cache=self.cache[:-1]
            self.cache.insert(0,(key,val))


