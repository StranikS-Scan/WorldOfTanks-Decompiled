# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/blueprints_convert_sale_controller.py
from enum import Enum
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BLUEPRINTS_CONVERT_SALE_STARTED_SEEN
from helpers import dependency, isPlayerAccount
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IBlueprintsConvertSaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.system_messages import ISystemMessages
_ACTION_POSTFIX = '_BCS'

class BCSActionState(Enum):
    STARTED = 'begin'
    PAUSED = 'pause'
    RESTORE = 'restore'
    END = 'end'


class BlueprintsConvertSaleController(IBlueprintsConvertSaleController):
    __slots__ = ('_isEnabled',)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(BlueprintsConvertSaleController, self).__init__()
        self._isEnabled = False
        self._isStarted = False

    def onLobbyStarted(self, event):
        if not isPlayerAccount():
            return
        self._isEnabled = int(self._lobbyContext.getServerSettings().getBlueprintsConvertSaleConfig().isEnabled())
        self.__updateActionState()
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self._eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted

    def fini(self):
        self.__stop()
        super(BlueprintsConvertSaleController, self).fini()

    def onDisconnected(self):
        self.__stop()
        super(BlueprintsConvertSaleController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__stop()
        super(BlueprintsConvertSaleController, self).onAvatarBecomePlayer()

    def __stop(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        if 'blueprints_convert_sale_config' in diff:
            newState = int(self._lobbyContext.getServerSettings().getBlueprintsConvertSaleConfig().isEnabled())
            if self._isEnabled != newState and self._isStarted:
                state = BCSActionState.PAUSED if newState == 0 else BCSActionState.RESTORE
                self.__showNotification(state)
                self._isEnabled = newState

    def __onEventsCacheSyncCompleted(self, *_):
        self.__updateActionState()

    def __updateActionState(self):
        actions = self._eventsCache.getActions().keys()
        for name in actions:
            if _ACTION_POSTFIX in name:
                self._isStarted = True
                if not AccountSettings.getNotifications(BLUEPRINTS_CONVERT_SALE_STARTED_SEEN) and self._isEnabled:
                    AccountSettings.setNotifications(BLUEPRINTS_CONVERT_SALE_STARTED_SEEN, True)
                    self.__showNotification(BCSActionState.STARTED)
                return

        if self._isStarted:
            self._isStarted = False
            self.__showNotification(BCSActionState.END)

    def __showNotification(self, state):
        self._systemMessages.proto.serviceChannel.pushClientMessage({'data': '',
         'type': '',
         'state': state}, SCH_CLIENT_MSG_TYPE.BLUEPRINTS_CONVERT_SALE)
