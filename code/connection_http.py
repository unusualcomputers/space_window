import sys
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import wifi_control as wifi
import time
import socket
from subprocess import Popen
import shlex
import py_game_msg as msg
import pygame
from processes import *
import logger
import os
from threading import Timer
import random
from async_job import Job

_ap_name=wifi.ap_name
_to_launch=wifi.config.get('access-point','execute_when_connected')
_sleep_on_connect=wifi.config.getint('access-point','sleep_on_connect',10)

_log=logger.get(__name__)

if wifi.config.getbool('access-point','use_pygame',False):
    _msg=msg.MsgScreen()
else:
    _msg=None

_keep_running=True

def _default_reporting_func( s ):
    if _msg is not None:
        _msg.set_text( s )
    else:
        print s

_reporting_func=_default_reporting_func

def set_reporting_func( f ):
    global _reporting_func
    _reporting_func=f

def _report( s ): 
    _log.info(s)
    if _reporting_func: _reporting_func( s ) 

def _waiting_status(msg, job, args=None):
    waiting_job=Job(job,args)
    waiting_job.start()
       
    waiting_msg=msg+'\n'
    
    while not waiting_job.done:
        _report(waiting_msg)
        time.sleep(1)
        waiting_msg+='.'
    return waiting_job.result

_cnt=random.randint(0,1000)


_html_template=u"""
    <!doctype html>
    <html>
    <head>
        <title>%s - Wifi</title>
        <meta name="description" content"%s - WiFi">
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
        <meta http-equiv="Pragma" content="no-cache"/>
        <meta http-equiv="Expires" content="-1"/>
    <style>
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=password]{
            color: #ff8000;
            background-color: #800080;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
          }
    </style>
    </head>
    <body>

    <h1>%s - Wifi</h1>
    <br><br>

    <h3>Choose a network to connect to.<br/>
    Once you click "connect" this network will go down.<br/>
    Please follow instructions on your space window.</h3>
    <form align="left" action="/connect">
    <table width=100%%>
        WIFI_ROWS
    </table>
    </form>
    </body>
    """ % (_ap_name,_ap_name,_ap_name)

_ap_html_public=u"""
<tr><td>AP_NAME<td><input type="hidden" name="hiddenAP_NAMECNT" value="AP_NAME"></td><td></td><td><input type="submit" name="AP_NAME" value="connect"></td></tr>
"""

_ap_html_private=u"""
<tr><td>AP_NAME</td><td><input type="hidden" name="hiddenAP_NAMECNT" value="AP_NAME"></td><td><input size="10" type="password" name="password"></td><td><input type="submit" name="AP_NAME" value="connect"></td></tr>
"""
    
def _make_wifi_rows(): 
    ret = ''
    nd=wifi.list_network_data()
    if len(nd)==0:
        return '<h1>No networks found, refresh to try again.</h1>'
    
    for (adapter,name,tp) in nd:
        global _cnt
        cntstr='%i' % _cnt
        _cnt += 1
        if tp!='OPEN':
            ret+=_ap_html_private.replace(u'AP_NAME',name)\
                .replace('CNT',cntstr)
        else:
            ret+=_ap_html_public.replace(u'AP_NAME',name)\
                .replace('CNT',cntstr)
            
    return ret

def make_wifi_html():
    return _html_template.replace(u'WIFI_ROWS',_make_wifi_rows())

class StandaloneWifiServer(BaseHTTPRequestHandler):

    def _handle_start_wifi_req(self,params):
        wifi_name='noname'
        password=None
        for n in params:
            v=params[n]
            if v==['Connect']:
                wifi_name=n
            elif n=='password':
                password=v[0]
        _report('thanks! trying to connect to %s now\n' % wifi_name)
        #server.wfile.write(make_attempting_html())
        wifi.set_wifi(wifi_name,password)
        wifi.start_wifi()
        if test_connection():
            return True

        _report('can\'t connect to wifi :(\nbringing my wifi up again\nt' +
            'most likely you typed the password wrong\n'+
            'also, you may have to reboot')
        wifi.start_ap()
        self._return_to_front()
        return False

    def _return_to_front(self):
        self.send_response(301)
        self.send_header('Location', '/')
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def do_GET(self):
        global _keep_running
        try:
            params = parse_qs(urlparse(self.path).query)
            if 'connect' in self.path:
                if self._handle_start_wifi_req(params):
                    _keep_running=False
                    return
            elif 'scan' in self.path:
                html = make_wifi_html()
                self.wfile.write(html)
                return
            # front page
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            # Send the html message
            html = get_standalone_html('')
            self.wfile.write(html)
            return
        except:
            _report('something went very wrong :(\nbest to reboot')
            print sys.exc_info()[0]
            raise


def start_ap():
    try:
        _waiting_status('starting my own network',wifi.start_ap)
        #wifi.start_ap()
        hostname=socket.gethostname()
        _report('connect to network %s\n' % _ap_name +
            'then type %s.local in a browser\n' % hostname +
            'or %s if that doesn\'t work' % wifi.ap_ip)
        time.sleep(10)
    except:
        _log.exception('error starting access point')
        raise

def test_connection(s='checking wifi connection\n'+
            'be patient, this can take a few minutes\n'):                
    _report(s)
    msg=s
    for i in range(0,60):
        if wifi.is_connected():
            return True
        time.sleep(1)
        msg=msg+'.'
        _report(msg)
    return False

def run_wifi_server():
    try:
        start_ap()
        handler=StandaloneWifiServer
        server = HTTPServer(('', 80),handler )
        print 'Started httpserver.' 
        while(_keep_running):
            server.handle_request()
        
    except KeyboardInterrupt:
        server.socket.close()


def setup_wifi(sleep=_sleep_on_connect,display_details=True):
    ip=""
    try:
        if not test_connection():
            _report('not connected to wifi, starting my own network\n'+
                'this will take a minute or two')
            run_wifi_server()
    except:
        _report('something went very wrong :(\nbest to reboot')
        time.sleep(sleep)
        return  
    finally:
        if display_details:
            display_connection_details()
            time.sleep(sleep)

def configure_wifi(sleep=_sleep_on_connect,display_details=True):
    ip=""
    try:
        while not test_connection():
            _report('not connected to wifi, starting my own network\n'+
                'this will take a minute or two')
            run_wifi_server()
    except:
        _report('something went very wrong :(\nbest to reboot')
        time.sleep(sleep)
        return  
    finally:
        if display_details:
            display_connection_details()
            time.sleep(sleep)

def display_connection_details():
    connections=wifi.get_interfaces_info()
    # first check for wifi connections
    # but keep track of lan 
    lan=None
    for con in connections:
        if con.is_wifi: 
            if con.ssid is not None: 
                network=con.ssid
                ip_address=con.ip_address
                hostname=wifi.get_host_name()
                msg=('I am now on network %s\n'+
                    'and my name is %s.local\n'+
                    '(or %s if that fails)') % (network,hostname,ip_address)
                _report(msg)
                return
            else:
                print 'ssid is None, wifi will be ignored\n',con
        else:
            lan=con
    
        # no wifi, wired connection?
        if lan is not None:
            ip=con.ip_address
            hostname=socket.gethostname()
            msg=('connected\n'+
                'my name is %s.local\n'+
                '(or %s if that fails)') % (hostname,ip)
            _report(msg)
            return
    time.sleep(1)

if __name__ == "__main__":
    configure_wifi()
    if _to_launch is not None:
        Popen(shlex.split(_to_launch))    
