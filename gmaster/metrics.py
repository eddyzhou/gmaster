import threading
import os

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
except ImportError:
    # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, multiprocess, CollectorRegistry
from prometheus_client.multiprocess import mark_process_dead


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            output = generate_latest(registry)
        except:
            self.send_error(500, 'error generating metric output')
            raise
        self.send_response(200)
        self.send_header('Content-Type', CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(output)

    def log_message(self, format, *args):
        return


def start_http_server(port, addr=''):
    """Starts an HTTP server for prometheus metrics as a daemon thread"""
    class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
        pass
    class PrometheusMetricsServer(threading.Thread):
        def run(self):
            httpd = ThreadingSimpleServer((addr, port), MetricsHandler)
            httpd.serve_forever()
    t = PrometheusMetricsServer()
    t.daemon = True
    t.start()


def clear_metrics_file():
    try:
        path = os.environ.get('prometheus_multiproc_dir')
        fs = os.listdir(path)
        files = [os.path.join(path, f) for f in fs]
        map(os.remove, files)
    except:
        pass


def start_metrics_server(metrics_port):
    clear_metrics_file()
    start_http_server(metrics_port)


def handle_process_dead(pid):
    try:
        mark_process_dead(pid)
    except:
        pass
