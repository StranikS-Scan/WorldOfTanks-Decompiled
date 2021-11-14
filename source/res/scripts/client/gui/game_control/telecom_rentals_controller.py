# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/telecom_rentals_controller.py
import BigWorld
from bootcamp.Bootcamp import g_bootcamp
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import settings
from helpers import dependency
from skeletons.gui.game_control import ITelecomRentalsNotificationController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
from telecom_rentals_common import TELECOM_RENTALS_CONFIG, PARTNERSHIP_BLOCKED_TOKEN_NAME

class TelecomRentalsNotificationController(ITelecomRentalsNotificationController):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(TelecomRentalsNotificationController, self).__init__()
        _systemMessages = dependency.descriptor(ISystemMessages)

    def onLobbyStarted(self, ctx):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.processSwitchNotifications()

    def onAccountBecomeNonPlayer(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange

    def onDisconnected(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self, True)

    def processSwitchNotifications(self):
        if g_bootcamp.isRunning():
            return
        serverSettings = self._lobbyContext.getServerSettings()
        isEnabled = serverSettings.isTelecomRentalsEnabled()
        with settings.telecomRentalsSettings() as dt:
            hasPartnership = BigWorld.player().telecomRentals.hasPartnership()
            if not hasPartnership:
                return
            isBlocked = BigWorld.player().telecomRentals.isBlocked()
            if not isBlocked and isEnabled != dt.isTelecomRentalsEnabled:
                if isEnabled:
                    self._showNotification(SystemMessages.SM_TYPE.FeatureSwitcherOn, backport.text(R.strings.system_messages.telecom_rentals.switch_on.title()), '')
                else:
                    self._showNotification(SystemMessages.SM_TYPE.WarningHeader, backport.text(R.strings.system_messages.telecom_rentals.switch_off.title()), backport.text(R.strings.system_messages.telecom_rentals.switch_off.body()))
            elif isEnabled and isBlocked != dt.isTelecomRentalsBlocked:
                if isBlocked:
                    self._showNotification(SystemMessages.SM_TYPE.WarningHeader, backport.text(R.strings.system_messages.telecom_rentals.switch_off.title()), backport.text(R.strings.system_messages.telecom_rentals.switch_off.body()))
                else:
                    self._showNotification(SystemMessages.SM_TYPE.FeatureSwitcherOn, backport.text(R.strings.system_messages.telecom_rentals.switch_on.title()), '')
            dt.setTelecomRentalsEnabledState(isEnabled)
            dt.setTelecomRentalsBlockedState(isBlocked)

    def _showNotification(self, msgType, title, body):
        SystemMessages.pushMessage(type=msgType, text=body, messageData={'header': title})

    def _onServerSettingsChange(self, diff):
        if TELECOM_RENTALS_CONFIG in diff:
            self.processSwitchNotifications()

    def __onTokensUpdate(self, diff):
        if PARTNERSHIP_BLOCKED_TOKEN_NAME in diff.keys():
            self.processSwitchNotifications()
