# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_dialog_window.py
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import sf_lobby
from gui.impl.pub.dialog_window import DialogWindow, DialogLayer
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController

class LobbyDialogWindow(DialogWindow):
    __slots__ = ()
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, content=None, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, enableBlur3dScene=True, layer=DialogLayer.TOP_WINDOW):
        if parent is None:
            app = self.__appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
        super(LobbyDialogWindow, self).__init__(content, bottomContent, parent, balanceContent, enableBlur, enableBlur3dScene, layer)
        return


class NYLobbyDialogWindow(LobbyDialogWindow):
    __newYearController = dependency.descriptor(INewYearController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def _initialize(self):
        super(NYLobbyDialogWindow, self)._initialize()
        self.__newYearController.onStateChanged += self.__onStateChanged
        self.__app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        self.__hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def _finalize(self):
        self.__newYearController.onStateChanged -= self.__onStateChanged
        self.__app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        super(NYLobbyDialogWindow, self)._finalize()

    @sf_lobby
    def __app(self):
        return None

    def __onStateChanged(self):
        if not self.__newYearController.isEnabled():
            self.destroy()

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias in (VIEW_ALIAS.BATTLE_QUEUE, VIEW_ALIAS.LOBBY_HANGAR):
            self.destroy()

    def __onSpaceDestroy(self, _):
        self.destroy()
