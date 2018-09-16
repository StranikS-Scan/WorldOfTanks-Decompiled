# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/impl.py


class IGuiLoader(object):

    @property
    def resourceManager(self):
        raise NotImplementedError

    @property
    def windowsManager(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
