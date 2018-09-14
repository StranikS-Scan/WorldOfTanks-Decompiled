# Embedded file name: scripts/client/gui/prb_control/restrictions/limits.py
from collections import defaultdict
import weakref
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_ACCOUNT_STATE, PREBATTLE_TYPE
from gui.prb_control import getClassLevelLimits, getTotalLevelLimits
from gui.prb_control import getPrebattleRosters, getMaxSizeLimits
from gui.prb_control.restrictions.interfaces import IVehicleLimit, ITeamLimit
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_RESTRICTION, UNIT_RESTRICTION
from gui.shared.ItemsCache import g_itemsCache
from items import vehicles
from items.vehicles import VehicleDescr, VEHICLE_CLASS_TAGS
from prebattle_shared import isTeamValid, isVehicleValid

class VehicleIsValid(IVehicleLimit):

    def __init__(self, checkForEventBattles = True):
        self.__checkForEventBattles = checkForEventBattles

    def check(self, teamLimits):
        if not g_currentVehicle.isReadyToFight():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_READY)
        vehicle = g_currentVehicle.item
        if self.__checkForEventBattles and vehicle.isOnlyForEventBattles:
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        shellsList = []
        for shell in vehicle.shells:
            shellsList.extend([shell.intCD, shell.count])

        return isVehicleValid(vehicle.descriptor, shellsList, teamLimits)


class AbstractTeamIsValid(ITeamLimit):

    def _getAccountsInfo(self, rosters, team):
        rosterKey = None
        if team is 1:
            rosterKey = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1
        elif team is 2:
            rosterKey = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2
        if rosterKey in rosters:
            accountsInfo = rosters[rosterKey]
        else:
            accountsInfo = {}
        return accountsInfo


class TeamIsValid(AbstractTeamIsValid):

    def check(self, rosters, team, teamLimits):
        return isTeamValid(self._getAccountsInfo(rosters, team), teamLimits)


class ObserverInTeamIsValid(AbstractTeamIsValid):

    def check(self, rosters, team, teamLimits):
        accountsInfo = self._getAccountsInfo(rosters, team)
        if len(accountsInfo) < teamLimits['minCount']:
            return (False, 'limit/minCount')
        if self.__isAllObservers(accountsInfo):
            return (False, 'observers')
        return (True, '')

    @classmethod
    def __isAllObservers(cls, accountsInfo):
        if not len(accountsInfo):
            return False
        for accInfo in accountsInfo.itervalues():
            if not accInfo['state'] & PREBATTLE_ACCOUNT_STATE.READY:
                continue
            if 'vehTypeCompDescr' not in accInfo or 'vehLevel' not in accInfo:
                vehDescr = vehicles.VehicleDescr(compactDescr=accInfo['vehCompDescr'])
                vehTypeCompDescr = vehDescr.type.compactDescr
            else:
                vehTypeCompDescr = accInfo['vehTypeCompDescr']
            if not g_itemsCache.items.getItemByCD(vehTypeCompDescr).isObserver:
                return False

        return True


class TeamNoPlayersInBattle(ITeamLimit):

    def __init__(self, prbType):
        super(TeamNoPlayersInBattle, self).__init__()
        self.__range = PREBATTLE_ROSTER.getRange(prbType)

    def __isPlayerInBattle(self, player):
        return player['state'] & PREBATTLE_ACCOUNT_STATE.IN_BATTLE != 0

    def check(self, rosters, team, teamLimits):
        for rosterKey in self.__range:
            if rosterKey & team and rosterKey in rosters:
                filtered = filter(self.__isPlayerInBattle, rosters[rosterKey].itervalues())
                if len(filtered):
                    return (False, PREBATTLE_RESTRICTION.HAS_PLAYER_IN_BATTLE)

        return (True, '')


class MaxCount(ITeamLimit):

    def __init__(self, assigned = True):
        super(MaxCount, self).__init__()
        self.__assigned = assigned

    def check(self, rosters, team, teamLimits):
        if self.__assigned:
            index = 0
            if team is 1:
                key = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1
            else:
                key = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2
        else:
            index = 1
            if team is 1:
                key = PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1
            else:
                key = PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM2
        maxCount = getMaxSizeLimits(teamLimits)[index]
        if key in rosters and len(rosters[key]) >= maxCount:
            return (False, PREBATTLE_RESTRICTION.LIMIT_MAX_COUNT)
        return (True, '')


class TotalMaxCount(ITeamLimit):

    def check(self, rosters, team, teamLimits):
        maxCount = sum(getMaxSizeLimits(teamLimits))
        result, restriction = True, ''
        if team is 1:
            keys = [PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1, PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1]
        else:
            keys = [PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2, PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM2]
        playersCount = 0
        for key in keys:
            if key in rosters:
                playersCount += len(rosters[key])

        if playersCount >= maxCount:
            result, restriction = False, PREBATTLE_RESTRICTION.LIMIT_MAX_COUNT
        return (result, restriction)


class VehiclesLevelLimit(ITeamLimit):

    def check(self, rosters, team, teamLimits):
        isValid, notValidReason = True, ''
        assignedRosters = rosters.get(team, {})
        totalLevel, classLevels = self.__calculate(assignedRosters)
        for classTag in VEHICLE_CLASS_TAGS:
            minLevel, maxLevel = getClassLevelLimits(teamLimits, classTag)
            currentLevel = classLevels[classTag]
            vClassTags = PREBATTLE_RESTRICTION.getVehClassTags()
            if not (minLevel <= currentLevel <= maxLevel or currentLevel == 0):
                isValid = False
                if classTag in vClassTags:
                    notValidReason = vClassTags[classTag]
                else:
                    notValidReason = PREBATTLE_RESTRICTION.LIMIT_CLASSES

        if isValid:
            minLevel, maxLevel = getTotalLevelLimits(teamLimits)
            if not minLevel <= totalLevel <= maxLevel:
                isValid = False
                notValidReason = PREBATTLE_RESTRICTION.LIMIT_TOTAL_LEVEL
        return (isValid, notValidReason)

    def __calculate(self, rosters):
        classLevels = defaultdict(lambda : 0)
        totalLevel = 0
        vehClassTags = set(VEHICLE_CLASS_TAGS)
        for roster in rosters.itervalues():
            if not roster['state'] & PREBATTLE_ACCOUNT_STATE.READY:
                continue
            vehCompDescr = roster.get('vehCompDescr', '')
            if vehCompDescr is not None and len(vehCompDescr):
                vehType = VehicleDescr(compactDescr=vehCompDescr).type
                level = vehType.level
                union = vehClassTags & vehType.tags
                if len(union):
                    vehClass = union.pop()
                    classLevels[vehClass] = max(classLevels[vehClass], level)
                totalLevel += level

        return (totalLevel, classLevels)


class LimitsCollection(object):

    def __init__(self, functional, vehicleLimits, teamLimits):
        self.__functional = weakref.proxy(functional)
        self.__vehicleLimits = vehicleLimits
        self.__teamLimits = teamLimits

    def clear(self):
        self.__functional = None
        self.__vehicleLimits = ()
        self.__teamLimits = ()
        return

    def isVehicleValid(self):
        result, errorCode = True, ''
        settings = self.__functional.getSettings()
        teamLimits = settings.getTeamLimits(self.__functional.getPlayerTeam())
        for limit in self.__vehicleLimits:
            result, errorCode = limit.check(teamLimits)
            if not result:
                break

        return (result, errorCode)

    def isTeamValid(self, team = None):
        result, errorCode = True, ''
        if team is None:
            team = self.__functional.getPlayerTeam()
        settings = self.__functional.getSettings()
        teamLimits = settings.getTeamLimits(team)
        rosters = getPrebattleRosters()
        for limit in self.__teamLimits:
            result, errorCode = limit.check(rosters, team, teamLimits)
            if not result:
                break

        return (result, errorCode)

    def isTeamsValid(self):
        settings = self.__functional.getSettings()
        rosters = getPrebattleRosters()
        for team in [1, 2]:
            teamLimits = settings.getTeamLimits(team)
            for limit in self.__teamLimits:
                result, errorCode = limit.check(rosters, team, teamLimits)
                if not result:
                    return (result, errorCode)

        return (True, '')

    def isMaxCountValid(self, team, assigned):
        settings = self.__functional.getSettings()
        rosters = getPrebattleRosters()
        return MaxCount(assigned=assigned).check(rosters, team, settings.getTeamLimits(team))


class DefaultLimits(LimitsCollection):

    def __init__(self, functional):
        super(DefaultLimits, self).__init__(functional, (VehicleIsValid(),), (TeamIsValid(),))


class SquadLimits(LimitsCollection):

    def __init__(self, functional):
        super(SquadLimits, self).__init__(functional, (VehicleIsValid(checkForEventBattles=False),), (TeamIsValid(),))


class TrainingLimits(LimitsCollection):

    def __init__(self, functional):
        super(TrainingLimits, self).__init__(functional, (VehicleIsValid(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.TRAINING), TeamIsValid(), ObserverInTeamIsValid()))


class CompanyLimits(LimitsCollection):

    def __init__(self, functional):
        super(CompanyLimits, self).__init__(functional, (VehicleIsValid(),), (VehiclesLevelLimit(), TeamIsValid()))


class BattleSessionLimits(LimitsCollection):

    def __init__(self, functional):
        super(BattleSessionLimits, self).__init__(functional, (VehicleIsValid(),), (VehiclesLevelLimit(), TeamIsValid()))


class _UnitActionValidator(object):

    def __init__(self, rosterSettings, hasPlayersSearch = False):
        super(_UnitActionValidator, self).__init__()
        self._hasPlayersSearch = hasPlayersSearch
        self._rosterSettings = weakref.proxy(rosterSettings)

    def clear(self):
        self._rosterSettings = None
        return

    def canDoAction(self, functional):
        state = functional.getState()
        stats = functional.getStats()
        vInfo = functional.getVehicleInfo()
        pInfo = functional.getPlayerInfo()
        if pInfo.isCreator():
            valid, restriction = self.canCreatorDoAction(pInfo, stats, state, vInfo)
        else:
            valid, restriction = self.canPlayerDoAction(pInfo, state, vInfo)
        return (valid, restriction)

    def canCreatorDoAction(self, pInfo, stats, state, vInfo):
        valid, restriction = self.canPlayerDoAction(pInfo, state, vInfo)
        if not valid:
            return (valid, restriction)
        valid, restriction = self._validateLevels(stats, state)
        if not valid:
            return (valid, restriction)
        return self._validateSlots(stats, state)

    def canPlayerDoAction(self, pInfo, state, vInfo):
        if state.isInIdle():
            return (False, UNIT_RESTRICTION.IS_IN_IDLE)
        if not pInfo.isCreator() and state.isInPreArena():
            return (False, UNIT_RESTRICTION.IS_IN_PRE_ARENA)
        if pInfo.isInSlot:
            if vInfo.isEmpty():
                return (False, UNIT_RESTRICTION.VEHICLE_NOT_SELECTED)
            if not vInfo.isReadyToBattle():
                return (False, UNIT_RESTRICTION.VEHICLE_NOT_VALID)
        else:
            return (False, UNIT_RESTRICTION.NOT_IN_SLOT)
        return (True, UNIT_RESTRICTION.UNDEFINED)

    def getRestrictionByLevel(self, stats, state):
        return self._validateLevels(stats, state)[1]

    def getUnitInvalidLevels(self, stats):
        return []

    def _areVehiclesSelected(self, stats):
        return not stats.freeSlotsCount and len(stats.levelsSeq) == stats.occupiedSlotsCount

    def _validateSlots(self, stats, state):
        if stats.readyCount != stats.occupiedSlotsCount:
            return (False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)
        return (True, UNIT_RESTRICTION.UNDEFINED)

    def _validateLevels(self, stats, state):
        if not stats.curTotalLevel:
            return (False, UNIT_RESTRICTION.ZERO_TOTAL_LEVEL)
        if not self._hasPlayersSearch or self._areVehiclesSelected(stats):
            if not state.isDevMode() and stats.curTotalLevel < stats.minTotalLevel:
                return (False, UNIT_RESTRICTION.MIN_TOTAL_LEVEL)
            if stats.curTotalLevel > stats.maxTotalLevel:
                return (False, UNIT_RESTRICTION.MAX_TOTAL_LEVEL)
        return (True, UNIT_RESTRICTION.UNDEFINED)


class UnitActionValidator(_UnitActionValidator):

    def __init__(self, rosterSettings):
        super(UnitActionValidator, self).__init__(rosterSettings, True)
        self._maxLevel = rosterSettings.getMaxLevel()
        maxSlots = rosterSettings.getMaxSlots()
        maxTotalLevel = rosterSettings.getMaxTotalLevel()
        self._compensation = self._maxLevel * maxSlots - maxTotalLevel

    def getRestrictionByLevel(self, stats, state):
        valid, restriction = self._validateLevels(stats, state)
        if valid and not self._areVehiclesSelected(stats):
            restriction = UNIT_RESTRICTION.NEED_PLAYERS_SEARCH
        return restriction

    def getUnitInvalidLevels(self, stats):
        if self._compensation <= 0:
            return []
        compensation = self._compensation
        levels = []
        for level in stats.levelsSeq:
            if not level:
                continue
            diff = self._maxLevel - level
            if diff:
                if level not in levels:
                    levels.append(level)
                if compensation > 0:
                    compensation -= diff
                else:
                    levels.sort()
                    return levels

        return []

    def _validateLevels(self, stats, state):
        if not state.isDevMode():
            if stats.occupiedSlotsCount > 1 and stats.freeSlotsCount > 0 and len(self.getUnitInvalidLevels(stats)):
                return (False, UNIT_RESTRICTION.INVALID_TOTAL_LEVEL)
        return super(UnitActionValidator, self)._validateLevels(stats, state)


class SortieActionValidator(_UnitActionValidator):

    def __init__(self, rosterSettings):
        super(SortieActionValidator, self).__init__(rosterSettings, False)

    def _validateSlots(self, stats, state):
        if state.isDevMode():
            return (True, UNIT_RESTRICTION.UNDEFINED)
        if self._rosterSettings.getMinSlots() > stats.occupiedSlotsCount:
            return (False, UNIT_RESTRICTION.MIN_SLOTS)
        if stats.readyCount != stats.occupiedSlotsCount:
            return (False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)
        return (True, UNIT_RESTRICTION.UNDEFINED)


class FortBattleActionValidator(_UnitActionValidator):

    def __init__(self, rosterSettings):
        super(FortBattleActionValidator, self).__init__(rosterSettings, False)


class ClubsActionValidator(_UnitActionValidator):

    def __init__(self, rosterSettings, proxy):
        super(ClubsActionValidator, self).__init__(rosterSettings)
        self.__proxy = weakref.proxy(proxy)

    def _validateSlots(self, stats, state):
        if state.isDevMode():
            return (True, UNIT_RESTRICTION.UNDEFINED)
        _, unit = self.__proxy.getUnit()
        if unit.isRated() and self._rosterSettings.getMinSlots() > stats.occupiedSlotsCount:
            return (False, UNIT_RESTRICTION.MIN_SLOTS)
        if not state.isInPreArena() and stats.readyCount != stats.occupiedSlotsCount:
            return (False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)
        return (True, UNIT_RESTRICTION.UNDEFINED)

    def _validateLevels(self, stats, state):
        if not stats.curTotalLevel:
            return (False, UNIT_RESTRICTION.ZERO_TOTAL_LEVEL)
        _, unit = self.__proxy.getUnit()
        if unit.isRated() or self._areVehiclesSelected(stats):
            if not state.isDevMode() and stats.curTotalLevel < stats.minTotalLevel:
                return (False, UNIT_RESTRICTION.MIN_TOTAL_LEVEL)
            if stats.curTotalLevel > stats.maxTotalLevel:
                return (False, UNIT_RESTRICTION.MAX_TOTAL_LEVEL)
        return (True, UNIT_RESTRICTION.UNDEFINED)
