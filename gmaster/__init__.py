__version__ = '0.2.1'
VERSION = tuple(map(int, __version__.split('.')))


def console_main():
    from . import app
    app.main()
