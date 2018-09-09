from __future__ import unicode_literals
import ConfigParser
import os
from os.path import *
import random
import logger


_log=logger.get(__name__)
_cnt=random.randint(0,1000) # global counter, used to make html more responsive
class Config:
    def __init__(self, filename, caller_file=None):
        if caller_file is None:
            path=join(dirname(abspath(__file__)),filename)
        else:
            path=join(dirname(abspath(caller_file)),filename)
        self.config=ConfigParser.ConfigParser()
        self.config.read(path)
        self.path=path

    def save(self):
        _log.info('saving config to %s' % self.path)        
        with open(self.path,'w') as cf:
            self.config.write(cf)

    def restore_defaults(self):
        player=self.get('player','player')
        player_args=self.get('player','player_args')
        player_playlist_args=self.get('player','playlist_player_args')
        nasa_height=self.get('nasa', 'height_ratio')
        ap_name=self.get('access-point','name')
        ap_ip=self.get('access-point','ip')
        ap_iprange=self.get('access-point','iprange')
        ap_driver=self.get('access-point','driver')
        ap_iface=self.get('access-point','interface')
        ap_pyg=self.get('access-point','use_pygame')
        
        path=join(dirname(abspath(__file__)),'conf/space_window.defaults')
        self.config=ConfigParser.ConfigParser()
        self.config.read(path)

        self.set('player','player',player)
        self.set('player','player_args',player_args)
        self.set('player','playlist_player_args',player_playlist_args)
        self.set('nasa', 'height_ratio',nasa_height)
        self.set('access-point','name',ap_name)
        self.set('access-point','ip',ap_ip)
        self.set('access-point','iprange',ap_iprange)
        self.set('access-point','driver',ap_driver)
        self.set('access-point','interface',ap_iface)
        self.set('access-point','use_pygame',ap_pyg)

        self.save() 

    def has(self, section, option):
        return self.config.has_section(section) and \
            self.config.has_option(section,option)

    def get(self, section, option, default=None):
        if self.has(section,option):
            return self.config.get(section,option)
        return default

    def set(self,section,option,value):
        self.config.set(section,option,value)
 
    def getint(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getint(section,option)
        return default

    def setint(self,section,option,value):
        self.config.set(section,option,str(value))
 
    def getfloat(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getfloat(section,option)
        return default

    def setfloat(self,section,option,value):
        self.config.set(section,option,str(value))
 
    def getbool(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getboolean(section,option)
        return default

    def setbool(self,section,option,value):
        self.config.set(section,option,str(value))
 
    def getcolor(self, section, option, default = None):
        if self.has(section,option):
            s=self.config.get(section,option)
            rgba=[int(i) for i in s.split(',')]
            if len(rgba) not in [3,4]: 
                raise 'colors must have 3 or 4 members,'+\
                     '%s in section %s is wrong' % (option, section) 
            return rgba
        return default
    
    def setcolor(self,section,option,r,g,b,a=None):
        if a is None:
            value = '%s,%s,%s' %(r,g,b)
        else:
            value = '%s,%s,%s,%s' %(r,g,b,a)
        self.config.set(section,option,value)


    def get_html(self):
        global _cnt
        _cnt+=1
        startwith=self.get('global','start_with')
        fontname=self.get('font','name')
        fontsize=self.get('message','font_size')
        txtcol=self.get('message','foreground').split(',')
        txtr=txtcol[0]
        txtg=txtcol[1]
        txtb=txtcol[2]

        bckcol=self.get('message','background').split(',')
        bckr=bckcol[0]
        bckg=bckcol[1]
        bckb=bckcol[2]

        clktxt=self.get('clock','foreground').split(',')
        clkr=clktxt[0]
        clkg=clktxt[1]
        clkb=clktxt[2]

        clkbck=self.get('clock','background').split(',')
        clkbr=clkbck[0]
        clkbg=clkbck[1]
        clkbb=clkbck[2]

        clocktimezone=self.get('clock','timezone')
        clocktimesize=self.get('clock','time_size')
        clockdatesize=self.get('clock','date_size')
        clockborder=self.get('clock','border')

        nasafontsize=self.get('nasa','font_size')
        nasadelay=self.get('nasa','frame_delay')

        gallerydelay=self.get('gallery','frame_delay')        
        weatherloc=self.get('weather','location')

        has_alsa='alsa' in self.get('player','player_args')
        if has_alsa:
            html_alsa=u"""
    <input type="radio" name="has_alsa" value="default" > Default<br/>
    <input type="radio" name="has_alsa" value="alsa" checked> Soundcard<br/>
        """
        else:
            html_alsa=u"""
    <input type="radio" name="has_alsa" value="default" checked> Default<br/>
    <input type="radio" name="has_alsa" value="alsa" > Soundcard<br/>
        """

        if startwith=='nasa':
            html_start_with=u"""
    <input type="radio" name="startwith" value="streams" > Streams<br/>
    <input type="radio" name="startwith" value="nasa" checked> Nasa POD<br/>
    <input type="radio" name="startwith" value="clock" > Clock<br/>
    <input type="radio" name="startwith" value="gallery" > Gallery<br/>
            """ 
        elif startwith=='clock':
            html_start_with=u"""
    <input type="radio" name="startwith" value="streams" > Streams<br/>
    <input type="radio" name="startwith" value="nasa" > Nasa POD<br/>
    <input type="radio" name="startwith" value="clock" checked> Clock<br/>
    <input type="radio" name="startwith" value="gallery" > Gallery<br/>
            """ 
        elif startwith=='gallery':
            html_start_with=u"""
    <input type="radio" name="startwith" value="streams" > Streams<br/>
    <input type="radio" name="startwith" value="nasa" > Nasa POD<br/>
    <input type="radio" name="startwith" value="clock" > Clock<br/>
    <input type="radio" name="startwith" value="gallery" checked> Gallery<br/>
            """ 
        else:
            html_start_with=u"""
    <input type="radio" name="startwith" value="streams" checked> Streams<br/>
    <input type="radio" name="startwith" value="nasa" > Nasa POD<br/>
    <input type="radio" name="startwith" value="clock" > Clock<br/>
    <input type="radio" name="startwith" value="gallery" > Gallery<br/>
            """ 

        html = u""" 
        <div align="right">
        <form align="center" action="/config_change">
            <input name="hidden_%s" value="config" type="hidden">
            <table width="100%%">
            <tbody>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>start with </td>
            <td>%s</td>
            <td colspan="2"> what to play first when booting up </td>
            </tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>font name</td>
            <td><input name="fontname" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>font size</td>
            <td><input name="fontsize" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>text color</td>
            <td><input name="textcolr" value="%s" type="text"></td>
            <td><input name="textcolg" value="%s" type="text"></td>
            <td><input name="textcolb" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>background color</td>
            <td><input name="backcolr" value="%s" type="text"></td>
            <td><input name="backcolg" value="%s" type="text"></td>
            <td><input name="backcolb" value="%s" type="text"></td>
            </tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>clock text color</td>
            <td><input name="clocktextcolr" value="%s" type="text"></td>
            <td><input name="clocktextcolg" value="%s" type="text"></td>
            <td><input name="clocktextcolb" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>clock background color</td>
            <td><input name="clockbackcolr" value="%s" type="text"></td>
            <td><input name="clockbackcolg" value="%s" type="text"></td>
            <td><input name="clockbackcolb" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>clock time zone</td>
            <td><input name="clocktimezone" value="%s" type="text"></td>
            <td colspan="2">time zone to use for the clock, for complete list checkout <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List">wikipedia</a> - it is the entry in column TZ*</td>
            </tr>
            <tr>
            <td>clock time size</td>
            <td><input name="clocktimesize" value="%s" type="text"></td>
            <td>size of time digits</td>
            </tr>
            <td>clock date size</td>
            <td><input name="clockdatesize" value="%s" type="text"></td>
            <td>size of date and wheater digits</td>
            </tr>
            <tr>
            <td>clock border</td>
            <td><input name="clockborder" value="%s" type="text"></td>
            </tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>nasa font size</td>
            <td><input name="nasafontsize" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>nasa picture delay</td>
            <td><input name="nasadelay" value="%s" type="text"></td>
            <td colspan="2">how long in seconds before changing to next picture</td>
            </tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>gallery picture delay</td>
            <td><input name="gallerydelay" value="%s" type="text"></td>
            <td colspan="2">how long in seconds before changing to next picture</td>
            </tr>
            <tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>weather location</td>
            <td><input name="weatherloc" value="%s" type="text"></td>
            <td colspan="2">
go to www.yr.no, find your location  and copy the last part of the web address here (for example: https://www.yr.no/place/United_Kingdom/England/London/ is address for london, the input in this field would then be: United_Kingdom/England/London) 
            </td>
            </tr>
            <tr><td colspan="4"><hr/></td></tr>
            <tr>
            <td>sound output</td>
            <td>%s</td>
            <td colspan="2">soundcard option should work for most sound cards and dac hats, it simply switches output to alsa though, you still have to make your card work with raspberry first</td>
            </tr>
            <tr><td><br/><br/></td></tr>
            <tr>
            <td/>
            <td>
                <button type="submit" name="action" value="apply conf">
                            Apply changes
                </button>
            </td>
            <td></td>
            <td>
                <button type="submit" name="action" value="restore conf">
                            Restore defaults
                </button>
            </td>
            </tr>
            </tbody></table>
            </form></div>
        """ %(_cnt,html_start_with,fontname,fontsize,txtr,txtg,txtb,
            bckr,bckg,bckb,clkr,clkg,clkb,clkbr,clkbg,clkbb,
            clocktimezone,clocktimesize,clockdatesize,clockborder,nasafontsize,
            nasadelay,gallerydelay,weatherloc,html_alsa)
        return html

    def parse_form_inputs(self,p):
        startwith=p['startwith'][0]
        self.set('global','start_with',startwith)
        fontname=p['fontname'][0]
        self.set('font','name',fontname)
        fontsize=p['fontsize'][0]
        self.set('message','font_size',fontsize)
        txtcol='%s,%s,%s' % (p['textcolr'][0],p['textcolg'][0],p['textcolb'][0])
        self.set('message','foreground',txtcol)
        bckcol='%s,%s,%s' % (p['backcolr'][0],p['backcolg'][0],p['backcolb'][0])
        self.set('message','background',bckcol)
        clktxt='%s,%s,%s' % (\
            p['clocktextcolr'][0],p['clocktextcolg'][0],p['clocktextcolb'][0])
        self.set('clock','foreground',clktxt)
        clkbck='%s,%s,%s' % (\
            p['clockbackcolr'][0],p['clockbackcolg'][0],p['clockbackcolb'][0])
        self.set('clock','background',clkbck)
        clocktimezone=p['clocktimezone'][0]
        self.set('clock','timezone',clocktimezone)
        clocktimesize=p['clocktimesize'][0]
        self.set('clock','time_size',clocktimesize)
        clockdatesize=p['clockdatesize'][0]
        self.set('clock','date_size',clockdatesize)
        clockborder=p['clockborder'][0]
        self.set('clock','border',clockborder)
        clockseparation=str(int(clockdatesize)/3)
        self.set('clock','separation',clockseparation)
        nasafontsize=p['nasafontsize'][0]
        self.set('nasa','font_size',nasafontsize)
        nasadelay=p['nasadelay'][0]
        self.set('nasa','frame_delay',nasadelay)
        gallerydelay=p['gallerydelay'][0]
        self.set('gallery','frame_delay',gallerydelay)
        weatherloc=p['weatherloc'][0]
        self.set('weather','location',weatherloc)

        has_alsa='alsa' in p['has_alsa'][0]
        has_alsa_current='alsa' in self.get('player','player_args')
        if has_alsa!=has_alsa_current:
            if has_alsa:
                self.set('player','player_args',
                    '-o alsa --timeout 60 --loop --no-osd -b') 
                self.set('player','playlist_player_args',
                    '-o alsa --timeout 60 --no-osd -b') 
                os.system("sed -i '/output/ c\output = alsasink' "+\
                    "/root/.config/mopidy/mopidy.conf")
            else: 
                self.set('player','player_args',
                    ' --timeout 60 --loop --no-osd -b') 
                self.set('player','playlist_player_args',
                    ' --timeout 60 --no-osd -b') 
                os.system("sed -i '/output/ c\#output = autoaudiosinkk' "+\
                    "/root/.config/mopidy/mopidy.conf")
