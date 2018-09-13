# Embedded file name: scripts/client/gui/battle_control/battle_arena_ctrl.py
import weakref
import BigWorld
from account_helpers.settings_core.SettingsCore import g_settingsCore
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui import game_control
from gui.BattleContext import g_battleContext
from gui.Scaleform import VoiceChatInterface
from gui.arena_info import IArenaController, getPlayerVehicleID, isPlayerTeamKillSuspected, isEventBattle
from gui.arena_info.arena_vos import VehicleActions
from messenger.storage import storage_getter
PLAYERS_PANEL_LENGTH = 15

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
        return False


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
        ctx = EnemyTeamCtx(team, labelMaxLength)
    elif cameraVehicleID > 0:
        ctx = PostmortemTeamCtx(team, labelMaxLength, getPlayerVehicleID(), isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    else:
        ctx = PlayerTeamCtx(team, labelMaxLength, getPlayerVehicleID(), isPlayerTeamKillSuspected(), cameraVehicleID, arenaDP.getVehicleInfo().prebattleID)
    return ctx


class BattleArenaController(IArenaController):

    def __init__(self, battleUI):
        super(BattleArenaController, self).__init__()
        self.__battleUI = weakref.proxy(battleUI)

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    @storage_getter('users')
    def usersStorage(self):
        return None

    def destroy(self):
        self.__battleUI = None
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(g_battleContext.arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        for isEnemy in (False, True):
            self.__updateTeamData(isEnemy, arenaDP)

        fragCorrelation = self.__battleUI.fragCorrelation
        playerTeam = arenaDP.getNumberOfTeam()
        fragCorrelation.updateFrags(playerTeam)
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
            self.__battleUI.vMarkersManager.setTeamKiller(vo.vehicleID)
        self.__updateTeamItem(vo, arenaDP)

    def invalidateChatRosters(self):
        self.invalidateVehiclesInfo(g_battleContext.arenaDP)

    def invalidateChatRoster(self, user):
        arenaDP = g_battleContext.arenaDP
        vehicleID = arenaDP.getVehIDByAccDBID(user.getID())
        if vehicleID:
            self.__updateTeamItem(arenaDP.getVehicleInfo(vehicleID), arenaDP)

    def invalidateGUI(self, playerTeamOnly = False):
        if playerTeamOnly:
            self.__updateTeamData(False, g_battleContext.arenaDP, False)
        else:
            for isEnemy in (False, True):
                self.__updateTeamData(isEnemy, g_battleContext.arenaDP, False)

    def __updateTeamItem(self, vo, arenaDP):
        updatedTeam = vo.team
        playerTeam = arenaDP.getNumberOfTeam()
        if not playerTeam:
            return
        isEnemy = updatedTeam != playerTeam
        self.__updateTeamData(isEnemy, arenaDP)
        fragCorrelation = self.__battleUI.fragCorrelation
        fragCorrelation.updateFrags(playerTeam)
        if self.__battleUI.isVehicleCountersVisible:
            fragCorrelation.updateTeam(isEnemy, updatedTeam)

    def __updateTeamData(self, isEnemy, arenaDP, isFragsUpdate = True):
        team = arenaDP.getNumberOfTeam(isEnemy)
        oppositeTeam = arenaDP.getNumberOfTeam(not isEnemy)
        fragCorrelation = self.__battleUI.fragCorrelation
        if isFragsUpdate:
            fragCorrelation.clear(team if not isEventBattle() else oppositeTeam)
        if isEnemy:
            playersPanel = self.__battleUI.rightPlayersPanel
        else:
            playersPanel = self.__battleUI.leftPlayersPanel
        regionGetter = g_battleContext.getRegionCode
        isSpeaking = VoiceChatInterface.g_instance.isPlayerSpeaking
        userGetter = self.usersStorage.getUser
        pNamesList, fragsList, vNamesList = [], [], []
        roamingCtrl = game_control.g_instance.roaming

        def isMenuEnabled(dbID):
            return not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(dbID)

        valuesHashes = []
        ctx = makeTeamCtx(team, isEnemy, arenaDP, int(playersPanel.getPlayerNameLength()), self.__battleUI.getCameraVehicleID())
        for index, (vInfoVO, vStatsVO) in enumerate(arenaDP.getTeamIterator(isEnemy)):
            if index >= PLAYERS_PANEL_LENGTH:
                LOG_WARNING('Max players in panel are', PLAYERS_PANEL_LENGTH)
                break
            if g_battleContext.isObserver(vInfoVO.vehicleID):
                if g_battleContext.isPlayerObserver():
                    continue
            elif isFragsUpdate:
                fragCorrelation.addVehicle(team, vInfoVO.vehicleID, vInfoVO.vehicleType.getClassName(), vInfoVO.isAlive())
                if isEventBattle():
                    fragCorrelation.addFrags(team, count=vStatsVO.frags)
                elif not vInfoVO.isAlive():
                    fragCorrelation.addKilled(team)
            playerFullName = g_battleContext.getFullPlayerName(vID=vInfoVO.vehicleID, showVehShortName=False)
            if not playerFullName:
                playerFullName = vInfoVO.player.getPlayerLabel()
            valuesHash = self.__makeHash(index, playerFullName, vInfoVO, vStatsVO, ctx, userGetter, isSpeaking, isMenuEnabled, regionGetter)
            pName, frags, vName = playersPanel.getFormattedStrings(vInfoVO, vStatsVO, ctx, playerFullName)
            pNamesList.append(pName)
            fragsList.append(frags)
            vNamesList.append(vName)
            valuesHashes.append(valuesHash)

        playersPanel.setTeamValuesData(self.__makeTeamValues(ctx, pNamesList, fragsList, vNamesList, valuesHashes))
        fragCorrelation.playGoalSound()

    def __makeTeamValues(self, ctx, pNamesList, fragsList, vNamesList, valuesHashes):
        return {'team': 'team%d' % ctx.team,
         'playerID': ctx.playerVehicleID,
         'squadID': ctx.prebattleID,
         'denunciationsLeft': ctx.denunciationsLeft,
         'isColorBlind': g_settingsCore.getSetting('isColorBlind'),
         'knownPlayersCount': None,
         'namesStr': ''.join(pNamesList),
         'fragsStr': ''.join(fragsList),
         'vehiclesStr': ''.join(vNamesList),
         'valuesHashes': valuesHashes}

    def __makeHash(self, index, playerFullName, vInfoVO, vStatsVO, ctx, userGetter, isSpeaking, isMenuEnabled, regionGetter):
        vehicleID = vInfoVO.vehicleID
        vTypeVO = vInfoVO.vehicleType
        playerVO = vInfoVO.player
        dbID = playerVO.accountDBID
        user = userGetter(dbID)
        if user:
            roster = user.getRoster()
            isMuted = user.isMuted()
        else:
            roster = 0
            isMuted = False
        return {'position': index + 1,
         'label': playerFullName,
         'userName': playerVO.getPlayerLabel(),
         'icon': vTypeVO.iconPath,
         'vehicle': vTypeVO.shortName,
         'vehicleState': vInfoVO.vehicleStatus,
         'frags': vStatsVO.frags if not isEventBattle() else 0,
         'squad': ctx.getSquadIndex(vInfoVO),
         'clanAbbrev': playerVO.clanAbbrev,
         'speaking': isSpeaking(dbID),
         'uid': dbID,
         'himself': ctx.isPlayerSelected(vInfoVO),
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
         'region': regionGetter(dbID)}
