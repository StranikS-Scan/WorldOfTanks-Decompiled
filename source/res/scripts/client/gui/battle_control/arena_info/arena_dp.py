# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_dp.py
import logging
import operator
from constants import TEAMS_IN_ARENA, PLAYER_RANK
from shared_utils import first
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import arena_descrs
from gui.battle_control.arena_info import arena_vos
from gui.battle_control.arena_info import settings
from gui.battle_control.arena_info import squad_finder
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS
from gui.battle_control.battle_constants import MULTIPLE_TEAMS_TYPE
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_session import IArenaDataProvider
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_OP = settings.INVALIDATE_OP
_INVITATION_STATUS = settings.INVITATION_DELIVERY_STATUS

class ArenaDataProvider(IArenaDataProvider):
    __slots__ = ('__playerTeam', '__playerVehicleID', '__vInfoVOs', '__vStatsVOs', '__avatarsVIDs', '__accountVIDs', '__weakref__', '__teamsOnArena', '__squadFinder', '__description', '__invitationStatuses')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, setup):
        super(ArenaDataProvider, self).__init__()
        self.__playerTeam = avatar_getter.getPlayerTeam(avatar=setup.avatar)
        self.__teamsOnArena = setup.arenaVisitor.type.getTeamsOnArenaRange()
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID(setup.avatar)
        self.__vInfoVOs = {}
        self.__vStatsVOs = arena_vos.VehicleArenaStatsDict()
        self.__avatarsVIDs = {}
        self.__accountVIDs = {}
        self.__invitationStatuses = {}
        self.__squadFinder = squad_finder.createSquadFinder(setup.arenaVisitor)
        self.__description = arena_descrs.createDescription(setup.arenaVisitor)

    def __del__(self):
        _logger.debug('Deleted: %r', self)

    def clearInfo(self):
        self.__vInfoVOs.clear()
        self.__avatarsVIDs.clear()
        self.__accountVIDs.clear()
        self.__squadFinder.clear()

    def clearStats(self):
        self.__vStatsVOs.clear()

    def clear(self):
        self.clearInfo()
        self.clearStats()
        self.__description.clear()
        self.__invitationStatuses.clear()

    def defaultInfo(self):
        self.clearInfo()

    def buildVehiclesData(self, vehicles):
        self.defaultInfo()
        for vID, vData in vehicles.iteritems():
            self.__addVehicleInfoVO(vID, arena_vos.VehicleArenaInfoVO(vID, **vData))

        self.__findSquads()

    def buildStatsData(self, stats):
        self.clearStats()
        for vID, vStats in stats.iteritems():
            vStatsVO = self.__vStatsVOs[vID]
            vStatsVO.updateVehicleStats(**vStats)

    def addVehicleInfo(self, vehicleID, vInfo):
        vInfoVO, updated = None, []
        if vehicleID not in self.__vInfoVOs:
            vInfoVO = arena_vos.VehicleArenaInfoVO(vehicleID, **vInfo)
            if self.__addVehicleInfoVO(vehicleID, vInfoVO):
                updated = self.__findSquads(exclude=(vehicleID,))
        else:
            _logger.warning('Vehicle already exists: %r', self.__vInfoVOs[vehicleID])
        return (vInfoVO, updated)

    def updateVehicleInfo(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.update(**vInfo)
        prebattleID = vInfoVO.prebattleID
        if flags & _OP.PREBATTLE_CHANGED > 0:
            self.__squadFinder.addVehicleInfo(vInfoVO.team, prebattleID, vID)
            result = self.__findSquads(exclude=(vID,))
        else:
            result = []
        avatarSessionID = vInfoVO.player.avatarSessionID
        if avatarSessionID:
            self.__avatarsVIDs[avatarSessionID] = vID
        accountDBID = vInfoVO.player.accountDBID
        if accountDBID:
            self.__accountVIDs[accountDBID] = vID
        result.insert(0, (flags, vInfoVO))
        return result

    def updateVehicleStatus(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updateVehicleStatus(**vInfo)
        return (flags, vInfoVO)

    def updatePlayerStatus(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updatePlayerStatus(**vInfo)
        return (flags, vInfoVO)

    def updateVehicleStats(self, vID, vStats):
        vStatsVO = self.__vStatsVOs[vID]
        flags = vStatsVO.updateVehicleStats(**vStats)
        return (flags, vStatsVO)

    def updateVehicleInteractiveStats(self, iStats):
        self.__vStatsVOs.clearInteractiveStats()
        updatedStats = []
        updatedStatuses = []
        for (vehicleID, _), iStat in iStats.iteritems():
            vStatsVO = self.__vStatsVOs[vehicleID]
            flags = vStatsVO.updateInteractiveStats(*iStat)
            if flags != _OP.NONE:
                updatedStats.append((flags, vStatsVO))
            vInfo = self.__vInfoVOs[vehicleID]
            flags = vInfo.updateVehicleStatus(isAlive=vInfo.isAlive(), isAvatarReady=vInfo.isReady(), stopRespawn=vStatsVO.stopRespawn)
            if flags != _OP.NONE:
                updatedStatuses.append((flags, vInfo))

        return (updatedStats, updatedStatuses)

    def updateGameModeSpecificStats(self, vehicleID, isStatic, stats):
        if not isStatic:
            vStatsVO = self.__vStatsVOs[vehicleID]
            flags = vStatsVO.updateGameModeSpecificStats(stats)
            return (flags, vStatsVO)
        vInfoVO = self.__vInfoVOs[vehicleID]
        flags = vInfoVO.updateGameModeSpecificStats(stats)
        return (flags, vInfoVO)

    def updateInvitationStatus(self, avatarSessionID, include, exclude=_INVITATION_STATUS.NONE):
        vehicleID = self.getVehIDBySessionID(avatarSessionID)
        if vehicleID:
            vInfoVO = self.__vInfoVOs[vehicleID]
            flags = vInfoVO.updateInvitationStatus(include=include, exclude=exclude)
        else:
            self.__invitationStatuses[avatarSessionID] = (include, exclude)
            flags, vInfoVO = _OP.NONE, None
        return (flags, vInfoVO)

    def updateChatCommandState(self, vID, chatCommandState):
        vStatsVO = self.__vStatsVOs[vID]
        flags = vStatsVO.updateChatCommandState(chatCommandState)
        return (flags, vStatsVO)

    def updateVehicleSpottedStatus(self, vID, spottedStatus):
        vStatsVO = self.__vStatsVOs[vID]
        flags = vStatsVO.updateSpottedStatus(spottedStatus)
        return (flags, vStatsVO)

    def updateVehicleDogTag(self, vID, vInfo):
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updateVehicleDogTag(**vInfo)
        return (flags, vInfoVO)

    def isRequiredDataExists(self):
        return self.__checkRequiredData()

    def getTeamsOnArena(self):
        return self.__teamsOnArena

    def getAllyTeams(self):
        return (self.__playerTeam,)

    def getEnemyTeams(self):
        allyTeams = self.getAllyTeams()
        return [ t for t in self.__teamsOnArena if t not in allyTeams ]

    def isEnemyTeam(self, team):
        return team not in self.getAllyTeams()

    def isAllyTeam(self, team):
        return team in self.getAllyTeams()

    def isMultipleTeams(self):
        return len(self.__teamsOnArena) > TEAMS_IN_ARENA.MIN_TEAMS

    def switchCurrentTeam(self, team):
        self.__playerTeam = team
        from PlayerEvents import g_playerEvents
        g_playerEvents.onTeamChanged(team)

    def getMultiTeamsType(self):
        if self.isMultipleTeams():
            squadTeamNumber = self.__squadFinder.getNumberOfSquads()
            if not squadTeamNumber:
                return MULTIPLE_TEAMS_TYPE.FFA
            if squadTeamNumber == len(self.__teamsOnArena):
                return MULTIPLE_TEAMS_TYPE.TDM
            return MULTIPLE_TEAMS_TYPE.MIXED
        return MULTIPLE_TEAMS_TYPE.UNDEFINED

    def getMultiTeamsIndexes(self):
        result = {}
        for team in self.__teamsOnArena:
            teamIdx = 0
            vInfoVO = next(vos_collections.TeamVehiclesInfoCollection(team).iterator(self), None)
            if vInfoVO is not None and vInfoVO.squadIndex > 0:
                teamIdx = vInfoVO.squadIndex
            result[team] = teamIdx

        return result

    def getTeamIDsIterator(self):
        allyTeams = self.getAllyTeams()
        for teamIdx in self.__teamsOnArena:
            yield (teamIdx not in allyTeams, teamIdx)

    def getNumberOfTeam(self, enemy=False):
        return first(self.getEnemyTeams()) if enemy else self.__playerTeam

    def getPersonalDescription(self):
        return self.__description

    def getNumberOfSquads(self):
        return self.__squadFinder.getNumberOfSquads()

    def getPlayerVehicleID(self, forceUpdate=False):
        if forceUpdate and self.__playerVehicleID is None:
            self.__tryToGetRequiredData()
        return self.__playerVehicleID

    def getAttachedVehicleID(self):
        return avatar_getter.getVehicleIDAttached()

    def getVehicleInfo(self, vID=None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        try:
            result = self.__vInfoVOs[vID]
        except KeyError:
            result = arena_vos.VehicleArenaInfoVO(vID)

        return result

    def getVehicleStats(self, vID=None):
        if vID is None:
            vID = self.getPlayerVehicleID()
        return self.__vStatsVOs[vID]

    def getVehiclesCountInPrebattle(self, team, prebattleID):
        return self.__squadFinder.getNumberOfSquadmen(team, prebattleID)

    def getSquadSizes(self):
        result = {teamID:{} for teamID in self.__teamsOnArena}
        for squadSizeDescription in self.__squadFinder.findSquadSizes():
            result[squadSizeDescription.teamID][squadSizeDescription.squadID] = squadSizeDescription.squadSize

        return result

    def getPlayerGuiProps(self, vID, team):
        if team in self.getAllyTeams():
            if self.isSquadMan(vID=vID):
                return PLAYER_GUI_PROPS.squadman
            if self.isTeamKiller(vID=vID):
                return PLAYER_GUI_PROPS.teamKiller
            return PLAYER_GUI_PROPS.ally
        return PLAYER_GUI_PROPS.enemy

    def isSquadMan(self, vID, prebattleID=None):
        if prebattleID is None:
            if not self.__playerVehicleID:
                self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
            if self.__playerVehicleID in self.__vInfoVOs:
                prebattleID = self.__vInfoVOs[self.__playerVehicleID].prebattleID
        return self.__getStateFlag(vID, 'isSquadMan', playerTeam=self.__playerTeam, prebattleID=prebattleID)

    def isGeneral(self, vID):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        arenaDP = sessionProvider.getArenaDP()
        vo = arenaDP.getVehicleStats(vID)
        rank = vo.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.RANK)
        return True if rank == PLAYER_RANK.GENERAL else False

    def isTeamKiller(self, vID):
        return self.__getStateFlag(vID, 'isTeamKiller', playerTeam=self.__playerTeam)

    def isObserver(self, vID):
        if vID not in self.__vInfoVOs:
            _logger.warning('vID not in __vInfoVOs, vID = %s', vID)
            return None
        else:
            return self.__getStateFlag(vID, 'isObserver')

    def isPlayerObserver(self):
        if self.__playerVehicleID not in self.__vInfoVOs:
            _logger.warning('vID not in __vInfoVOs, vID = %s', self.__playerVehicleID)
            return None
        else:
            return self.__getStateFlag(self.__playerVehicleID, 'isObserver')

    def getVehIDByAccDBID(self, accDBID):
        try:
            vID = self.__accountVIDs[accDBID]
        except KeyError:
            vID = 0

        return vID

    def getVehIDBySessionID(self, avatarSessionID):
        try:
            vID = self.__avatarsVIDs[avatarSessionID]
        except KeyError:
            vID = 0

        return vID

    def getSessionIDByVehID(self, vehID):
        try:
            sessionID = self.__vInfoVOs[vehID].player.avatarSessionID
        except KeyError:
            sessionID = ''

        return sessionID

    def getVehiclesInfoIterator(self):
        return self.__vInfoVOs.itervalues()

    def getVehiclesStatsIterator(self):
        return self.__vStatsVOs.itervalues()

    def getVehiclesItemsGenerator(self):
        for vInfo in self.__vInfoVOs.itervalues():
            yield (vInfo, self.__vStatsVOs[vInfo.vehicleID])

    def getActiveVehiclesGenerator(self):
        for vInfo in self.__vInfoVOs.itervalues():
            if not isSpawnedBot(vInfo.vehicleType.tags) and not vInfo.isObserver():
                yield (vInfo, self.__vStatsVOs[vInfo.vehicleID])

    def getAlliesVehiclesNumber(self):
        return vos_collections.AllyItemsCollection().count(self)

    def getEnemiesVehiclesNumber(self):
        return vos_collections.EnemyItemsCollection().count(self)

    def isAlly(self, vehicleID):
        vehInfo = self.getVehicleInfo(vehicleID)
        return self.isAllyTeam(vehInfo.team)

    def __findSquads(self, exclude=None):
        result = []
        prebattleID = self.getVehicleInfo().prebattleID
        if exclude is None:
            exclude = ()
        for vehicleID, squadIndex in self.__squadFinder.findSquads():
            try:
                vInfoVO = self.__vInfoVOs[vehicleID]
            except KeyError:
                pass

            if squadIndex != vInfoVO.squadIndex or not vInfoVO.isSquadMan() or vInfoVO.isSquadMan(prebattleID=prebattleID):
                vInfoVO.squadIndex = squadIndex
                vInfoVO.updatePlayerStatus(isSquadMan=True)
                if vehicleID not in exclude:
                    result.append((_OP.PREBATTLE_CHANGED, vInfoVO))

        return result

    def __addVehicleInfoVO(self, vID, vInfoVO):
        avatarSessionID = vInfoVO.player.avatarSessionID
        accountDBID = vInfoVO.player.accountDBID
        hasPrbID = False
        self.__vInfoVOs[vID] = vInfoVO
        if accountDBID:
            self.__accountVIDs[accountDBID] = vID
        if avatarSessionID:
            self.__avatarsVIDs[avatarSessionID] = vID
            if avatarSessionID in self.__invitationStatuses:
                include, exclude = self.__invitationStatuses.pop(avatarSessionID)
                vInfoVO.updateInvitationStatus(include=include, exclude=exclude)
        prebattleID = vInfoVO.prebattleID
        if prebattleID > 0:
            self.__squadFinder.addVehicleInfo(vInfoVO.team, prebattleID, vID)
            hasPrbID = True
        return hasPrbID

    def __getStateFlag(self, vID, flagName, **kwargs):
        result = False
        if vID in self.__vInfoVOs:
            result = operator.methodcaller(flagName, **kwargs)(self.__vInfoVOs[vID])
        else:
            _logger.warning('vID not in __vInfoVOs, vID = %s', vID)
        return result

    def __checkRequiredData(self):
        result = self.__playerTeam > 0 and self.__playerVehicleID > 0
        if result:
            self.__setPersonalDataOnce()
        return result or self.__tryToGetRequiredData()

    def __tryToGetRequiredData(self):
        successful = True
        self.__playerTeam = avatar_getter.getPlayerTeam()
        if not self.__playerTeam:
            successful = False
            _logger.info("Player's team not found.")
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        if not self.__playerVehicleID:
            successful = False
            _logger.info("Player's vehicle ID not found.")
        if not successful:
            playerName = avatar_getter.getPlayerName()
            _logger.info('Uses slow player search by name')
            for vo in self.__vInfoVOs.itervalues():
                if vo.player.name == playerName:
                    self.__playerTeam = vo.team
                    self.__playerVehicleID = vo.vehicleID
                    successful = True
                    break

        if successful:
            self.__setPersonalDataOnce()
        return successful

    def __setPersonalDataOnce(self):
        if not self.__description.isPersonalDataSet():
            if self.__playerVehicleID is None:
                _logger.error("Player's vehicle ID not be None")
                return
            if self.__playerVehicleID in self.__vInfoVOs:
                self.__description.setPersonalData(self.__vInfoVOs[self.__playerVehicleID])
        return
