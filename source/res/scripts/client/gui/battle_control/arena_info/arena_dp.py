# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_dp.py
import BigWorld
import operator
from constants import TEAMS_IN_ARENA
from debug_utils import LOG_NOTE, LOG_WARNING, LOG_DEBUG
from shared_utils import first
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import arena_descrs
from gui.battle_control.arena_info import arena_vos
from gui.battle_control.arena_info import settings
from gui.battle_control.arena_info import squad_finder
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.battle_constants import MULTIPLE_TEAMS_TYPE
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from skeletons.gui.battle_session import IArenaDataProvider
_OP = settings.INVALIDATE_OP
_INVITATION_STATUS = settings.INVITATION_DELIVERY_STATUS

class ArenaDataProvider(IArenaDataProvider):
    """ Data provider containing precached information about vehicles in arena,
    their statistics.
    """
    __slots__ = ('__playerTeam', '__playerVehicleID', '__vInfoVOs', '__vStatsVOs', '__playersVIDs', '__weakref__', '__teamsOnArena', '__squadFinder', '__description', '__invitationStatuses')

    def __init__(self, setup):
        super(ArenaDataProvider, self).__init__()
        self.__playerTeam = avatar_getter.getPlayerTeam(avatar=setup.avatar)
        self.__teamsOnArena = setup.arenaVisitor.type.getTeamsOnArenaRange()
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID(setup.avatar)
        self.__vInfoVOs = {}
        self.__vStatsVOs = arena_vos.VehicleArenaStatsDict()
        self.__playersVIDs = {}
        self.__invitationStatuses = {}
        self.__squadFinder = squad_finder.createSquadFinder(setup.arenaVisitor)
        self.__description = arena_descrs.createDescription(setup.arenaVisitor)

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def clearInfo(self):
        """Clears information about vehicles."""
        self.__vInfoVOs.clear()
        self.__playersVIDs.clear()
        self.__squadFinder.clear()

    def clearStats(self):
        """Clears statistics."""
        self.__vStatsVOs.clear()

    def clear(self):
        """Clears data."""
        self.clearInfo()
        self.clearStats()
        self.__description.clear()
        self.__invitationStatuses.clear()

    def defaultInfo(self):
        """Sets default information about vehicles."""
        self.clearInfo()

    def buildVehiclesData(self, vehicles):
        """ New list of vehicles has been received.
        :param vehicles: dict(<vehicleID>: { <vehicle info> }, ...).
        """
        self.defaultInfo()
        for vID, vData in vehicles.iteritems():
            self.__addVehicleInfoVO(vID, arena_vos.VehicleArenaInfoVO(vID, **vData))

        self.__findSquads()

    def buildStatsData(self, stats):
        """New list of statistics has been received.
        :param stats: dict(<vehicleID>: {<vehicle statistic>}, ...).
        """
        self.clearStats()
        for vID, vStats in stats.iteritems():
            vStatsVO = self.__vStatsVOs[vID]
            vStatsVO.updateVehicleStats(**vStats)

    def addVehicleInfo(self, vehicleID, vInfo):
        """Vehicle has been added to arena.
        :param vehicleID: long containing vehicle ID.
        :param vInfo: dict containing information about vehicle.
        :return: tuple(instance of VehicleArenaInfoVO that added to dataProvider,
            [(flags, updated VehicleArenaInfoVO), ...]).
        """
        vInfoVO, updated = None, []
        if vehicleID not in self.__vInfoVOs:
            vInfoVO = arena_vos.VehicleArenaInfoVO(vehicleID, **vInfo)
            if self.__addVehicleInfoVO(vehicleID, vInfoVO):
                updated = self.__findSquads(exclude=(vehicleID,))
        else:
            LOG_WARNING('Vehicle already exists', self.__vInfoVOs[vehicleID])
        return (vInfoVO, updated)

    def updateVehicleInfo(self, vID, vInfo):
        """Vehicle has been updated on arena.
        :param vID: long containing vehicle ID.
        :param vInfo: dict containing updated information.
        :return: [(<flags to invalidate>, <updated VehicleArenaInfoVO>), ...].
        """
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.update(**vInfo)
        prebattleID = vInfoVO.prebattleID
        if flags & _OP.PREBATTLE_CHANGED > 0:
            self.__squadFinder.addVehicleInfo(vInfoVO.team, prebattleID, vID)
            result = self.__findSquads(exclude=(vID,))
        else:
            result = []
        dbID = vInfoVO.player.accountDBID
        if dbID:
            self.__playersVIDs[dbID] = vID
        result.insert(0, (flags, vInfoVO))
        return result

    def updateVehicleStatus(self, vID, vInfo):
        """Status of vehicle (is alive, is ready, ...) has been changed.
        :param vID: long containing vehicle ID.
        :param vInfo: dict containing updated information.
        :return: tuple(<flags to invalidate> , <updated VehicleArenaInfoVO>).
        """
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updateVehicleStatus(**vInfo)
        return (flags, vInfoVO)

    def updatePlayerStatus(self, vID, vInfo):
        """Status of player (is team killer, is squadman, ...) has been changed.
        :param vID: long containing vehicle ID.
        :param vInfo: dict containing updated information.
        :return: tuple( <flags to invalidate> , <updated VehicleArenaInfoVO> ).
        """
        vInfoVO = self.__vInfoVOs[vID]
        flags = vInfoVO.updatePlayerStatus(**vInfo)
        return (flags, vInfoVO)

    def updateVehicleStats(self, vID, vStats):
        """Statistics of vehicle has been changed.
        :param vID: long containing vehicle ID.
        :param vStats: dict containing new statistics.
        :return: tuple(<flags to invalidate>, <updated VehicleArenaStatsVO>).
        """
        vStatsVO = self.__vStatsVOs[vID]
        flags = vStatsVO.updateVehicleStats(**vStats)
        return (flags, vStatsVO)

    def updateVehicleInteractiveStats(self, iStats):
        """Interactive statistics has been changed.
        :param iStats: dict containing new statistics.
        :return: tuple([(flags, vStatsVO), ...], [(flags, vInfoVO), ...]).
        """
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

    def updateInvitationStatus(self, accountDBID, include, exclude=_INVITATION_STATUS.NONE):
        """Invitations states has been changed.
        :param accountDBID: long containing account database ID.
        :param include: bitmask containing INVITATION_DELIVERY_STATUS on including to status.
        :param exclude: bitmask containing INVITATION_DELIVERY_STATUS on excluding from status.
        :return: tuple( <flags to invalidate> , <updated VehicleArenaInfoVO> ).
        """
        vehicleID = self.getVehIDByAccDBID(accountDBID)
        if vehicleID:
            vInfoVO = self.__vInfoVOs[vehicleID]
            flags = vInfoVO.updateInvitationStatus(include=include, exclude=exclude)
        else:
            self.__invitationStatuses[accountDBID] = (include, exclude)
            flags, vInfoVO = _OP.NONE, None
        return (flags, vInfoVO)

    def isRequiredDataExists(self):
        return self.__checkRequiredData()

    def getTeamsOnArena(self):
        return self.__teamsOnArena

    def getAllyTeams(self):
        return (self.__playerTeam,)

    def getEnemyTeams(self):
        allyTeams = self.getAllyTeams()
        return filter(lambda t: t not in allyTeams, self.__teamsOnArena)

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
        """Returns multi team indexes for teams, and zero for solo players.
        :return: dict(team: teamIdx, ...)
        """
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
        if enemy:
            return first(self.getEnemyTeams())
        else:
            return self.__playerTeam

    def getPersonalDescription(self):
        return self.__description

    def getPlayerVehicleID(self, forceUpdate=False):
        if forceUpdate and self.__playerVehicleID is None:
            self.__tryToGetRequiredData()
        return self.__playerVehicleID

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

    def isTeamKiller(self, vID):
        """ Is desired player team-killer. Note: shows only team-killer for his team.
        :param vID: vehicle ID from player.arena.vehicles.
        :return: True - if player is team-killer, otherwise - False.
        """
        return self.__getStateFlag(vID, 'isTeamKiller', playerTeam=self.__playerTeam)

    def isObserver(self, vID):
        """ Is desired player observer. @see WOTD-5872.
        :param vID: vehicle ID from player.arena.vehicles
        :return: True - if player is observer, otherwise - False.
        """
        return self.__getStateFlag(vID, 'isObserver')

    def isPlayerObserver(self):
        """ Is current player observer.
        :return: True - if current player is observer, otherwise - False.
        """
        return self.__getStateFlag(self.__playerVehicleID, 'isObserver')

    def getVehIDByAccDBID(self, accDBID):
        """
        Gets player vehicle ID by account database ID.
        
        :param accDBID: account database ID.
        :return: player vehicle ID (long) or 0 if there no player with the given database ID.
        """
        try:
            vID = self.__playersVIDs[accDBID]
        except KeyError:
            vID = 0

        return vID

    def getAccountDBIDByVehID(self, vID):
        """
        Gets player database ID by the given vehicle ID.
        
        :param vID: vehicle ID
        :return: account database ID (long) or 0 if there no vehicle with the given ID.
        """
        for accountDBID, vInfo in self.__playersVIDs:
            if vInfo.vehicleID == vID:
                break
        else:
            accountDBID = 0

        return accountDBID

    def getVehiclesInfoIterator(self):
        """ Gets iterator where is each item is VehicleArenaInfoVO.
        :return: iterator.
        """
        return self.__vInfoVOs.itervalues()

    def getVehiclesStatsIterator(self):
        """ Gets iterator where is each item is VehicleArenaStatsVO.
        :return: iterator.
        """
        return self.__vStatsVOs.itervalues()

    def getVehiclesItemsGenerator(self):
        """ Gets generator where is each item is tuple(VehicleArenaInfoVO, VehicleArenaStatsVO).
        :return: generator.
        """
        for vInfo in self.__vInfoVOs.itervalues():
            yield (vInfo, self.__vStatsVOs[vInfo.vehicleID])

    def getAlliesVehiclesNumber(self):
        """Gets number of vehicles that are allies
        :return: number of vehicles that are allies.
        :rtype: int.
        """
        return vos_collections.AllyItemsCollection().count(self)

    def getEnemiesVehiclesNumber(self):
        """Gets number of vehicles that are enemies
        :return: number of vehicles that are enemies.
        :rtype: int.
        """
        return vos_collections.EnemyItemsCollection().count(self)

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
        dbID = vInfoVO.player.accountDBID
        hasPrbID = False
        self.__vInfoVOs[vID] = vInfoVO
        if dbID:
            self.__playersVIDs[dbID] = vID
            if dbID in self.__invitationStatuses:
                include, exclude = self.__invitationStatuses.pop(dbID)
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
            LOG_NOTE("Player's team not found.")
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        if not self.__playerVehicleID:
            successful = False
            LOG_NOTE("Player's vehicle ID not found.")
        if not successful:
            playerName = avatar_getter.getPlayerName()
            LOG_NOTE('Uses slow player search by name')
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
            assert self.__playerVehicleID, "Player's vehicle ID not be None"
            if self.__playerVehicleID in self.__vInfoVOs:
                self.__description.setPersonalData(self.__vInfoVOs[self.__playerVehicleID])
