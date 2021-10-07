# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_controller.py
import BigWorld
from bootcamp.Bootcamp import g_bootcamp
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from gui.server_events import settings
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IWotPlusNotificationController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages

class _INotificationStrategy(object):
    _systemMessages = dependency.descriptor(ISystemMessages)

    def notifyClient(self, lastSeenStatus, currentStatus, enableMsgId, disableMsgId):
        raise NotImplementedError


class _LoginNotificationStrategy(_INotificationStrategy):

    def notifyClient(self, lastSeenStatus, currentStatus, enableMsgId, disableMsgId):
        if not currentStatus:
            self._systemMessages.proto.serviceChannel.pushClientMessage({}, disableMsgId)
        elif lastSeenStatus != currentStatus:
            if not currentStatus:
                self._systemMessages.proto.serviceChannel.pushClientMessage({}, disableMsgId)
            else:
                self._systemMessages.proto.serviceChannel.pushClientMessage({}, enableMsgId)


class _SessionNotificationStrategy(_INotificationStrategy):

    def notifyClient(self, lastSeenStatus, currentStatus, enableMsgId, disableMsgId):
        if lastSeenStatus != currentStatus:
            if not currentStatus:
                self._systemMessages.proto.serviceChannel.pushClientMessage({}, disableMsgId)
            else:
                self._systemMessages.proto.serviceChannel.pushClientMessage({}, enableMsgId)


class WotPlusNotificationController(IWotPlusNotificationController):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(WotPlusNotificationController, self).__init__()
        self._validSessionStarted = False

    def onLobbyStarted(self, ctx):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.processSwitchNotifications()
        self._validSessionStarted = False if g_bootcamp.isRunning() else True

    def onAccountBecomeNonPlayer(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange

    def onDisconnected(self):
        self._validSessionStarted = False
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange

    def _getStrategy(self):
        return _SessionNotificationStrategy() if self._validSessionStarted else _LoginNotificationStrategy()

    def processSwitchNotifications(self):
        if g_bootcamp.isRunning():
            return
        serverSettings = self._lobbyContext.getServerSettings()
        isWotPlusEnabled = serverSettings.isRenewableSubEnabled()
        isEntryPointsEnabled = serverSettings.isWotPlusNewSubscriptionEnabled()
        isGoldReserveEnabled = serverSettings.isRenewableSubGoldReserveEnabled()
        isPassiveXpEnabled = serverSettings.isRenewableSubPassiveCrewXPEnabled()
        isTankRentalEnabled = serverSettings.isWotPlusTankRentalEnabled()
        isFreeDirectivesEnabled = serverSettings.isRenewableSubFreeDirectivesEnabled()
        with settings.wotPlusSettings() as dt:
            dt.setEntryPointsEnabledState(isEntryPointsEnabled)
            dt.setWotPlusEnabledState(isWotPlusEnabled)
            hasSubscription = BigWorld.player().renewableSubscription.isEnabled()
            if not isWotPlusEnabled or not hasSubscription:
                return
            strategy = self._getStrategy()
            strategy.notifyClient(dt.isGoldReserveEnabled, isGoldReserveEnabled, SCH_CLIENT_MSG_TYPE.WOTPLUS_GOLDRESERVE_ENABLED, SCH_CLIENT_MSG_TYPE.WOTPLUS_GOLDRESERVE_DISABLED)
            strategy.notifyClient(dt.isPassiveXpEnabled, isPassiveXpEnabled, SCH_CLIENT_MSG_TYPE.WOTPLUS_PASSIVEXP_ENABLED, SCH_CLIENT_MSG_TYPE.WOTPLUS_PASSIVEXP_DISABLED)
            strategy.notifyClient(dt.isTankRentalEnabled, isTankRentalEnabled, SCH_CLIENT_MSG_TYPE.WOTPLUS_TANKRENTAL_ENABLED, SCH_CLIENT_MSG_TYPE.WOTPLUS_TANKRENTAL_DISABLED)
            strategy.notifyClient(dt.isFreeDirectivesEnabled, isFreeDirectivesEnabled, SCH_CLIENT_MSG_TYPE.WOTPLUS_FREEDIRECTIVES_ENABLED, SCH_CLIENT_MSG_TYPE.WOTPLUS_FREEDIRECTIVES_DISABLED)
            dt.setGoldReserveEnabledState(isGoldReserveEnabled)
            dt.setPassiveXpState(isPassiveXpEnabled)
            dt.setTankRentalState(isTankRentalEnabled)
            dt.setFreeDirectivesState(isFreeDirectivesEnabled)

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.processSwitchNotifications()
