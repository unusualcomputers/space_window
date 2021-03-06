from __future__ import unicode_literals
import threading
import sys
import logger

# run a function on a thread and keep track of result
# to use:
#   job=Job(function_name,(function_arg1,function_arg2))
# or with no arguments:
#   job=Job(function_name)
# then:
#   job.start()
# when finished:
#    job.done will be True
# if there was an exception, job.exception will contain it
# otherwise job.result will hold the result
class Job:
    def __init__(self, target, args=None):
        self.result=None
        self.done=False
        self.exception=None
        self.target=target
        self.args=args

    def _target(self):
        log=logger.get(__name__)
        try:
            if self.args is None:
                self.result=self.target()
            else:
                self.result=self.target(*self.args)
        except Exception as e:
            log.exception('exception in async job')
            self.exception=e
        finally:
            log.info('async job done %s ' % self.target)
            self.done=True

    def start(self):
        self.done=False
        threading.Thread(target=self._target).start()
