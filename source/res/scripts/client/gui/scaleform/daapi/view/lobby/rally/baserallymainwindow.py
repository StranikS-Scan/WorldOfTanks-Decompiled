# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/BaseRallyMainWindow.py
import BigWorld
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.prb_helpers import GlobalListener
from gui.Scaleform.locale.WAITING import WAITING
from gui.Scaleform.daapi.view.lobby.rally import NavigationStack
from gui.Scaleform.daapi.view.meta.BaseRallyMainWindowMeta import BaseRallyMainWindowMeta
from gui.shared.events import FocusEvent
from messenger.ext import channel_num_gen
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS

class BaseRallyMainWindow(BaseRallyMainWindowMeta, GlobalListener):
    LEADERSHIP_NOTIFICATION_TIME = 2.5

    def __init__(self, ctx = None):
        super(BaseRallyMainWindow, self).__init__()
        self._currentView = None
        self._isBackClicked = False
        self._leadershipNotificationCallback = None
        return

    def getClientID(self):
        return channel_num_gen.getClientID4Prebattle(self.getPrbType())

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.getClientID()}))

    def onSourceLoaded(self):
        if self.unitFunctional and not self.unitFunctional.hasEntity():
            self.destroy()

    def isPlayerInSlot(self, databaseID = None):
        pInfo = self.unitFunctional.getPlayerInfo(dbID=databaseID)
        return pInfo.isInSlot

    def getIntroViewAlias(self):
        return ''

    def getPrbType(self):
        return PREBATTLE_TYPE.NONE

    def getPrbChatType(self):
        return PREBATTLE_TYPE.UNIT

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

    def _applyViewLoad(self):
        super(BaseRallyMainWindow, self)._applyViewLoad()
        self._isBackClicked = False

    def _populate(self):
        super(BaseRallyMainWindow, self)._populate()
        self.startGlobalListening()
        self._showLeadershipNotification()

    def _dispose(self):
        self.stopGlobalListening()
        self._currentView = None
        self._clearLeadershipNotification()
        super(BaseRallyMainWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            events_dispatcher.rqActivateChannel(self.getClientID(), viewPy)
            return
        super(BaseRallyMainWindow, self)._onRegisterFlashComponent(viewPy, alias)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            events_dispatcher.rqDeactivateChannel(self.getClientID())
        super(BaseRallyMainWindow, self)._onUnregisterFlashComponent(viewPy, alias)

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
            if prbType is self.getPrbChatType():
                chat = self.chat
                if chat is not None:
                    controller.setView(chat)
            return

    def _showLeadershipNotification(self):
        functional = self.unitFunctional
        if functional and functional.getShowLeadershipNotification():
            self.as_showWaitingS(WAITING.PREBATTLE_GIVELEADERSHIP, {})
            self._leadershipNotificationCallback = BigWorld.callback(self.LEADERSHIP_NOTIFICATION_TIME, self._cancelLeadershipNotification)

    def _clearLeadershipNotification(self):
        if self._leadershipNotificationCallback is not None:
            BigWorld.cancelCallback(self._leadershipNotificationCallback)
            self._leadershipNotificationCallback = None
        return

    def _cancelLeadershipNotification(self):
        self._clearLeadershipNotification()
        functional = self.unitFunctional
        if functional:
            functional.doLeadershipNotificationShown()
        self.as_hideWaitingS()
