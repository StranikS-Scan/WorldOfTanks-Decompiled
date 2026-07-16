# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/voip_ctrl.py
from __future__ import absolute_import
import logging
import BigWorld
import typing
import CommandMapping
import Keys
import VOIP
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getKey
from last_stand.gui import ls_account_settings
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.battle_control.interfaces import ILSVOIPController
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from constants import IS_CHINA, REQUEST_COOLDOWN, ARENA_PERIOD, ARENA_BONUS_TYPE_IDS
from gui.battle_control import event_dispatcher
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage, ACTION_MESSAGE_TYPE
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager
_logger = logging.getLogger(__name__)

class LSVOIPController(ILSVOIPController):
    __slots__ = ('__cooldownCallback', '__isTeamChannelAvailable', '__messageShown')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, isTeamChannelAvailable=True):
        super(LSVOIPController, self).__init__()
        self.__messageShown = False
        self.__cooldownCallback = None
        self.__isTeamChannelAvailable = isTeamChannelAvailable
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.LS_VOIP_CTRL

    @property
    def isVoipSupported(self):
        return not IS_CHINA and self.voipManager.isVoiceSupported()

    @property
    def isVoipEnabled(self):
        return self.voipManager.isEnabled()

    @property
    def isJoined(self):
        return self.voipManager.isCurrentChannelEnabled()

    @property
    def isTeamVoipEnabled(self):
        return self.isVoipSupported and self.isVoipEnabled and self.isTeamChannelAvailable

    @property
    def isTeamChannelAvailable(self):
        return self.__isTeamChannelAvailable

    @property
    def voipManager(self):
        return VOIP.getVOIPManager()

    def startControl(self, *_):
        _logger.debug('[LS] LSVOIPController started.')
        self.__subscribe()

    def stopControl(self):
        _logger.debug('[LS] LSVOIPController stopped.')
        self.__unsubscribe()
        self.__clearCooldown()

    def arenaLoadCompleted(self):
        self.__tryActivateVOIP()

    def toggleMute(self, isMuted):
        if not self.isTeamVoipEnabled:
            _logger.error('Failed to toggle mic mute for LS team VOIP channel.')
            return
        VOIP.getVOIPManager().setMicMute(isMuted)

    def toggleChannelConnection(self, automatic=False):
        if self.__sessionProvider.isReplayPlaying:
            return
        elif self.__cooldownCallback is not None:
            _logger.info('Failed to toggle LS team VOIP channel. Cooldown is in progress.')
            return
        else:
            arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
            if not self.isTeamChannelAvailable and self.voipManager.isVoiceSupported():
                if self.__isPlayerInSquad():
                    event_dispatcher.toggleVoipChannelEnabled(arenaBonusType)
                return
            elif not self.isTeamVoipEnabled:
                _logger.error('Failed to toggle LS team VOIP channel. Joining is not allowed.')
                return
            _logger.info('toggleChannelConnection')
            if not automatic and self.__isSoloPlayer():
                ls_account_settings.setSettings(AccountSettingsKeys.IS_VOIP_IN_BATTLE_ACTIVATED, not self.voipManager.isCurrentChannelEnabled(), section=AccountSettingsKeys.PERSISTENT_EVENT_KEY)
            event_dispatcher.toggleVoipChannelEnabled(arenaBonusType)
            self.__cooldownCallback = BigWorld.callback(REQUEST_COOLDOWN.SET_VIVOX_PRESENCE + 1.0, self.__clearCooldown)
            return

    def __subscribe(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable += self.__onChannelAvailable

    def __unsubscribe(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable -= self.__onChannelAvailable

    def __onChannelAvailable(self, *_, **__):
        self.__tryActivateVOIP()

    def __tryActivateVOIP(self):
        if not self.isTeamChannelAvailable:
            return
        if self.isVoipSupported and self.voipManager.isChannelAvailable():
            if self.__isSoloPlayer():
                self.__restoreChannelState()
        self.__processInfoMessages()

    def __restoreChannelState(self):
        wasActivePreviously = ls_account_settings.getSettings(AccountSettingsKeys.IS_VOIP_IN_BATTLE_ACTIVATED, section=AccountSettingsKeys.PERSISTENT_EVENT_KEY)
        if wasActivePreviously != self.voipManager.isCurrentChannelEnabled():
            self.toggleChannelConnection(automatic=True)

    def __isSoloPlayer(self):
        return not self.__sessionProvider.getArenaDP().getVehicleInfo().prebattleID

    def __clearCooldown(self):
        if self.__cooldownCallback is not None:
            BigWorld.cancelCallback(self.__cooldownCallback)
            self.__cooldownCallback = None
        return

    def __isPlayerInSquad(self):
        return self.__sessionProvider.getArenaDP().isSquadMan(vID=BigWorld.player().playerVehicleID)

    def __processInfoMessages(self):
        if self.__messageShown:
            return
        arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod <= ARENA_PERIOD.PREBATTLE:
            self.__tryShowInfoMessages()
            self.__messageShown = True

    def __tryShowInfoMessages(self):
        commands = (CommandMapping.CMD_VOICECHAT_ENABLE, CommandMapping.CMD_VOICECHAT_MUTE)
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        resStr = R.strings.messenger.client.dyn(ARENA_BONUS_TYPE_IDS.get(arenaBonusType))
        if not self.isVoipEnabled or not self.isVoipSupported:
            g_messengerEvents.onCustomMessage(ClientActionMessage(msg=backport.text(resStr.withoutVOIP()), type_=ACTION_MESSAGE_TYPE.ERROR))
        if any((getKey(cmd) == Keys.KEY_NONE for cmd in commands)):
            g_messengerEvents.onCustomMessage(ClientActionMessage(msg=backport.text(resStr.specifyVOIP()), type_=ACTION_MESSAGE_TYPE.ERROR))
