
_html_template_main=u"""
<!doctype html>
<html>
<head>
    <title>Space Window</title>
    <meta name="description" content"Space Window">
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
    <meta http-equiv="Pragma" content="no-cache"/>
    <meta http-equiv="Expires" content="-1"/>
    [%REFRESH%]
<style>
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
</style>
</head>
<body>
<h1>Space Window</h1>
<br><br>
[%HTML_BODY%]
<br><br><br>
<footer>
Brought to you by <a href="https://unusualcomputerscollective.org/" target="_blank"> unusual computers collective </a> (also on <a href="https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective" target="_blank"> github </a>)
</footer>

</body>

"""           
html_upload="""
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
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type="file"] {
            display: none;
        }
        .custom-file-upload {
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
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
</style>
</head>
<body>
<h1>Space Window</h1>
<br><br>
    <form enctype="multipart/form-data" action="/upload_video" method="post"> 
    <input type="text" name="name" value="NAME">
    <br><br>
    Video file 
    <label class="custom-file-upload">
        <input type="hidden" name="hiddenfile_CNT" value="FILE">
        <input type="file" name = "video"/>
        <i class="fa fa-cloud-upload"></i> Choose file
    </label>
    <br><br>
    Subtitles 
    <label class="custom-file-upload">
        <input type="hidden" name="hiddensrt_CNT" value="SRT">
        <input type="file" name = "subs"/>
        <i class="fa fa-cloud-upload"></i> Choose file
    </label>
    <p><input type="submit" value="Upload"></p>
    </form>
<br><br><br>
<footer>
Brought to you by <a href="https://unusualcomputerscollective.org/" target="_blank"> unusual computers collective </a> (also on <a href="https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective" target="_blank"> github </a>)
</footer>

</body>

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
    <input type="submit" value="Add">
</form></div>
<br/>
<hr/>
<br/>
<table width=100%>
<tr>
<td>
    <form action="/slideshow">
    <input type="hidden" name="hiddennasa_CNT" value="NASAPOD">
    <input type="submit" value="Nasa POD">
    </form>
</td><td>
    <form action="/next">
    <input type="hidden" name="hiddenplay_CNT" value="NEXT">
    <input type="submit" value="Play next">
    </form>
</td><td>
    <form action="/upload" target="_blank">
    <input type="hidden" name="hiddenupload_CNT" value="UPLOAD">
    <input type="submit" value="Upload Video">
    </form>
</td><td>
    <form action="/rough" target="_blank">
    <input type="hidden" name="hiddenrough_CNT" value="ROUGH">
    <input type="submit" value="Radio Rough">
    </form>
</td><td>
    <form action="/refresh_caches">
    <input type="hidden" name="hiddenrefresh_CNT" value="REFRESH_CACHES">
    <input type="submit" value="Refresh Caches">
    </form>
    </td>
<td>
    <form action="/clock">
    <input type="hidden" name="hiddenclock_CNT" value="CLOCK">
    <input type="submit" value="Clock">
    </form>
</td><!--<td>
    <form action="/kodi">
    <input type="hidden" name="hiddenkodi_CNT" value="KODI">
    <input type="submit" value="kodi :)">
    </form>
</td>-->
<!--<td>
    <form action="/reboot">
    <input type="hidden" name="hiddenreboot_CNT" value="REBOOT">
    <input type="submit" value="Reboot">
    </form>
</td>-->
<td>
    <form action="/shutdown">
    <input type="hidden" name="hiddenshutdown_CNT" value="SHUTDOWN">
    <input type="submit" value="Shutdown">
    </form>
</td><td>
    <form action="/wifi">
    <input type="hidden" name="hiddenwifi_CNT" value="WIFI">
    <input type="submit" value="Change WiFi">
    </form>
</td>
</tr>
</table>    
"""

html_error="""
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
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
</style>
</head>
<body>
<h1>Space Window</h1>
<br><br>
[%ERROR_TEXT%]
<br><br><br>
<footer>
Brought to you by <a href="https://unusualcomputerscollective.org/" target="_blank"> unusual computers collective </a> (also on <a href="https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective" target="_blank"> github </a>)
</footer>

</body>

"""           
_cnt=0
def build_html(body,refresh_time=None):
    global _cnt
    if refresh_time is None:
        refresh=''
    else:
        refresh_html=\
            '<meta http-equiv="refresh" content="{}" >'.format(refresh_time)

    html = _html_template_main.replace('[%REFRESH%]',refresh).\
        replace('[%HTML_BODY%]',body)
    _cnt+=1
    cntstr='%i' % _cnt
    return html.replace('CNT',cntstr)

def get_main_html(rows_html,refresh_time=None):
    global _cnt
    if refresh_time is None:
        refresh=''
    else:
        refresh_html=\
            '<meta http-equiv="refresh" content="{}" >'.format(refresh_time)

    html = _html_template_main.replace('HTML_BODY',_main_table).\
        replace('STREAM_ROWS',rows_html).replace('[%REFRESH%]',refresh)
    _cnt+=1
    cntstr='%i' % _cnt
    return html.replace('CNT',cntstr)

def get_upload_html():
    _cnt+=1
    cntstr='%i' % _cnt
    return html_upload.replace('CNT',cntstr)

def get_error_html(err):
    return html_error.replace('[%ERROR_TEXT%]',err)
