# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/BaseRallyMainWindow.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.rally import NavigationStack
from gui.Scaleform.daapi.view.meta.BaseRallyMainWindowMeta import BaseRallyMainWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from messenger import MessengerEntry
from messenger.gui.Scaleform.sf_settings import MESSENGER_VIEW_ALIAS
from messenger.proto.bw import find_criteria
__author__ = 'd_dichkovsky'

class BaseRallyMainWindow(View, AbstractWindowView, BaseRallyMainWindowMeta):

    def __init__(self):
        super(BaseRallyMainWindow, self).__init__()
        self._viewToLoad = None
        self._viewToUnload = None
        self._currentView = None
        self._isBackClicked = False
        return

    def getIntroViewAlias(self):
        return ''

    def getFlashAliases(self):
        return []

    def getPythonAliases(self):
        return []

    def getPrbType(self):
        return PREBATTLE_TYPE.NONE

    def getNavigationKey(self):
        return 'BaseRallyMainWindow'

    @property
    def chat(self):
        chat = None
        if MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT in self.components:
            chat = self.components[MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT]
        return chat

    def canGoBack(self):
        return self._currentView != self.getIntroViewAlias()

    def onBackClick(self):
        self._isBackClicked = True
        self._goToNextView()

    def _goToNextView(self, closeForced = False):
        if NavigationStack.hasHistory(self.getNavigationKey()):
            self._viewToUnload = NavigationStack.current(self.getNavigationKey())
            self._viewToLoad = NavigationStack.prev(self.getNavigationKey())
            if self._viewToLoad is None:
                self._requestViewLoad(self.getIntroViewAlias(), None, closeForced=closeForced)
            else:
                self._processStacks(closeForced=closeForced)
        else:
            self._requestViewLoad(self.getIntroViewAlias(), None, closeForced=closeForced)
        return

    def _requestViewLoad(self, flashAlias, itemID, closeForced = False):
        flashAliases = self.getFlashAliases()
        pythonAliases = self.getPythonAliases()
        if flashAlias in flashAliases:
            pyAlias = pythonAliases[flashAliases.index(flashAlias)]
            self._viewToLoad = (flashAlias, pyAlias, itemID)
            self._processStacks(closeForced=closeForced)
        else:
            LOG_ERROR('Passed flash alias is not registered:', flashAlias)

    def _closeCallback(self, canBeClosed):
        self._viewToUnload = None
        if canBeClosed:
            NavigationStack.nav2Prev(self.getNavigationKey())
            self._processStacks()
        return

    def _processStacks(self, closeForced = False):
        if self._viewToUnload is not None:
            flashAlias, pyAlias, itemID = self._viewToUnload
            pyView = self.components.get(pyAlias)
            if pyView is not None:
                if not closeForced:
                    pyView.canBeClosed(lambda canBeClosed: self._closeCallback(canBeClosed))
                else:
                    self._closeCallback(True)
        elif self._viewToLoad is not None:
            flashAlias, pyAlias, itemID = self._viewToLoad
            self._currentView = flashAlias
            self.as_loadViewS(flashAlias, pyAlias)
            self._isBackClicked = False
        return

    def _dispose(self):
        chat = self.chat
        if chat:
            chat.minimize()
        self._viewToLoad = None
        self._viewToUnload = None
        self._currentView = None
        super(BaseRallyMainWindow, self)._dispose()
        self.removeListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self._handleChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BaseRallyMainWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            channels = MessengerEntry.g_instance.gui.channelsCtrl
            controller = None
            if channels:
                controller = channels.getControllerByCriteria(find_criteria.BWPrbChannelFindCriteria(self.getPrbType()))
            if controller is not None:
                controller.setView(viewPy)
            else:
                self.addListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self._handleChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
            return
        else:
            if self._viewToLoad is not None:
                NavigationStack.nav2Next(self.getNavigationKey(), *self._viewToLoad)
                flashAlias, pyAlias, itemID = self._viewToLoad
                if pyAlias == alias:
                    viewPy.setData(itemID)
                    self._viewToLoad = None
            return

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(BaseRallyMainWindow, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            chat = self.chat
            if chat:
                chat.removeController()

    def _handleChannelControllerInited(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType', 0)
        if prbType is 0:
            LOG_ERROR('Prebattle type is not defined', ctx)
            return
        else:
            controller = ctx.get('controller')
            if controller is None:
                LOG_ERROR('Channel controller is not defined', ctx)
                return
            if prbType is self.getPrbType():
                chat = self.chat
                if chat is not None:
                    controller.setView(chat)
            return
