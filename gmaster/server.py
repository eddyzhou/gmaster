class ServerBase(object):

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def start(self):
        raise NotImplementedError()

    def bind(self, addr):
        raise NotImplementedError()

    def stop(self, grace_timeout=0):
        raise NotImplementedError()
