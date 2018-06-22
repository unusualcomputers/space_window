import threading

class Job:
    def __init__(self, target, args=None):
        self.result=None
        self.done=False
        self.target=target
        self.args=args
        self.exception=None

    def _target(self):
        try:
            if args is None:
                self.result=self.target()
            else:
                self.result=self.target(*args)
        except e:
            self.exception=e
        finally:
            self.done=True

    def start(self):
        self.done=False
        threading.thread(target=self.target,args=self.args).start()
