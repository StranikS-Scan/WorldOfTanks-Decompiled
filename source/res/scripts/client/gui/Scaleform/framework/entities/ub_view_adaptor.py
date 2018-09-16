# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ub_view_adaptor.py
import BigWorld
from frameworks.wulf import ViewStatus
from frameworks.wulf import View
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.view_interface import ViewInterface
from gui.Scaleform.framework.settings import UIFrameworkImpl
from soft_exception import SoftException

class UnboundViewAdaptor(DisposableEntity, ViewInterface):

    def __init__(self):
        super(UnboundViewAdaptor, self).__init__()
        self.__view = None
        self.__loadID = None
        return

    @property
    def uiImpl(self):
        return UIFrameworkImpl.UNBOUND

    @property
    def viewType(self):
        return self.__view.viewType

    @property
    def viewScope(self):
        return ScopeTemplates.DEFAULT_SCOPE

    @property
    def key(self):
        return ViewKey(self.__view.layoutID, self.__view.uniqueID)

    @property
    def alias(self):
        return self.__view.layoutID

    @property
    def uniqueName(self):
        return self.__view.uniqueID

    @property
    def settings(self):
        return None

    @property
    def soundManager(self):
        return None

    def isViewModal(self):
        return False

    def getAlias(self):
        return self.__view.layoutID

    def setAlias(self, alias):
        raise SoftException('This method is not implemented')

    def getSubContainersSettings(self):
        pass

    def getUniqueName(self):
        return self.__view.uniqueID

    def setUniqueName(self, name):
        raise SoftException('This method is not implemented')

    def getCurrentScope(self):
        return ScopeTemplates.DEFAULT_SCOPE

    def setCurrentScope(self, scope):
        raise SoftException('This method is not implemented')

    def isLoaded(self):
        return False if self.__view is None else self.__view.viewStatus == ViewStatus.LOADED

    def setView(self, view):
        self.__view = view
        self.__view.onStatusChanged += self.__onStatusChanged

    def loadView(self):
        if self.__loadID is not None:
            BigWorld.cancelCallback(self.__loadID)
            self.__loadID = None
        self.__loadID = BigWorld.callback(0.0, self.__startToLoad)
        return

    def _destroy(self):
        if self.__loadID is not None:
            BigWorld.cancelCallback(self.__loadID)
            self.__loadID = None
        if self.__view is None:
            return
        else:
            self.__view.onStatusChanged -= self.__onStatusChanged
            self.__view.destroy()
            self.__view = None
            return

    def __onStatusChanged(self, state):
        if state == ViewStatus.LOADED:
            self.create()
        elif state == ViewStatus.DESTROYED:
            self.destroy()

    def __startToLoad(self):
        self.__loadID = None
        if self.__view is None:
            raise SoftException('View is not defined.')
        self.__view.load()
        return
