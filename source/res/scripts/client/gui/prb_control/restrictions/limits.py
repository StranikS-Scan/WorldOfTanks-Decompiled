# Embedded file name: scripts/client/gui/prb_control/restrictions/limits.py
from collections import defaultdict
import weakref
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_ACCOUNT_STATE, PREBATTLE_TYPE
from gui.prb_control import getClassLevelLimits, getTotalLevelLimits
from gui.prb_control import getPrebattleRosters, getMaxSizeLimits
from gui.prb_control.restrictions.interfaces import IVehicleLimit, ITeamLimit
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_RESTRICTION
from gui.shared.ItemsCache import g_itemsCache
from items import vehicles
from items.vehicles import VehicleDescr, VEHICLE_CLASS_TAGS
from prebattle_shared import isTeamValid, isVehicleValid

class VehicleIsValid(IVehicleLimit):

    def check(self, teamLimits):
        if not g_currentVehicle.isReadyToFight():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_READY)
        vehicle = g_currentVehicle.item
        if vehicle.isOnlyForEventBattles:
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        shellsList = []
        for shell in vehicle.shells:
            shellsList.extend([shell.intCD, shell.count])

        return isVehicleValid(vehicle.descriptor, shellsList, teamLimits)


class VehicleIsValidForSquad(IVehicleLimit):

    def check(self, teamLimits):
        if not g_currentVehicle.isReadyToFight():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_READY)
        vehicle = g_currentVehicle.item
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

    def __isAllObservers(self, accountsInfo):
        if len(accountsInfo) == 0:
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
        super(SquadLimits, self).__init__(functional, (VehicleIsValidForSquad(),), (TeamIsValid(),))


class TrainingLimits(LimitsCollection):

    def __init__(self, functional):
        super(TrainingLimits, self).__init__(functional, (VehicleIsValid(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.TRAINING), TeamIsValid(), ObserverInTeamIsValid()))


class CompanyLimits(LimitsCollection):

    def __init__(self, functional):
        super(CompanyLimits, self).__init__(functional, (VehicleIsValid(),), (VehiclesLevelLimit(), TeamIsValid()))


class BattleSessionLimits(LimitsCollection):

    def __init__(self, functional):
        super(BattleSessionLimits, self).__init__(functional, (VehicleIsValid(),), (VehiclesLevelLimit(), TeamIsValid()))
