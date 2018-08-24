import ConfigParser
from os.path import *

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
        self.config.write(file(self.path))

    def restore_defaults(self):
        path=join(dirname(abspath(__file__)),'conf/space_window.defaults')
        self.config=ConfigParser.ConfigParser()
        self.config.read(path)
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

        clockfontsize=self.get('clock','time_size')
        clockborder=self.get('clock','border')

        nasafontsize=self.get('nasa','font_size')
        nasadelay=self.get('nasa','frame_delay')
        
        weatherloc=self.get('weather','location')

        omxargs=self.get('player','player_args')

        html = """ 
        <div align="right">
        <form align="center" action="/config_change">
            <input name="hidden_748" value="config" type="hidden">
            <table width="100%%">
            <tbody>
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
            <td>clock font size</td>
            <td><input name="clockfontsize" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>clock border</td>
            <td><input name="clockborder" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>nasa font size</td>
            <td><input name="nasafontsize" value="%s" type="text"></td>
            </tr>
            <tr>
            <td>nasa picture delay</td>
            <td><input name="nasadelay" value="%s" type="text"></td>
            </tr>
            <tr>
            <tr>
            <td>weather location</td>
            <td><input name="weatherloc" value="%s" type="text"></td>
            </tr>
            <td>omxplayer arguments</td>
            <td><input name=
                "omxargs" value="%s" type="text">
            </td>
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
        """ %(fontname,fontsize,txtr,txtg,txtb,bckr,bckg,bckb,clkr,clkg,clkb,
               clkbr,clkbg,clkbb,clockfontsize,clockborder,nasafontsize,
                nasadelay,weatherloc,omxargs )
        return html

    def parse_form_inputs(self,p):
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
        clocktimesize=p['clockfontsize'][0]
        self.set('clock','time_size',clocktimesize)
        clockdatesize=str(int(clocktimesize)/8)
        self.set('clock','date_size',clockdatesize)
        clockborder=p['clockborder'][0]
        self.set('clock','border',clockborder)
        clockseparation=str(int(clockdatesize)/3)
        self.set('clock','separation',separation)
        nasafontsize=p['nasafontsize'][0]
        self.set('nasa','font_size',nasafontsize)
        nasadelay=p['nasadelay'][0]
        self.set('nasa','frame_delay',nasadelay)
        weatherloc=p['weatherloc'][0]
        self.set('weather','location',weatherloc)
        omxargs=p['omxargs'][0]
        self.set('player','player_args',omxargs)

        
