import os
import signal

from .utils import setproctitle
from .metrics import handle_process_dead
from .log import gmaster_logger


class Worker(object):

    def __init__(self, server, args):
        self.server = server
        self.args = args

    def init_worker(self):
        self.init_signals()

    def run(self):
        pid = os.getpid()
        gmaster_logger.info('Worker[pid: %s] is running.' % pid)
        setproctitle('gmaster worker[pid=%s]' % pid)
        self.server.start()

    def stop(self):
        handle_process_dead(os.getpid())
        self.server.stop(self.args.graceful_timeout)

    def init_signals(self):
        for sig in (signal.SIGQUIT, signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.stop)
