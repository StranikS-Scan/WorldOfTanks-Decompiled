# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/team_overrides.py
from account_helpers.settings_core.settings_constants import SOUND
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info import settings
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_DELIVERY_STATUS = settings.INVITATION_DELIVERY_STATUS
_P_STATUS = settings.PLAYER_STATUS

class DefaultTeamOverrides(object):
    __slots__ = ('team', 'personal', 'isReplayPlaying')
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, team, personal, isReplayPlaying=False):
        super(DefaultTeamOverrides, self).__init__()
        self.team = team
        self.personal = personal
        self.isReplayPlaying = isReplayPlaying

    def isPlayerSelected(self, vo):
        return False

    def isPersonalSquad(self, vo):
        return False

    def isTeamKiller(self, vo):
        return False

    def getAction(self, vo):
        return VehicleActions.getBitMask(vo.events)

    def getPlayerStatus(self, vo):
        playerStatus = _P_STATUS.DEFAULT
        if vo.isActionsDisabled() or self.isReplayPlaying:
            playerStatus |= _P_STATUS.IS_ACTION_DISABLED
        if vo.isSquadMan():
            playerStatus |= _P_STATUS.IS_SQUAD_MAN
            if self.isPersonalSquad(vo):
                playerStatus |= _P_STATUS.IS_SQUAD_PERSONAL
        if self.isTeamKiller(vo):
            playerStatus |= _P_STATUS.IS_TEAM_KILLER
        if self.isPlayerSelected(vo) and not self.personal.isOtherSelected() or self.isPostmortemView(vo):
            playerStatus |= _P_STATUS.IS_PLAYER_SELECTED
        return playerStatus

    def isPostmortemView(self, vo):
        return vo.vehicleID == self.personal.selectedID

    def getInvitationDeliveryStatus(self, vo):
        return _DELIVERY_STATUS.FORBIDDEN_BY_RECEIVER

    def getColorScheme(self):
        pass

    def clear(self):
        self.personal = None
        return


class PlayerTeamOverrides(DefaultTeamOverrides):
    __slots__ = ('__isVoipSupported',)

    def __init__(self, team, personal, isVoipSupported=False, isReplayPlaying=False):
        super(PlayerTeamOverrides, self).__init__(team, personal, isReplayPlaying)
        self.__isVoipSupported = isVoipSupported

    def isPlayerSelected(self, vo):
        return vo.vehicleID == self.personal.vehicleID

    def isPersonalSquad(self, vo):
        return vo.isSquadMan(prebattleID=self.personal.prebattleID)

    def isTeamKiller(self, vo):
        return self.personal.teamKillSuspected or vo.isTeamKiller(playerTeam=self.team) if self.isPlayerSelected(vo) else vo.isTeamKiller(playerTeam=self.team)

    def getAction(self, vo):
        pass

    def getPlayerStatus(self, vo):
        status = super(PlayerTeamOverrides, self).getPlayerStatus(vo)
        if self.personal.vehicleID == vo.vehicleID and vo.isSquadMan() and self.__isVoipSupported and not self.settingsCore.getSetting(SOUND.VOIP_ENABLE) and not self.isReplayPlaying:
            status |= _P_STATUS.IS_VOIP_DISABLED
        return status

    def getInvitationDeliveryStatus(self, vo):
        return vo.invitationDeliveryStatus

    def getColorScheme(self):
        pass


class PersonalInfo(object):
    __slots__ = ('vehicleID', 'selectedID', 'prebattleID', 'teamKillSuspected')

    def __init__(self):
        super(PersonalInfo, self).__init__()
        self.vehicleID = avatar_getter.getPlayerVehicleID()
        self.selectedID = self.vehicleID
        self.prebattleID = 0
        self.teamKillSuspected = avatar_getter.isPlayerTeamKillSuspected()

    def changeSelected(self, selectedID):
        previousID, self.selectedID = self.selectedID, selectedID
        return previousID

    def isOtherSelected(self):
        return self.vehicleID != self.selectedID


def makeOverrides(isEnemy, team, personal, arenaVisitor, isReplayPlaying=False):
    if isEnemy:
        ctx = DefaultTeamOverrides(team, personal, isReplayPlaying=isReplayPlaying)
    else:
        ctx = PlayerTeamOverrides(team, personal, isVoipSupported=arenaVisitor.gui.isRandomBattle(), isReplayPlaying=isReplayPlaying)
    return ctx
