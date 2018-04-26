import os
import sys
import importlib
import traceback

from .config import parser
from .arbiter import Arbiter
from .utils import getcwd
from .log import gmaster_logger, log_setting
from .metrics import start_metrics_server


class Application(object):
    path = getcwd()
    sys.path.insert(0, path)

    def __init__(self, args):
        self.args = args
        self.server = None

    def run(self):
        self._load_class()
        if self.server:
            Arbiter(self).run()
        else:
            raise RuntimeError('server not being initialized')

    def _load_class(self):
        cls = self.args.cls
        try:
            module, var = cls.split(':')
            m = importlib.import_module(module)
            s = m.__dict__.get(var)
            if not s:
                s = eval(var, vars(m))

            if hasattr(s, 'start') and hasattr(s, 'stop'):
                self.server = s
            else:
                msg = 'server: %s not extends ServerBase'
                raise RuntimeError(msg % s)
        except:
            exc = traceback.format_exc()
            msg = 'class: %s invalid or not found: \n\n[%s]'
            raise RuntimeError(msg % (cls, exc))


def main():
    if 'prometheus_multiproc_dir' not in os.environ:
        raise RuntimeError('`prometheus_multiproc_dir` environ is missing')

    p = parser()
    args = p.parse_args()
    if args.log_file:
        log_setting(gmaster_logger, args.log_file)

    start_metrics_server(args.metrics_port)

    app = Application(args)
    app.run()


if __name__ == '__main__':
    main()