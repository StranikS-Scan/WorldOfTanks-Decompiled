# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/RankedVoiceComponent.py
import logging
import typing
import VOIP
from constants import REQUEST_COOLDOWN
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import RankedKeys
from helpers.CallbackDelayer import CallbackDelayer
from script_component.DynamicScriptComponent import DynamicScriptComponent
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager
logger = logging.getLogger(__name__)

class RankedVoiceComponent(DynamicScriptComponent):

    def __init__(self):
        super(RankedVoiceComponent, self).__init__()
        self.__callbackDelayer = CallbackDelayer()

    def onEnterWorld(self, *args):
        super(RankedVoiceComponent, self).onEnterWorld(*args)
        voipManager = VOIP.getVOIPManager()
        voipManager.onJoinedChannel += self.__onJoinedVoipChannel
        voipManager.onLeftChannel += self.__onLeftVoipChannel
        self.__updateVoipConnection()

    def onLeaveWorld(self):
        voipManager = VOIP.getVOIPManager()
        voipManager.onJoinedChannel -= self.__onJoinedVoipChannel
        voipManager.onLeftChannel -= self.__onLeftVoipChannel
        self.__callbackDelayer.clearCallbacks()
        super(RankedVoiceComponent, self).onLeaveWorld()

    def set_teamVivoxChannel(self, prev):
        if self._isAvatarReady:
            self.__invalidateTeamVivoxChannel()

    def _onAvatarReady(self):
        voipManager = VOIP.getVOIPManager()
        voipManager.onJoinedChannel += self.__onJoinedVoipChannel
        voipManager.onLeftChannel += self.__onLeftVoipChannel
        self.__updateVoipConnection()
        self.__invalidateTeamVivoxChannel()

    def __onJoinedVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __onLeftVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __invalidateTeamVivoxChannel(self):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {vID:{RankedKeys.VOIP_CONNECTED: bool(connected)} for vID, connected in self.teamVivoxChannel.iteritems()}
        arena.onGameModeSpecificStats(isStatic=True, stats=gameModeStats)

    def __updateVoipConnection(self):
        voipManager = VOIP.getVOIPManager()
        isJoined = voipManager.isCurrentChannelEnabled()
        wasJoined = self.teamVivoxChannel.get(avatar_getter.getPlayerVehicleID(), False)
        if wasJoined and not isJoined:
            self.__updateVivoxPresence()
            voipManager.enableCurrentChannel(isEnabled=True)

    def __updateVivoxPresence(self):
        isVoipEnabled = VOIP.getVOIPManager().isCurrentChannelEnabled()
        if self.teamVivoxChannel.get(avatar_getter.getPlayerVehicleID(), False) != isVoipEnabled:
            try:
                self.cell.setVivoxPresence(isVoipEnabled)
            except:
                logger.warning('Cell is not ready')

            self.__callbackDelayer.delayCallback(REQUEST_COOLDOWN.SET_VIVOX_PRESENCE + 1.0, self.__updateVivoxPresence)
