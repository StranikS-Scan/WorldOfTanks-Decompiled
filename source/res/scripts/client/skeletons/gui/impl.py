# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/impl.py


class IGuiLoader(object):
    __slots__ = ()

    @property
    def resourceManager(self):
        raise NotImplementedError

    @property
    def windowsManager(self):
        raise NotImplementedError

    @property
    def systemLocale(self):
        raise NotImplementedError

    @property
    def implTypeMask(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class IOverlaysManager(object):
    __slots__ = ()

    def isSuspended(self, window):
        raise NotImplementedError

    def suspend(self, condition=None):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
