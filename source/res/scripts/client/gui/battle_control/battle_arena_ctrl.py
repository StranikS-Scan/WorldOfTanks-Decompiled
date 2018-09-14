# Embedded file name: scripts/client/gui/battle_control/battle_arena_ctrl.py
import weakref
import BigWorld
from account_helpers.settings_core.SettingsCore import g_settingsCore
from constants import FLAG_ACTION
from avatar_helpers import getAvatarDatabaseID
from constants import PREBATTLE_TYPE
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui import game_control
from gui.Scaleform import VoiceChatInterface
from gui.battle_control import avatar_getter, arena_info
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.prb_control.prb_helpers import prbInvitesProperty
from gui.prb_control.settings import PRB_INVITE_STATE
from messenger.storage import storage_getter
from unit_roster_config import SquadRoster
PLAYERS_PANEL_LENGTH = 15

def _getRoster(user):
    roster = 0
    if user.isFriend():
        roster = 1
    elif user.isIgnored():
        roster = 2
    if user.isMuted():
        roster |= 4
    return roster


class EnemyTeamCtx(object):
    __slots__ = ('team', 'labelMaxLength', 'playerVehicleID', 'prebattleID', 'cameraVehicleID', 'denunciationsLeft', 'playerTeamKillSuspected')

    def __init__(self, team, labelMaxLength, playerVehicleID = -1, playerTeamKillSuspected = False, cameraVehicleID = -1, prebattleID = -1):
        super(EnemyTeamCtx, self).__init__()
        self.team = team
        self.labelMaxLength = labelMaxLength
        self.playerVehicleID = playerVehicleID
        self.playerTeamKillSuspected = playerTeamKillSuspected
        self.cameraVehicleID = cameraVehicleID
        self.prebattleID = prebattleID
        self.denunciationsLeft = getattr(BigWorld.player(), 'denunciationsLeft', 0)

    def isPlayerSelected(self, vo):
        return False

    def getSquadIndex(self, vo):
        return vo.squadIndex

    def isSquadMan(self, vo):
        return False

    def isTeamKiller(self, vo):
        return False

    def getAction(self, vo):
        return VehicleActions.getBitMask(vo.events)

    def isPostmortemView(self, vo):
        return vo.vehicleID == self.cameraVehicleID


class PlayerTeamCtx(EnemyTeamCtx):

    def isPlayerSelected(self, vo):
        return vo.vehicleID == self.playerVehicleID

    def getSquadIndex(self, vo):
        squadIndex = vo.squadIndex
        if vo.isSquadMan(prebattleID=self.prebattleID):
            squadIndex = vo.squadIndex + 10
        return squadIndex

    def isSquadMan(self, vo):
        return vo.isSquadMan(prebattleID=self.prebattleID)

    def isTeamKiller(self, vo):
        if self.isPlayerSelected(vo):
            return self.playerTeamKillSuspected or vo.isTeamKiller(playerTeam=self.team)
        return vo.isTeamKiller(playerTeam=self.team)

    def getAction(self, vo):
        return 0


class PostmortemTeamCtx(PlayerTeamCtx):

    def isPostmortemView(self, vo):
        return vo.vehicleID == self.cameraVehicleID


def makeTeamCtx(team, isEnemy, arenaDP, labelMaxLength, cameraVehicleID = -1):
    if isEnemy:
        ctx = EnemyTeamCtx(team, labelMaxLength, cameraVehicleID=cameraVehicleID)
    elif cameraVehicleID > 0:
        ctx = PostmortemTeamCtx(team, labelMaxLength, avatar_getter.getPlayerVehicleID(), arena_info.isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    else:
        ctx = PlayerTeamCtx(team, labelMaxLength, avatar_getter.getPlayerVehicleID(), arena_info.isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    return ctx


class BattleArenaController(arena_info.IArenaController):
    _PANNELS_ALWAYS_UPDATABLE = True

    def __init__(self, battleUI):
        super(BattleArenaController, self).__init__()
        self.__battleUI = weakref.proxy(battleUI)
        self.__battleCtx = None
        self.__panelsUpdatable = True
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified += self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified += self.__onSentInviteListModified
        return

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    @storage_getter('users')
    def usersStorage(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def destroy(self):
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified -= self.__onSentInviteListModified
        self.__battleUI = None
        return

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def setPanelsUpdatable(self, value):
        if self._PANNELS_ALWAYS_UPDATABLE:
            return
        if self.__panelsUpdatable ^ value:
            self.__panelsUpdatable = value
            if self.__panelsUpdatable:
                self.invalidateGUI()

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        for isEnemy in (False, True):
            self.__updateTeamData(isEnemy, arenaDP)

        fragCorrelation = self.__battleUI.fragCorrelation
        playerTeam = arenaDP.getNumberOfTeam()
        fragCorrelation.updateScore(playerTeam)
        if self.__battleUI.isVehicleCountersVisible:
            fragCorrelation.updateTeam(False, playerTeam)
            fragCorrelation.updateTeam(True, arenaDP.getNumberOfTeam(True))

    def invalidateStats(self, arenaDP):
        self.invalidateVehiclesInfo(arenaDP)

    def addVehicleInfo(self, vo, arenaDP):
        self.__updateTeamItem(vo, arenaDP)

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        self.__updateTeamItem(vo, arenaDP)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        self.__updateTeamItem(vo, arenaDP)

    def invalidateVehicleStats(self, flags, vo, arenaDP):
        self.__updateTeamItem(arenaDP.getVehicleInfo(vo.vehicleID), arenaDP)

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        if vo.isTeamKiller():
            self.__battleUI.markersManager.setTeamKiller(vo.vehicleID)
        self.__updateTeamItem(vo, arenaDP)

    def invalidateUsersTags(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

    def invalidateUserTags(self, user):
        vehicleID = self.__battleCtx.getVehIDByAccDBID(user.getID())
        if vehicleID:
            arenaDP = self.__battleCtx.getArenaDP()
            self.__updateTeamItem(arenaDP.getVehicleInfo(vehicleID), arenaDP)

    def invalidateVehicleInteractiveStats(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

    def invalidateGUI(self, playerTeamOnly = False):
        arenaDP = self.__battleCtx.getArenaDP()
        if playerTeamOnly:
            self.__updateTeamData(False, arenaDP, False)
        else:
            for isEnemy in (False, True):
                self.__updateTeamData(isEnemy, arenaDP, False)

    def __updateTeamItem(self, vo, arenaDP):
        updatedTeam = vo.team
        playerTeam = arenaDP.getNumberOfTeam()
        if not playerTeam:
            return
        isEnemy = updatedTeam != playerTeam
        self.__updateTeamData(isEnemy, arenaDP)
        fragCorrelation = self.__battleUI.fragCorrelation
        fragCorrelation.updateScore(playerTeam)
        if self.__battleUI.isVehicleCountersVisible:
            fragCorrelation.updateTeam(isEnemy, updatedTeam)

    def __updateTeamData(self, isEnemy, arenaDP, isFragsUpdate = True):
        team = arenaDP.getNumberOfTeam(isEnemy)
        fragCorrelation = self.__battleUI.fragCorrelation
        if isFragsUpdate:
            fragCorrelation.clear(team)
        regionGetter = self.__battleCtx.getRegionCode
        isSpeaking = VoiceChatInterface.g_instance.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        pNamesList, fragsList, vNamesList = [], [], []
        roamingCtrl = game_control.g_instance.roaming

        def isMenuEnabled(dbID):
            return not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(dbID)

        valuesHashes = []
        ctx = makeTeamCtx(team, isEnemy, arenaDP, int(self.__battleUI.getPlayerNameLength(isEnemy)), self.__battleUI.getCameraVehicleID())
        playerAccountID = getAvatarDatabaseID()
        inviteSendingProhibited = isEnemy or self.prbInvites.getSentInviteCount() >= 100
        if not inviteSendingProhibited:
            inviteSendingProhibited = not self.__isSquadAllowToInvite(arenaDP)
        invitesReceivingProhibited = arenaDP.getVehicleInfo(playerAccountID).player.forbidInBattleInvitations
        for index, (vInfoVO, vStatsVO, viStatsVO) in enumerate(arenaDP.getTeamIterator(isEnemy)):
            if index >= PLAYERS_PANEL_LENGTH:
                LOG_WARNING('Max players in panel are', PLAYERS_PANEL_LENGTH)
                break
            if self.__battleCtx.isObserver(vInfoVO.vehicleID):
                if self.__battleCtx.isPlayerObserver():
                    continue
            elif isFragsUpdate:
                fragCorrelation.addVehicle(team, vInfoVO.vehicleID, vInfoVO.vehicleType.getClassName(), vInfoVO.isAlive())
                if not vInfoVO.isAlive():
                    fragCorrelation.addKilled(team)
            if not self.__panelsUpdatable:
                continue
            playerFullName = self.__battleCtx.getFullPlayerName(vID=vInfoVO.vehicleID, showVehShortName=False)
            if not playerFullName:
                playerFullName = vInfoVO.player.getPlayerLabel()
            valuesHash = self.__makeHash(index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, userGetter, isSpeaking, isMenuEnabled, regionGetter, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited)
            pName, frags, vName = self.__battleUI.getFormattedStrings(vInfoVO, vStatsVO, ctx, playerFullName)
            pNamesList.append(pName)
            fragsList.append(frags)
            vNamesList.append(vName)
            valuesHashes.append(valuesHash)

        if self.__panelsUpdatable:
            self.__battleUI.setTeamValuesData(self.__makeTeamValues(isEnemy, ctx, pNamesList, fragsList, vNamesList, valuesHashes))

    def __makeTeamValues(self, isEnemy, ctx, pNamesList, fragsList, vNamesList, valuesHashes):
        return {'isEnemy': isEnemy,
         'team': 'team%d' % ctx.team,
         'playerID': ctx.playerVehicleID,
         'squadID': ctx.prebattleID,
         'denunciationsLeft': ctx.denunciationsLeft,
         'isColorBlind': g_settingsCore.getSetting('isColorBlind'),
         'knownPlayersCount': None,
         'namesStr': ''.join(pNamesList),
         'fragsStr': ''.join(fragsList),
         'vehiclesStr': ''.join(vNamesList),
         'valuesHashes': valuesHashes}

    def __makeHash(self, index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, userGetter, isSpeaking, isMenuEnabled, regionGetter, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited):
        vehicleID = vInfoVO.vehicleID
        vTypeVO = vInfoVO.vehicleType
        playerVO = vInfoVO.player
        dbID = playerVO.accountDBID
        user = userGetter(dbID)
        if user:
            roster = _getRoster(user)
            isMuted = user.isMuted()
            isIgnored = user.isIgnored()
        else:
            isIgnored = False
            roster = 0
            isMuted = False
        squadIndex = ctx.getSquadIndex(vInfoVO)
        himself = ctx.isPlayerSelected(vInfoVO)
        isInvitesForbidden = inviteSendingProhibited or himself or playerVO.forbidInBattleInvitations or isIgnored
        LOG_DEBUG('!!!', playerVO.getPlayerLabel(), inviteSendingProhibited, himself, playerVO.forbidInBattleInvitations, isIgnored)
        return {'position': index + 1,
         'label': playerFullName,
         'userName': playerVO.getPlayerLabel(),
         'icon': vTypeVO.iconPath,
         'vehicle': vTypeVO.shortName,
         'vehicleState': vInfoVO.vehicleStatus,
         'frags': vStatsVO.frags,
         'squad': squadIndex,
         'clanAbbrev': playerVO.clanAbbrev,
         'speaking': isSpeaking(dbID),
         'uid': dbID,
         'himself': himself,
         'roster': roster,
         'muted': isMuted,
         'vipKilled': 0,
         'VIP': False,
         'teamKiller': ctx.isTeamKiller(vInfoVO),
         'denunciations': ctx.denunciationsLeft,
         'isPostmortemView': ctx.isPostmortemView(vInfoVO),
         'level': vTypeVO.level if g_settingsCore.getSetting('ppShowLevels') else 0,
         'vehAction': ctx.getAction(vInfoVO),
         'team': vInfoVO.team,
         'vehId': vehicleID,
         'isIGR': playerVO.isIGR(),
         'igrType': playerVO.igrType,
         'igrLabel': playerVO.getIGRLabel(),
         'isEnabledInRoaming': isMenuEnabled(dbID),
         'region': regionGetter(dbID),
         'victoryScore': BigWorld.wg_getNiceNumberFormat(viStatsVO.winPoints),
         'flags': BigWorld.wg_getNiceNumberFormat(viStatsVO.flagActions[FLAG_ACTION.CAPTURED]),
         'damage': BigWorld.wg_getNiceNumberFormat(viStatsVO.damageDealt),
         'deaths': BigWorld.wg_getNiceNumberFormat(viStatsVO.deathCount),
         'isPrebattleCreator': playerVO.isPrebattleCreator,
         'dynamicSquad': self.__getDynamicSquadData(dbID, playerAccountID, isInSquad=squadIndex > 0, inviteSendingProhibited=isInvitesForbidden, invitesReceivingProhibited=invitesReceivingProhibited)}

    def __getDynamicSquadData(self, userDBID, currentAccountDBID, isInSquad, inviteSendingProhibited, invitesReceivingProhibited):
        INVITE_DISABLED = 0
        IN_SQUAD = 1
        INVITE_AVAILABLE = 2
        INVITE_SENT = 3
        INVITE_RECEIVED = 4
        INVITE_RECEIVED_FROM_SQUAD = 5
        state = INVITE_AVAILABLE
        if inviteSendingProhibited:
            state = INVITE_DISABLED
        for invite in self.prbInvites.getInvites():
            if invite.type == PREBATTLE_TYPE.SQUAD:
                inviteState = invite.getState()
                if invite.creatorDBID == userDBID and invite.receiverDBID == currentAccountDBID and inviteState == PRB_INVITE_STATE.PENDING and not invitesReceivingProhibited:
                    state = INVITE_RECEIVED
                elif not inviteSendingProhibited and invite.creatorDBID == currentAccountDBID and userDBID == invite.receiverDBID and inviteState == PRB_INVITE_STATE.PENDING:
                    state = INVITE_SENT

        if isInSquad:
            if state == INVITE_RECEIVED:
                state = INVITE_RECEIVED_FROM_SQUAD
            else:
                state = IN_SQUAD
        return state

    def __isSquadAllowToInvite(self, arenaDP):
        allow = True
        avatarVeh = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
        avatarSquadIndex = avatarVeh.squadIndex
        if avatarSquadIndex > 0:
            if avatarVeh.player.isPrebattleCreator:
                allow = not arenaDP.getPrbVehCount(avatarVeh.team, avatarVeh.prebattleID) >= SquadRoster.MAX_SLOTS
            else:
                allow = False
        return allow

    def __onReceivedInviteModified(self, added, changed, deleted):
        self.invalidateGUI(True)

    def __onSentInviteListModified(self, added, changed, deleted):
        self.invalidateGUI(True)
