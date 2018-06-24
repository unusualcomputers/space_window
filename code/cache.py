import threading

# simple limited size caches for things
# 
# SynchronisedCache is for multithreaded use, it will lock when accessing values
# Cache is for single threaded use

class SynchronisedCache:
    def __init__(self, size):
        self.cache_size=size
        self.cache = []
        self.lock=threading.Lock()

    def get(self, key):
        with self.lock:
            if len(self.cache)!=0:
                for k,val in self.cache:
                    if k==key:
                        self.lock.release()
                        return val
            return None

    def add(self, key, val):
        if self.get(key) is None:
            with self.lock:
                if len(self.cache)>self.cache_size:
                    self.cache=self.cache[:-1]
                self.cache.insert(0,(key,val))
        else:
            self.remove(key)
            self.add(key,val)

    def remove(self,key):
        with self.lock():
            new_cache=[]
            for k,val in self.cache:
                if k!=key: self.cache.append((key,val))
            self.cache=new_cache        

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
        else:
            self.remove(key)
            self.add(key,val)

    def remove(self,key):
        new_cache=[]
        for k,val in self.cache:
            if k!=key: self.cache.append((key,val))
        self.cache=new_cache        
