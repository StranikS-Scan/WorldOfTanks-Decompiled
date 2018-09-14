# Embedded file name: scripts/client/gui/battle_control/battle_arena_ctrl.py
from collections import defaultdict
import weakref
import BattleReplay
import BigWorld
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import SOUND
from avatar_helpers import getAvatarDatabaseID
from constants import PREBATTLE_TYPE, IS_CHINA
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.Scaleform import VoiceChatInterface
from gui.battle_control import avatar_getter, arena_info
from gui.battle_control.arena_info.arena_vos import VehicleActions, _VEHICLE_STATUS
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.avatar_getter import getArenaUniqueID
from gui.battle_control.battle_constants import MULTIPLE_TEAMS_TYPE
from gui.prb_control.prb_helpers import prbInvitesProperty
from messenger.storage import storage_getter
from unit_roster_config import SquadRoster
from gui.LobbyContext import g_lobbyContext
from gui.battle_control.arena_info import hasResourcePoints, isRandomBattle
PLAYERS_PANEL_LENGTH = 24

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
    __slots__ = ('team', 'playerLabelMaxLength', 'vehicleLabelMaxLength', 'playerVehicleID', 'prebattleID', 'cameraVehicleID', 'denunciationsLeft', 'playerTeamKillSuspected')

    def __init__(self, team, playerLabelMaxLength, vehicleLabelMaxLength, playerVehicleID = -1, playerTeamKillSuspected = False, cameraVehicleID = -1, prebattleID = -1):
        super(EnemyTeamCtx, self).__init__()
        self.team = team
        self.playerLabelMaxLength = playerLabelMaxLength
        self.vehicleLabelMaxLength = vehicleLabelMaxLength
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


def makeTeamCtx(team, isEnemy, arenaDP, playerLabelMaxLength, vehicleLabelMaxLength, cameraVehicleID = -1):
    if isEnemy:
        ctx = EnemyTeamCtx(team, playerLabelMaxLength, vehicleLabelMaxLength, cameraVehicleID=cameraVehicleID)
    elif cameraVehicleID > 0:
        ctx = PostmortemTeamCtx(team, playerLabelMaxLength, vehicleLabelMaxLength, avatar_getter.getPlayerVehicleID(), arena_info.isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    else:
        ctx = PlayerTeamCtx(team, playerLabelMaxLength, vehicleLabelMaxLength, avatar_getter.getPlayerVehicleID(), arena_info.isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    return ctx


class BattleArenaController(IArenaVehiclesController):

    def __init__(self, battleUI):
        super(BattleArenaController, self).__init__()
        self._battleUI = weakref.proxy(battleUI)
        self._battleCtx = None
        self._regionGetter = lambda dbID: None
        self._isSpeaking = VoiceChatInterface.g_instance.isPlayerSpeaking
        self._userGetter = self.usersStorage.getUser
        roaming = g_lobbyContext.getServerSettings().roaming

        def isMenuEnabled(dbID):
            return not roaming.isInRoaming() and not roaming.isPlayerInRoaming(dbID)

        self._isMenuEnabled = isMenuEnabled
        self._isReplayPlaying = BattleReplay.g_replayCtrl.isPlaying
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

    def clear(self):
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified -= self.__onSentInviteListModified
        self._battleUI = None
        self._regionGetter = None
        self._isSpeaking = None
        self._userGetter = None
        self._isMenuEnabled = None
        return

    def setBattleCtx(self, battleCtx):
        self._battleCtx = battleCtx
        if self._battleCtx is not None:
            self._regionGetter = self._battleCtx.getRegionCode
        else:
            self._regionGetter = None
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self._battleCtx.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        for isEnemy, teamIdx in arenaDP.getTeamIDsIterator():
            self._updateTeamData(isEnemy, teamIdx, arenaDP)

        fragCorrelation = self._battleUI.fragCorrelation
        fragCorrelation.updateScore()
        if self._battleUI.isVehicleCountersVisible:
            for isEnemy, teamIdx in arenaDP.getTeamIDsIterator():
                fragCorrelation.updateTeam(isEnemy, teamIdx)

    def invalidateStats(self, arenaDP):
        self.invalidateVehiclesInfo(arenaDP)

    def addVehicleInfo(self, vo, arenaDP):
        self._updateTeamItem(vo, arenaDP)

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        self._updateTeamItem(vo, arenaDP)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        self._updateTeamItem(vo, arenaDP)

    def invalidateVehicleStats(self, flags, vo, arenaDP):
        self._updateTeamItem(arenaDP.getVehicleInfo(vo.vehicleID), arenaDP)

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        if vo.isTeamKiller():
            self._battleUI.markersManager.setTeamKiller(vo.vehicleID)
        self._updateTeamItem(vo, arenaDP)

    def invalidateUsersTags(self):
        self.invalidateVehiclesInfo(self._battleCtx.getArenaDP())

    def invalidateUserTags(self, user):
        vehicleID = self._battleCtx.getVehIDByAccDBID(user.getID())
        if vehicleID:
            arenaDP = self._battleCtx.getArenaDP()
            self._updateTeamItem(arenaDP.getVehicleInfo(vehicleID), arenaDP)

    def invalidateVehicleInteractiveStats(self):
        self.invalidateVehiclesInfo(self._battleCtx.getArenaDP())

    def invalidateGUI(self, playerTeamOnly = False):
        arenaDP = self._battleCtx.getArenaDP()
        if playerTeamOnly:
            self._updateTeamData(False, arenaDP.getNumberOfTeam(), arenaDP, False)
        else:
            for isEnemy, teamIdx in arenaDP.getTeamIDsIterator():
                self._updateTeamData(isEnemy, teamIdx, arenaDP, False)

    def _updateTeamItem(self, vo, arenaDP):
        updatedTeam = vo.team
        playerTeam = arenaDP.getNumberOfTeam()
        if not playerTeam:
            return
        isEnemy = arenaDP.isEnemyTeam(updatedTeam)
        self._updateTeamData(isEnemy, updatedTeam, arenaDP)
        fragCorrelation = self._battleUI.fragCorrelation
        fragCorrelation.updateScore()
        if self._battleUI.isVehicleCountersVisible:
            fragCorrelation.updateTeam(isEnemy, updatedTeam)

    def _updateTeamData(self, isEnemy, team, arenaDP, isFragsUpdate = True):
        pNamesList, fragsList, vNamesList, additionalDataList = ([],
         [],
         [],
         [])
        valuesHashes = []
        ctx = makeTeamCtx(team, isEnemy, arenaDP, int(self._battleUI.getPlayerNameLength(isEnemy)), int(self._battleUI.getVehicleNameLength(isEnemy)), self._battleUI.getCameraVehicleID())
        if isFragsUpdate:
            fragCorrelation = self._battleUI.fragCorrelation
            fragCorrelation.clear(team)
            for index, (vInfoVO, vStatsVO, viStatsVO) in enumerate(arenaDP.getTeamIterator(team)):
                if not self._battleCtx.isObserver(vInfoVO.vehicleID):
                    fragCorrelation.addVehicle(team, vInfoVO.vehicleID, vInfoVO.vehicleType.getClassName(), vInfoVO.isAlive())
                    if not vInfoVO.isAlive():
                        fragCorrelation.addKilled(team)

        playerAccountID = getAvatarDatabaseID()
        inviteSendingProhibited = isEnemy or self.prbInvites.getSentInviteCount() >= 100
        if not inviteSendingProhibited:
            inviteSendingProhibited = not self._isSquadAllowToInvite(arenaDP)
        invitesReceivingProhibited = arenaDP.getVehicleInfo(playerAccountID).player.forbidInBattleInvitations
        for index, (vInfoVO, vStatsVO, viStatsVO) in enumerate(arenaDP.getVehiclesIterator(isEnemy)):
            if index >= PLAYERS_PANEL_LENGTH:
                LOG_WARNING('Max players in panel are', PLAYERS_PANEL_LENGTH)
                break
            if self._battleCtx.isObserver(vInfoVO.vehicleID) and self._battleCtx.isPlayerObserver():
                continue
            playerFullName = self._battleCtx.getFullPlayerName(vID=vInfoVO.vehicleID, showVehShortName=False)
            if not playerFullName:
                playerFullName = vInfoVO.player.getPlayerLabel()
            valuesHash = self._makeHash(index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited, isEnemy)
            pName, frags, vName, additionalData = self._battleUI.statsForm.getFormattedStrings(vInfoVO, vStatsVO, viStatsVO, ctx, playerFullName)
            pNamesList.append(pName)
            fragsList.append(frags)
            vNamesList.append(vName)
            additionalDataList.append(additionalData)
            valuesHashes.append(valuesHash)

        self._battleUI.setTeamValuesData(self._makeTeamValues(isEnemy, ctx, pNamesList, fragsList, vNamesList, additionalDataList, valuesHashes))

    def _makeTeamValues(self, isEnemy, ctx, pNamesList, fragsList, vNamesList, additionalDatas, valuesHashes):
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

    def _makeHash(self, index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited, isEnemy):
        vehicleID = vInfoVO.vehicleID
        vTypeVO = vInfoVO.vehicleType
        playerVO = vInfoVO.player
        dbID = playerVO.accountDBID
        user = self._userGetter(dbID)
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
        isActionsDisabled = vInfoVO.isActionsDisabled()
        isInvitesForbidden = inviteSendingProhibited or himself or playerVO.forbidInBattleInvitations or isIgnored or isActionsDisabled
        isPlayerInSquad = playerAccountID == dbID and vInfoVO.isSquadMan()
        squadNoSound = False
        if isPlayerInSquad and isRandomBattle() and not IS_CHINA:
            squadNoSound = not g_settingsCore.getSetting(SOUND.VOIP_ENABLE)
        return {'position': index + 1,
         'label': playerFullName,
         'userName': playerVO.getPlayerLabel(),
         'icon': vTypeVO.iconPath,
         'vehicle': vTypeVO.shortName,
         'vehicleState': vInfoVO.vehicleStatus,
         'frags': vStatsVO.frags,
         'squad': squadIndex,
         'clanAbbrev': playerVO.clanAbbrev,
         'speaking': self._isSpeaking(dbID),
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
         'isEnabledInRoaming': self._isMenuEnabled(dbID),
         'region': self._regionGetter(dbID),
         'isPrebattleCreator': playerVO.isPrebattleCreator,
         'dynamicSquad': self._getDynamicSquadData(dbID, playerAccountID, isInSquad=squadIndex > 0, inviteSendingProhibited=isInvitesForbidden, invitesReceivingProhibited=invitesReceivingProhibited),
         'vehicleType': vTypeVO.getClassName(),
         'teamColorScheme': 'vm_enemy' if isEnemy else 'vm_ally',
         'vLevel': vTypeVO.level,
         'contextMenuDisabled': isActionsDisabled or self._isReplayPlaying,
         'squadNoSound': squadNoSound}

    def _getDynamicSquadData(self, userDBID, currentAccountDBID, isInSquad, inviteSendingProhibited, invitesReceivingProhibited):
        INVITE_DISABLED = 0
        IN_SQUAD = 1
        INVITE_AVAILABLE = 2
        INVITE_SENT = 3
        INVITE_RECEIVED = 4
        INVITE_RECEIVED_FROM_SQUAD = 5
        state = INVITE_AVAILABLE
        if inviteSendingProhibited:
            state = INVITE_DISABLED
        arenaUniqueID = getArenaUniqueID()
        for invite in self.prbInvites.getInvites():
            if invite.type == PREBATTLE_TYPE.SQUAD and invite.isActive() and invite.isSameBattle(arenaUniqueID):
                if invite.creatorDBID == userDBID and invite.receiverDBID == currentAccountDBID and not invitesReceivingProhibited:
                    state = INVITE_RECEIVED
                elif not inviteSendingProhibited and invite.creatorDBID == currentAccountDBID and userDBID == invite.receiverDBID:
                    state = INVITE_SENT

        if isInSquad:
            if state == INVITE_RECEIVED:
                state = INVITE_RECEIVED_FROM_SQUAD
            else:
                state = IN_SQUAD
        return state

    def _isSquadAllowToInvite(self, arenaDP):
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


class FalloutBattleArenaController(BattleArenaController):

    def _makeTeamValues(self, isEnemy, ctx, pNamesList, fragsList, vNamesList, additionalDatas, valuesHashes):
        result = super(FalloutBattleArenaController, self)._makeTeamValues(isEnemy, ctx, pNamesList, fragsList, vNamesList, additionalDatas, valuesHashes)
        specialPointsStr = ''
        damageStr = ''
        deathsStr = ''
        scoreStr = ''
        for scoreString, damageString, deathsString, specialPointsString in additionalDatas:
            scoreStr += scoreString
            deathsStr += deathsString
            damageStr += damageString
            specialPointsStr += specialPointsString

        if hasResourcePoints():
            battleType = 'resources'
        else:
            battleType = 'flags'
        result.update({'specialPointsStr': specialPointsStr,
         'damageStr': damageStr,
         'deathsStr': deathsStr,
         'scoreStr': scoreStr,
         'battleType': battleType})
        return result

    def _makeHash(self, index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited, isEnemy):
        result = super(FalloutBattleArenaController, self)._makeHash(index, playerFullName, vInfoVO, vStatsVO, viStatsVO, ctx, playerAccountID, inviteSendingProhibited, invitesReceivingProhibited, isEnemy)
        state = result['vehicleState'] & (_VEHICLE_STATUS.IS_READY | _VEHICLE_STATUS.NOT_AVAILABLE)
        if not viStatsVO.stopRespawn:
            state |= _VEHICLE_STATUS.IS_ALIVE
        result['vehicleState'] = state
        result['isPostmortemView'] = result['himself']
        return result


class MultiteamBattleArenaController(BattleArenaController):

    def _updateTeamData(self, isEnemy, team, arenaDP, isFragsUpdate = True):
        pNamesList, fragsList, vNamesList, additionalDataList = ([],
         [],
         [],
         [])
        valuesHashes = []
        teamsList, teamScoreList = [], []
        playerIdx = -1
        playerTeamID = avatar_getter.getPlayerTeam()
        teamScores = defaultdict(list)
        teamIds = arenaDP.getMultiTeamsIndexes()
        camraVehicleID = self._battleUI.getCameraVehicleID()
        playerNameLength = int(self._battleUI.getPlayerNameLength(isEnemy))
        vehicleNameLength = int(self._battleUI.getVehicleNameLength(isEnemy))
        for index, (vInfoVO, vStatsVO, viStatsVO) in enumerate(arenaDP.getAllVehiclesIteratorByTeamScore()):
            team = vInfoVO.team
            isEnemy = arenaDP.isEnemyTeam(team)
            ctx = makeTeamCtx(team, isEnemy, arenaDP, playerNameLength, vehicleNameLength, camraVehicleID)
            if ctx.playerVehicleID == vInfoVO.vehicleID:
                playerIdx = index
            playerFullName = self._battleCtx.getFullPlayerName(vID=vInfoVO.vehicleID, showVehShortName=False)
            if not playerFullName:
                playerFullName = vInfoVO.player.getPlayerLabel()
            pName, frags, vName, additionalData = self._battleUI.statsForm.getFormattedStrings(vInfoVO, vStatsVO, viStatsVO, ctx, playerFullName)
            pNamesList.append(pName)
            fragsList.append(frags)
            vNamesList.append(vName)
            additionalDataList.append(additionalData)
            valuesHashes.append({'vehicleState': 0 if viStatsVO.stopRespawn else _VEHICLE_STATUS.IS_ALIVE})
            teamIdx = teamIds[team]
            if (team, teamIdx) not in teamsList:
                teamsList.append((team, teamIdx))
            format = self._battleUI.statsForm.getTeamScoreFormat()
            teamScores[team].append((viStatsVO.winPoints, format))

        for team, _ in teamsList:
            teamScore = teamScores[team]
            totalScore = sum([ score for score, _ in teamScore ])
            scoreIndexForTable = len(teamScore) / 2
            for index, (score, format) in enumerate(teamScore):
                teamScoreStr = format % ' '
                if index == scoreIndexForTable:
                    teamScoreStr = format % BigWorld.wg_getNiceNumberFormat(totalScore)
                teamScoreList.append(teamScoreStr)

        self._battleUI.setMultiteamValues(self._makeMultiTeamValues(playerTeamID, playerIdx, pNamesList, fragsList, vNamesList, teamsList, teamScoreList, additionalDataList, valuesHashes, arenaDP.getMultiTeamsType()))

    def _makeMultiTeamValues(self, playerTeamID, playerIdx, pNamesList, fragsList, vNamesList, teamsList, teamScoreList, additionalDataList, valuesHashes, multiteamType):
        flagsStr = ''
        damageStr = ''
        deathsStr = ''
        scoreStr = ''
        for scoreString, damageString, deathsString, flagsString in additionalDataList:
            scoreStr += scoreString
            deathsStr += deathsString
            damageStr += damageString
            flagsStr += flagsString

        return {'namesStr': ''.join(pNamesList),
         'vehiclesStr': ''.join(vNamesList),
         'playerIndex': playerIdx,
         'multiteamType': multiteamType,
         'fragsStr': ''.join(fragsList),
         'teamScoreStr': ''.join(teamScoreList),
         'scoreStr': scoreStr,
         'flagsStr': flagsStr,
         'damageStr': damageStr,
         'deathsStr': deathsStr,
         'multiteams': self.__getMultiteamValues(teamsList, playerTeamID, multiteamType),
         'valuesHashes': valuesHashes}

    def __getMultiteamValues(self, teamsList, playerTeamID, multiteamType):
        if multiteamType == MULTIPLE_TEAMS_TYPE.FFA:
            return []

        def __pack(teamData):
            teamID, teamIdx = teamData
            return {'squadId': teamIdx,
             'isPlayerTeam': playerTeamID == teamID}

        return map(__pack, teamsList)


def battleArenaControllerFactory(battleUI, isEventBattle = False, isMutlipleTeams = False):
    if isEventBattle:
        if isMutlipleTeams:
            return MultiteamBattleArenaController(battleUI)
        return FalloutBattleArenaController(battleUI)
    return BattleArenaController(battleUI)
