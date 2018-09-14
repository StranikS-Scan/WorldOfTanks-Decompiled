# Embedded file name: scripts/client/gui/battle_control/battle_arena_ctrl.py
import weakref
import BigWorld
from account_helpers.settings_core.SettingsCore import g_settingsCore
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui import game_control
from gui.Scaleform import VoiceChatInterface
from gui.battle_control import avatar_getter, arena_info
from gui.battle_control.arena_info.arena_vos import VehicleActions
from messenger.storage import storage_getter
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

    def __init__(self, battleUI):
        super(BattleArenaController, self).__init__()
        self.__battleUI = weakref.proxy(battleUI)
        self.__battleCtx = None
        return

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    @storage_getter('users')
    def usersStorage(self):
        return None

    def destroy(self):
        self.__battleUI = None
        return

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

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

    def invalidateUsersTags(self):
        self.invalidateVehiclesInfo(self.__battleCtx.getArenaDP())

    def invalidateUserTags(self, user):
        vehicleID = self.__battleCtx.getVehIDByAccDBID(user.getID())
        if vehicleID:
            arenaDP = self.__battleCtx.getArenaDP()
            self.__updateTeamItem(arenaDP.getVehicleInfo(vehicleID), arenaDP)

    def invalidateGUI(self, playerTeamOnly = False):
        if playerTeamOnly:
            self.__updateTeamData(False, self.__battleCtx.getArenaDP(), False)
        else:
            arenaDP = self.__battleCtx.getArenaDP()
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
        fragCorrelation.updateFrags(playerTeam)
        if self.__battleUI.isVehicleCountersVisible:
            fragCorrelation.updateTeam(isEnemy, updatedTeam)

    def __updateTeamData(self, isEnemy, arenaDP, isFragsUpdate = True):
        team = arenaDP.getNumberOfTeam(isEnemy)
        fragCorrelation = self.__battleUI.fragCorrelation
        if isFragsUpdate:
            fragCorrelation.clear(team)
        if isEnemy:
            playersPanel = self.__battleUI.rightPlayersPanel
        else:
            playersPanel = self.__battleUI.leftPlayersPanel
        regionGetter = self.__battleCtx.getRegionCode
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
            if self.__battleCtx.isObserver(vInfoVO.vehicleID):
                if self.__battleCtx.isPlayerObserver():
                    continue
            elif isFragsUpdate:
                fragCorrelation.addVehicle(team, vInfoVO.vehicleID, vInfoVO.vehicleType.getClassName(), vInfoVO.isAlive())
                if not vInfoVO.isAlive():
                    fragCorrelation.addKilled(team)
            playerFullName = self.__battleCtx.getFullPlayerName(vID=vInfoVO.vehicleID, showVehShortName=False)
            if not playerFullName:
                playerFullName = vInfoVO.player.getPlayerLabel()
            valuesHash = self.__makeHash(index, playerFullName, vInfoVO, vStatsVO, ctx, userGetter, isSpeaking, isMenuEnabled, regionGetter)
            pName, frags, vName = playersPanel.getFormattedStrings(vInfoVO, vStatsVO, ctx, playerFullName)
            pNamesList.append(pName)
            fragsList.append(frags)
            vNamesList.append(vName)
            valuesHashes.append(valuesHash)

        playersPanel.setTeamValuesData(self.__makeTeamValues(ctx, pNamesList, fragsList, vNamesList, valuesHashes))

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
            roster = _getRoster(user)
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
         'frags': vStatsVO.frags,
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
