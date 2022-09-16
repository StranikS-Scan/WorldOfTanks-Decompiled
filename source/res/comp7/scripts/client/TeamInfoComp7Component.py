# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/TeamInfoComp7Component.py
import typing
import VOIP
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import Comp7Keys
from helpers import dependency
from script_component.ScriptComponent import ScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager

class TeamInfoComp7Component(ScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self, *args):
        super(TeamInfoComp7Component, self).onEnterWorld(*args)
        voipManager = VOIP.getVOIPManager()
        voipManager.onJoinedChannel += self.__onJoinedVoipChannel
        voipManager.onLeftChannel += self.__onLeftVoipChannel
        self.__updateVoipConnection()

    def onLeaveWorld(self):
        voipManager = VOIP.getVOIPManager()
        voipManager.onJoinedChannel -= self.__onJoinedVoipChannel
        voipManager.onLeftChannel -= self.__onLeftVoipChannel
        super(TeamInfoComp7Component, self).onLeaveWorld()

    def set_roleSkillLevels(self, prev):
        if self._isAvatarReady:
            self.__invalidateRoleSkillLevels()

    def set_teamVivoxChannel(self, prev):
        if self._isAvatarReady:
            self.__invalidateTeamVivoxChannel()

    def _onAvatarReady(self):
        self.__invalidateRoleSkillLevels()
        self.__invalidateTeamVivoxChannel()

    def __onJoinedVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __onLeftVoipChannel(self, *_, **__):
        self.__updateVivoxPresence()

    def __invalidateRoleSkillLevels(self):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {vID:{Comp7Keys.ROLE_SKILL_LEVEL: level} for vID, level in self.roleSkillLevels.iteritems()}
        arena.onGameModeSpecificStats(isStatic=True, stats=gameModeStats)

    def __invalidateTeamVivoxChannel(self):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {vID:{Comp7Keys.VOIP_CONNECTED: bool(connected)} for vID, connected in self.teamVivoxChannel.iteritems()}
        arena.onGameModeSpecificStats(isStatic=True, stats=gameModeStats)

    def __updateVoipConnection(self):
        voipManager = VOIP.getVOIPManager()
        isJoined = voipManager.isCurrentChannelEnabled()
        wasJoined = self.teamVivoxChannel.get(avatar_getter.getPlayerVehicleID(), False)
        if wasJoined and not isJoined:
            self.__updateVivoxPresence()
            voipManager.enableCurrentChannel(isEnabled=True)

    def __updateVivoxPresence(self):
        voipManager = VOIP.getVOIPManager()
        self.cell.setVivoxPresence(voipManager.isCurrentChannelEnabled())
