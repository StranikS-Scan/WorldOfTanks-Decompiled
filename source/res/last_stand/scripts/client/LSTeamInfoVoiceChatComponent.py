# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSTeamInfoVoiceChatComponent.py
from __future__ import absolute_import
from script_component.DynamicScriptComponent import DynamicScriptComponent
import VOIP
import typing
from helpers.CallbackDelayer import CallbackDelayer
from constants import REQUEST_COOLDOWN
from gui.battle_control import avatar_getter
from last_stand.gui.battle_control.arena_info.arena_vos import LSKeys
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager

class LSTeamInfoVoiceChatComponent(DynamicScriptComponent):

    def __init__(self):
        super(LSTeamInfoVoiceChatComponent, self).__init__()
        self.__callbackDelayer = CallbackDelayer()

    def _onAvatarReady(self):
        super(LSTeamInfoVoiceChatComponent, self)._onAvatarReady()
        voipManager = VOIP.getVOIPManager()
        if voipManager:
            voipManager.onJoinedChannel += self.__onJoinedVoipChannel
            voipManager.onLeftChannel += self.__onLeftVoipChannel
        self.__updateVoipConnection()
        self.__invalidateTeamVivoxChannel()

    def onDestroy(self):
        voipManager = VOIP.getVOIPManager()
        if voipManager:
            voipManager.onJoinedChannel -= self.__onJoinedVoipChannel
            voipManager.onLeftChannel -= self.__onLeftVoipChannel
        self.__callbackDelayer.clearCallbacks()
        super(LSTeamInfoVoiceChatComponent, self).onDestroy()

    def set_teamVivoxChannel(self, prev):
        if self._isAvatarReady:
            self.__invalidateTeamVivoxChannel()

    def __onJoinedVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __onLeftVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __invalidateTeamVivoxChannel(self):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {vID:{LSKeys.VOIP_CONNECTED: bool(connected)} for vID, connected in self.teamVivoxChannel.items()}
        arena.updateGameModeSpecificStats(isStatic=True, stats=gameModeStats)

    def __updateVoipConnection(self):
        voipManager = VOIP.getVOIPManager()
        isJoined = voipManager.isEnabled() and voipManager.isCurrentChannelEnabled()
        wasJoined = self.teamVivoxChannel.get(avatar_getter.getPlayerVehicleID(), False)
        if wasJoined and not isJoined:
            self.__updateVivoxPresence()
            voipManager.enableCurrentChannel(isEnabled=True)

    def __updateVivoxPresence(self):
        voipManager = VOIP.getVOIPManager()
        isVoipEnabled = voipManager.isEnabled() and voipManager.isCurrentChannelEnabled()
        if self.teamVivoxChannel.get(avatar_getter.getPlayerVehicleID(), False) != isVoipEnabled:
            self.cell.setVivoxPresence(isVoipEnabled)
            self.__callbackDelayer.delayCallback(REQUEST_COOLDOWN.SET_VIVOX_PRESENCE + 1.0, self.__updateVivoxPresence)
