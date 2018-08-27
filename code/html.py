import random

_html_header=u"""
<!doctype html>
<html>
<head>
    <title>Space Window</title>
    <meta name="description" content"Space Window">
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
    <meta http-equiv="Pragma" content="no-cache"/>
    <meta http-equiv="Expires" content="-1"/>
<style>
        a {
            color: #ff8000;
        }
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type=text]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        button[type=submit]{
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
        .center{text-align:center;}
</style>
</head>
<body>
<a href="/"><h1>Space Window</h1></a>
<br><br>
"""

_html_footer=u"""
<br><br>
<footer>
Brought to you by <a href="https://unusualcomputerscollective.org/" target="_blank">unusual computers collective</a> (also on <a href="https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective" target="_blank">github</a>)
</footer>

</body>

"""
_html_template_main=u"""
[%HEADER%]
[%HTML_BODY%]
[%FOOTER%]
"""           
_html_upload="""
[%HEADER%]
<form enctype="multipart/form-data" action="/upload_video" method="post"> 
<input type="text" name="name" value="NAME">
<br><br>
Video file 
    <input type="file" name = "video"/>
<br><br>
Subtitles 
    <input type="file" name = "subs"/>
<p><input type="submit" value="Upload"></p>
</form>
[%FOOTER%]
"""
_main_table=u"""

<div align="left">
<form align="center" action="/play_remove">
    <table width=100%>
    STREAM_ROWS
    </table>
    </form></div>
    <br/>
    <hr/>
    <br/>
    <div align="left">
    <form align="center" action="/add_link">
    <input type="text" name="name" value="NAME">
    <input type="text" name="link" value="LINK">
    <input type="text" name="quality" value="default">
    <input type="hidden" name="hiddenadd_CNT" value="ADDLINK">
    <input type="submit" value="Add stream">
</form></div>
<br/>
<hr/>
<br/>
<table width=100%>
<tr>
<td class="center">
    <form action="/slideshow">
    <input type="hidden" name="hiddennasa_CNT" value="NASAPOD">
    <input type="submit" value="Nasa POD">
    </form>
</td><td class="center">
    <form action="/next">
    <input type="hidden" name="hiddenplay_CNT" value="NEXT">
    <input type="submit" value="Play next">
    </form>
</td><td class="center">
    <form action="/rough" target="_blank">
    <input type="hidden" name="hiddenrough_CNT" value="ROUGH">
    <input type="submit" value="Radio">
    </form>
</td><td class="center">
    <form action="/clock">
    <input type="hidden" name="hiddenclock_CNT" value="CLOCK">
    <input type="submit" value="Clock">
    </form>
</td><td class="center">
    <form action="/gallery">
    <input type="hidden" name="hiddengallery_CNT" value="GALLERY">
    <input type="submit" value="Gallery">
    </form>
</td><!--<td class="center">
    <form action="/kodi">
    <input type="hidden" name="hiddenkodi_CNT" value="KODI">
    <input type="submit" value="kodi :)">
    </form>
</td>-->
</tr>
<tr><td colspan="4"><br/><br/></td></tr>
<tr>
<td class="center">
    <form action="/upload">
    <input type="hidden" name="hiddenupload_CNT" value="UPLOAD">
    <input type="submit" value="Upload video">
    </form>
</td><td class="center">
    <form action="/configuration">
    <input type="hidden" name="hiddenconfig_CNT" value="CONFIGURATION">
    <input type="submit" value="Configuration">
    </form>
</td>
<!--<td class="center">
    <form action="/refresh_caches">
    <input type="hidden" name="hiddenrefresh_CNT" value="REFRESH_CACHES">
    <input type="submit" value="Clear cache">
    </form>
</td>-->
<td class="center">
    <form action="/update_sw">
    <input type="hidden" name="hiddenupdate_CNT" value="UPDATE">
    <input type="submit" value="Update">
    </form>
</td>
<td class="center">
    <form action="/reboot">
    <input type="hidden" name="hiddenreboot_CNT" value="REBOOT">
    <input type="submit" value="Reboot">
    </form>
</td>
<td class="center">
    <form action="/shutdown">
    <input type="hidden" name="hiddenshutdown_CNT" value="SHUTDOWN">
    <input type="submit" value="Shutdown">
    </form>
</td>
<!--<td class="center">
    <form action="/wifi">
    <input type="hidden" name="hiddenwifi_CNT" value="WIFI">
    <input type="submit" value="Change WiFi">
    </form>
</td>-->
</tr>
</table>    
"""

_main_table_standalone=u"""

<div align="left">
<form align="center" action="/play_remove">
    <table width=100%>
    STREAM_ROWS
    </table>
    </form></div>
    <br/>
    <hr/>
    <br/>
<br/>
<hr/>
<br/>
<table width=100%>
<tr>
<td>
    <form action="/scan_wifi">
    <input type="hidden" name="hiddenscan_CNT" value="SCANWIFI">
    <input type="submit" value="Scan Wifi">
    </form>
</td><td>
    <form action="/upload" target="_blank">
    <input type="hidden" name="hiddenupload_CNT" value="UPLOAD">
    <input type="submit" value="Upload Video">
    </form>
</td><td class="center">
    <form action="/gallery">
    <input type="hidden" name="hiddengallery_CNT" value="GALLERY">
    <input type="submit" value="Gallery">
    </form>
</td><td>
    <form action="/reboot">
    <input type="hidden" name="hiddenreboot_CNT" value="REBOOT">
    <input type="submit" value="Reboot">
    </form>
</td>
<td>
    <form action="/shutdown">
    <input type="hidden" name="hiddenshutdown_CNT" value="SHUTDOWN">
    <input type="submit" value="Shutdown">
    </form>
</td>
<td>
    <form action="/reset_wifi">
    <input type="hidden" name="hiddenn_reset_wifi_CNT" value="RESET_WIFI">
    <input type="submit" value="Reset WiFi">
    </form>
</td>




</tr>
</table>    
"""

_cnt=random.randint(0,1000)
def _head_foot(html):
    return html.replace('[%HEADER%]',_html_header).replace('[%FOOTER%]',_html_footer)

def _count(html):
    global _cnt
    _cnt+=1
    cntstr='%i' % _cnt
    return html.replace('CNT',cntstr)

def build_html(body):
    html = _head_foot(_html_template_main).replace('[%HTML_BODY%]',body)
    return _count(html)

def get_standalone_html(rows_html):
    html = _head_foot(_html_template_main).\
        replace('[%HTML_BODY%]',_main_table_standalone).\
        replace('STREAM_ROWS',rows_html)
    return _count(html)

def get_main_html(rows_html):
    html = _head_foot(_html_template_main).replace('[%HTML_BODY%]',_main_table).\
        replace('STREAM_ROWS',rows_html)
    return _count(html)

def get_upload_html():
    return _count(_head_foot(_html_upload))

def get_empty_html(err):
    return build_html(err)
