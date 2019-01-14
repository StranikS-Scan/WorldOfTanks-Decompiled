# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ub_view_adaptor.py
import BigWorld
from frameworks.wulf import WindowStatus, WindowFlags
from frameworks.wulf import Window
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.view_interface import ViewInterface
from gui.Scaleform.framework.settings import UIFrameworkImpl
from soft_exception import SoftException

class UnboundViewAdaptor(DisposableEntity, ViewInterface):

    def __init__(self):
        super(UnboundViewAdaptor, self).__init__()
        self.__window = None
        self.__loadID = None
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        return

    @property
    def view(self):
        return self.__window.content

    @property
    def uiImpl(self):
        return UIFrameworkImpl.UNBOUND

    @property
    def viewType(self):
        return self.view.viewType

    @property
    def viewScope(self):
        return self.__scope

    @property
    def key(self):
        return ViewKey(self.view.layoutID, self.view.uniqueID)

    @property
    def alias(self):
        return self.view.layoutID

    @property
    def uniqueName(self):
        return self.view.uniqueID

    @property
    def settings(self):
        return None

    @property
    def soundManager(self):
        return None

    def isViewModal(self):
        return False

    def getAlias(self):
        return self.view.layoutID

    def setAlias(self, alias):
        raise SoftException('This method is not implemented')

    def getSubContainersSettings(self):
        pass

    def getUniqueName(self):
        return self.view.uniqueID

    def setUniqueName(self, name):
        raise SoftException('This method is not implemented')

    def getCurrentScope(self):
        return self.__scope

    def setCurrentScope(self, scope):
        self.__scope = scope

    def isLoaded(self):
        return False if self.__window is None else self.__window.windowStatus == WindowStatus.LOADED

    def setView(self, view):
        self.__window = Window(WindowFlags.WINDOW, content=view)
        self.__window.onStatusChanged += self.__onStatusChanged

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
        if self.__window is None:
            return
        else:
            self.__window.onStatusChanged -= self.__onStatusChanged
            self.__window.destroy()
            self.__window = None
            return

    def __onStatusChanged(self, state):
        if state == WindowStatus.LOADED:
            self.create()
        elif state == WindowStatus.DESTROYED:
            self.destroy()

    def __startToLoad(self):
        self.__loadID = None
        if self.__window is None:
            raise SoftException('Window is not defined.')
        self.__window.load()
        return
