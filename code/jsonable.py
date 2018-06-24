import jsonpickle
import io
import os

# base class for object that can be serialised to Json
# subclasses should implement class methods to load, something like:
#
#    @classmethod
#    def load(cls):
#        if not cls.file_exists(_base_path):
#            os.mkdir(_base_path)
#        path=_config_path
#        if cls.file_exists(path):
#            return cls.from_file(path)
#        s=cls()
#        s.save()
#        return s                

class Jsonable(object):

    @classmethod
    def file_exists(self, path):
        try:
            os.stat(path)
            return True
        except:
            return False
            
    def to_json(self):
        return jsonpickle.encode(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__class__) + ': ' + str(self.__dict__)      
    
    def __eq__(self,other):
        return self.__dict__==other.__dict__
        
    @classmethod
    def from_json(cls,json_string):
        d=jsonpickle.decode(json_string)
        return d
        
    @classmethod
    def from_file(cls,path):
        f=io.open(path,'r',encoding='utf-8')
        return cls.from_json(f.read())

    def to_file(self,path):
        f=io.open(path,'w',encoding='utf8')
        f.write(unicode(self.to_json()))

