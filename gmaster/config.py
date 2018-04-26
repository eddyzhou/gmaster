import argparse
import os
import sys

from . import __version__


def parser():
    prog = os.path.basename(sys.argv[0])

    p = argparse.ArgumentParser(prog=prog, description='A gRPC management tool like Gunicorn')
    p.add_argument('-v', '--version',
                   action='version', default=argparse.SUPPRESS,
                   version='%s (version %s)\n' % (prog, __version__),
                   help="show program's version number and exit")
    p.add_argument('-b', '--bind', type=str, default='0.0.0.0:10024',
                   help='The socket to bind(A string of the form: ``HOST:PORT``)')
    p.add_argument('-c', '--cls', type=str, required=True,
                   help='gRPC server module [app:server]')
    p.add_argument('-n', '--num', type=int, default=1,
                   help='The number of worker processes for handling requests')
    p.add_argument('-p', '--pid', type=str,
                   help='A filename to use for the PID file')
    #p.add_argument('-d', '--daemon', type=int, default=0,
    #               help='Daemonize the gmaster process')
    p.add_argument('--graceful_timeout', type=int, default=3,
                   help='Timeout for graceful shutdown')
    p.add_argument('--metrics_port', type=int, default=10025,
                   help='Metrics port')
    p.add_argument('--log_file', type=str, default='',
                   help='Log path')
    return p