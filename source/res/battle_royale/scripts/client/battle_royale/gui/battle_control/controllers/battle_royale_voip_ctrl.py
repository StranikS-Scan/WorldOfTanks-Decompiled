# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/battle_royale_voip_ctrl.py
import logging
import typing
import VOIP
import CommandMapping
from account_helpers.settings_core.settings_constants import SOUND
from constants import IS_CHINA, ARENA_BONUS_TYPE
from gui import g_keyEventHandlers
from gui.battle_control import event_dispatcher
from gui.battle_control.arena_info.interfaces import IBRVOIPController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.utils.key_mapping import getKey
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager
_logger = logging.getLogger(__name__)

class BRVOIPController(IBRVOIPController):
    __slots__ = ()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    @property
    def isVoipSupported(self):
        return not IS_CHINA and self.__VOIPManager.isVoiceSupported()

    @property
    def isVoipEnabled(self):
        return self.__VOIPManager.isEnabled()

    @property
    def isJoined(self):
        return self.__VOIPManager.isCurrentChannelEnabled()

    @property
    def isTeamVoipEnabled(self):
        return self.isVoipSupported and self.isVoipEnabled

    @property
    def __VOIPManager(self):
        return VOIP.getVOIPManager()

    def startControl(self, *_, **__):
        _logger.debug('BR VOIPController started.')
        self.__subscribe()

    def stopControl(self):
        _logger.debug('BR VOIPController stopped.')
        self.__unsubscribe()

    def getControllerID(self):
        return BATTLE_CTRL_ID.BR_VOIP_CTRL

    def arenaLoadCompleted(self):
        self.__tryActivateVOIP()

    def toggleChannelConnection(self):
        if self.__sessionProvider.isReplayPlaying:
            return
        if not self.isTeamVoipEnabled:
            _logger.error('Failed to toggle team VOIP channel. Joining is not allowed.')
            return
        _logger.info('toggleChannelConnection')
        event_dispatcher.toggleVoipChannelEnabled(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)

    def __subscribe(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable += self.__onChannelAvailable
        g_keyEventHandlers.add(self.__handleKeyEvent)

    def __unsubscribe(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable -= self.__onChannelAvailable
        g_keyEventHandlers.discard(self.__handleKeyEvent)

    def __onChannelAvailable(self, *_, **__):
        self.__tryActivateVOIP()

    def __tryActivateVOIP(self):
        if self.isVoipSupported and self.__VOIPManager.isChannelAvailable():
            if self.__isSoloPlayer():
                self.__restoreChannelState()

    def __restoreChannelState(self):
        wasActivePreviously = self.__settingsCore.getSetting(SOUND.VOIP_ENABLE)
        if wasActivePreviously != self.__VOIPManager.isCurrentChannelEnabled():
            self.toggleChannelConnection()

    def __isSoloPlayer(self):
        return not self.__sessionProvider.getArenaDP().getVehicleInfo().prebattleID

    def __handleKeyEvent(self, event):
        if not (self.isTeamVoipEnabled and self.__VOIPManager.isChannelAvailable()):
            return
        if event.key == getKey(CommandMapping.CMD_VOICECHAT_ENABLE):
            if event.isKeyDown() and not event.isRepeatedEvent():
                self.toggleChannelConnection()
