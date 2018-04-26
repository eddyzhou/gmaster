import os

try:
    from setproctitle import setproctitle
except ImportError:
    def setproctitle(title):
        return

try:
    from os import closerange
except ImportError:
    def closerange(fd_low, fd_high):
        for fd in range(fd_low, fd_high):
            try:
                os.close(fd)
            except OSError:
                pass


REDIRECT_TO = getattr(os, 'devnull', '/dev/null')


def getcwd():
    # get current path, try to use PWD env first
    try:
        a = os.stat(os.environ['PWD'])
        b = os.stat(os.getcwd())
        if a.st_ino == b.st_ino and a.st_dev == b.st_dev:
            cwd = os.environ['PWD']
        else:
            cwd = os.getcwd()
    except:
        cwd = os.getcwd()
    return cwd


def daemonize():
    if os.fork():
        os._exit(0)
    os.setsid()

    if os.fork():
        os._exit(0)

    os.umask(0o22)

    # Remap all of stdin, stdout and stderr on to
    # /dev/null. The expectation is that users have
    # specified the --error-log option.
    closerange(0, 3)
    fd_null = os.open(REDIRECT_TO, os.O_RDWR)
    if fd_null != 0:
        os.dup2(fd_null, 0)

    os.dup2(fd_null, 1)
    os.dup2(fd_null, 2)

