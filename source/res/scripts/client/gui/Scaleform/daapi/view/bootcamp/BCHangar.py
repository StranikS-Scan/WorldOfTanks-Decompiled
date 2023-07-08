# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangar.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import events
from helpers import dependency
from skeletons.tutorial import ITutorialLoader

class BCHangar(Hangar):
    tutorialLoader = dependency.descriptor(ITutorialLoader)
    DISABLE_ESC_FLAG = 'DisableEscapeMenuInHangar'

    def onEscape(self):
        topWindowContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if CurtainWindow.isOpened():
            return
        flags = self.tutorialLoader.tutorial.getFlags()
        if flags.isActiveFlag(self.DISABLE_ESC_FLAG):
            return
        if not self.__isViewOpenOrLoading(topWindowContainer, VIEW_ALIAS.LOBBY_MENU) and not self.__isViewOpenOrLoading(topWindowContainer, VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW) and not self.__isViewOpenOrLoading(topWindowContainer, VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO) and not self.__isViewOpenOrLoading(topWindowContainer, VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def showHelpLayout(self):
        pass

    def __isViewOpenOrLoading(self, container, viewAlias):
        openView = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: viewAlias})
        if openView is not None:
            return True
        else:
            for loadingView in container.getAllLoadingViews():
                if loadingView.alias == viewAlias:
                    return True

            return False
