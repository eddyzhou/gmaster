import os
import sys
import signal
import errno
import time
import traceback
import random

from . import __version__
from .worker import Worker
from .pidfile import Pidfile
from .utils import getcwd, setproctitle, daemonize
from .log import gmaster_logger


class Arbiter(object):

    SIG_QUEUE = []
    SIGNALS = [getattr(signal, "SIG%s" % x)
               for x in "HUP QUIT INT TERM TTIN TTOU USR1 USR2 WINCH".split()]
    SIG_NAMES = dict(
        (getattr(signal, name), name[3:].lower()) for name in dir(signal)
        if name[:3] == "SIG" and name[3] != "_"
    )

    WORKERS = {}
    START_CTX = {}

    def __init__(self, app):
        self.app = app
        self.pid = None
        self.pidfile = None
        self.try_to_stop = False

        args = sys.argv[:]
        args.insert(0, sys.executable)
        cwd = getcwd()
        self.START_CTX = {
            'args': args,
            'cwd': cwd,
            'exectable': sys.executable
        }

    @property
    def num_workers(self):
        return self.app.args.num

    @num_workers.setter
    def num_workers(self, value):
        self.app.args.num = value

    def spawn_worker(self):
        worker = Worker(self.app.server, self.app.args)

        pid = os.fork()
        if pid != 0:
            # parent process
            self.WORKERS[pid] = worker
            return pid

        # child process
        try:
            gmaster_logger.info("Booting worker with pid: %s", os.getpid())
            worker.init_worker()
            worker.run()
            sys.exit(0)
        except:
            exc = traceback.format_exc()
            msg = 'Booting worker failed: \n\n[%s]'
            raise RuntimeError(msg % exc)
        finally:
            gmaster_logger.info("Worker exiting (pid: %s)", os.getpid())
            worker.stop()

    def spawn_workers(self):
        for _ in range(self.num_workers - len(self.WORKERS.keys())):
            self.spawn_worker()
            time.sleep(0.1 * random.random())

    def stop_workers(self):
        for pid, worker in self.WORKERS.items():
            worker.stop()
            del self.WORKERS[pid]
            self.kill_worker(pid, signal.SIGKILL)

    def kill_worker(self, pid, sig):
        try:
            os.kill(pid, sig)
        except OSError:
            pass

    def clean(self):
        self.stop_workers()
        if self.pidfile is not None:
            self.pidfile.unlink()

    def run(self):
        self.start()

        try:
            self.manage_workers()

            while True:
                if self.try_to_stop:
                    break

                sig = self.SIG_QUEUE.pop(0) if self.SIG_QUEUE else None

                if sig is None:
                    self.manage_workers()
                    continue

                if sig not in self.SIG_NAMES:
                    gmaster_logger.info("Ignoring unknown signal: %s", sig)
                    continue

                signame = self.SIG_NAMES.get(sig)
                handler = getattr(self, "handle_%s" % signame, None)
                if not handler:
                    gmaster_logger.error("Unhandled signal: %s", signame)
                    continue

                gmaster_logger.info("Handling signal: %s", signame)
                handler()
        except KeyboardInterrupt:
            self.clean()
            sys.exit(0)
        except:
            gmaster_logger.info("Unhandled exception in main loop",
                          exc_info=True)
            self.clean()
            sys.exit(-1)

        # gRPC master server should close first
        self.kill_worker(self.pid, signal.SIGKILL)

    def start(self):
        gmaster_logger.info("Starting gmaster %s", __version__)

        #if self.app.args.daemon:
        #    daemonize()

        self.pid = os.getpid()

        addr = self.app.args.bind
        self.app.server.bind(addr)

        gmaster_logger.info("Listening at: %s (pid:%s)", addr, self.pid)
        setproctitle('Gmaster[pid:%s]' % self.pid)

        self.init_signals()

        if self.app.args.pid:
            try:
                self.pidfile = Pidfile(self.app.args.pid)
                self.pidfile.create(self.pid)
            except:
                self.clean()
                raise

    def init_signals(self):
        for s in self.SIGNALS:
            signal.signal(s, self.signal)
        signal.signal(signal.SIGCHLD, self.handle_chld)

    def signal(self, sig, frame):
        if len(self.SIG_QUEUE) < 5:
            self.SIG_QUEUE.append(sig)

    def stop(self):
        self.clean()
        self.try_to_stop = True

    def handle_int(self):
        self.stop()

    def handle_quit(self):
        self.stop()

    def handle_usr1(self):
        self.stop()

    def handle_term(self):
        self.stop()

    def handle_ttin(self):
        """SIGTTIN handling.
        Increases the number of workers by one.
        """
        self.num_workers = self.num_workers + 1
        self.manage_workers()

    def handle_ttou(self):
        """SIGTTOU handling.
        Decreases the number of workers by one.
        """
        if self.num_workers <= 1:
            return
        self.num_workers -= 1
        self.manage_workers()

    def handle_chld(self, sig, frame):
        self.reap_workers()

    def reap_workers(self):
        """
        Reap workers to avoid zombie processes
        """
        try:
            while True:
                wpid, status = os.waitpid(-1, os.WNOHANG)
                if not wpid:
                    break
                else:
                    worker = self.WORKERS.pop(wpid, None)
                    if not worker:
                        continue
                    worker.stop()
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise

    def manage_workers(self):
        if len(self.WORKERS.keys()) < self.num_workers:
            self.spawn_workers()

        workers = self.WORKERS.items()
        while len(workers) > self.num_workers:
            (pid, _) = workers.pop(0)
            self.kill_worker(pid, signal.SIGTERM)