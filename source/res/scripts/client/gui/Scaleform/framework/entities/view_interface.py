# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/view_interface.py


class ViewInterface(object):

    @property
    def uiImpl(self):
        raise NotImplementedError

    @property
    def layer(self):
        raise NotImplementedError

    @property
    def viewScope(self):
        raise NotImplementedError

    @property
    def key(self):
        raise NotImplementedError

    @property
    def alias(self):
        raise NotImplementedError

    @property
    def uniqueName(self):
        raise NotImplementedError

    @property
    def settings(self):
        raise NotImplementedError

    @property
    def soundManager(self):
        raise NotImplementedError

    def isViewModal(self):
        raise NotImplementedError

    def getAlias(self):
        raise NotImplementedError

    def setAlias(self, alias):
        raise NotImplementedError

    def getSubContainersSettings(self):
        raise NotImplementedError

    def getUniqueName(self):
        raise NotImplementedError

    def setUniqueName(self, name):
        raise NotImplementedError

    def getCurrentScope(self):
        raise NotImplementedError

    def setCurrentScope(self, scope):
        raise NotImplementedError
