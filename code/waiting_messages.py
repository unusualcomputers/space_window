from html import build_html

class WaitingMsgs:
    def __init__(self):
        self._msgs=['','this may take a little while...',
        '...still at it...','...working hard, have some respect...',
        '...do be patient...','...after all, this is a little wonder...',
        '...if you prefer you can go to cinema instead...',
        '...thank you for your patience ;)...',
        '...this is taking time, like all good things...',
        '...admire the colors on the screen and wait...']
        self._current=0
        self.delay=10

    def _make_html(self,msg):
        body = u"""    
            <p style="font-size:35px">{}?</p>
        """.format(self.msg)
        return build_html(body,self.delay)
    
    def start(self):
        self._current=0
       
    def next(self,action_name=None):
        msg=self._msgs[self._current]
        self._current+=1
        if self._current >= len(self._msgs):
            self._current=0
        if action_name is not None:
            msg=action_name+'\n\n'+msg
        return msg

    def next_html(self,action_name=None):
        return self._make_html(self.next(action_name))    
