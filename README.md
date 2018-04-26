Overview
--------

A gRPC management tool like Gunicorn

Usage
-----

`prometheus_multiproc_dir` environment variable is needed, you should set it first.

Basic usage::

    $ gmaster [OPTIONS] --cls=APP_MODULE

Where ``APP_MODULE`` is of the pattern ``$(MODULE_NAME):$(VARIABLE_NAME)``. The
module name can be a full dotted path. The variable name refers to a gRPC server
that should be found in the specified module.

Example::

    $ gmaster --num=8 --bind=0.0.0.0:50051 --cls=server:app


Optional arguments:


```
  --bind BIND                 The socket to bind(A string of the form: ``HOST:PORT``)
  --cls  CLS                  gRPC server module [app:server]
  --num  NUM                  The number of worker processes for handling requests
  --pid  PID                  A filename to use for the PID file
  --graceful_timeout TIMEOUT  Timeout for graceful shutdown
  --metrics_port PORT         Metrics port
  --log_file PATH             Log path
```
