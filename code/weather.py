from config_util import Config
import re
import requests

class Weather:
    def __init__(self):
        config = Config('space_window.conf',__file__)    
        location=config.get('weather','location',
            'United_Kingdom/England/London')
        self.url='https://www.yr.no/place/%s/forecast.xml' % location
        self.re_top=re.compile('<time from=.*?\/time>',re.S)
        self.re_desc=re.compile('<symbol number=\".*?\" name=\"(.*?)\"')
        self.re_temp=re.compile('<temperature unit=\".*?\" value=\"(.*?)"')
        #self.re_wind_dir=re.compile('<windDirection.*? code=\"(.*?)\"')
        self.re_wind_speed=\
            re.compile('<windSpeed.*? mps=\"(.*?)\".*?name=\"(.*?)"')

    def get(self):
        try:
            xml=requests.get(self.url).text
            now=re.search(self.re_top,xml).group(0)
            desc=re.search(self.re_desc,now).group(1)
            temp=re.search(self.re_temp,now).group(1)
            #wind_dir=re.search(self.re_wind_dir,now).group(1)
            wind_sp=re.search(self.re_wind_speed,now)
            #wind_speed=wind_sp.group(1)
            wind_desc=wind_sp.group(2)
            return '%s C  %s,%s' %(temp,desc,wind_desc) 
        except:
            return ""


if __name__=='__main__':
    print Weather().get() 
