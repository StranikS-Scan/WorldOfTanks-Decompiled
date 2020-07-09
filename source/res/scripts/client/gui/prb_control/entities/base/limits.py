# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/limits.py
from collections import defaultdict
import weakref
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_ACCOUNT_STATE
from gui.prb_control import prb_getters
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_RESTRICTION
from items.vehicles import VehicleDescr, VEHICLE_CLASS_TAGS
from prebattle_shared import isTeamValid, isVehicleValid

class IVehicleLimit(object):

    def check(self, teamLimits):
        return (True, '')


class ITeamLimit(object):

    def check(self, rosters, team, teamLimits):
        return (True, '')


class VehicleIsValid(IVehicleLimit):

    def check(self, teamLimits):
        if not g_currentVehicle.isPresent():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
        if g_currentVehicle.isEvent():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        if g_currentVehicle.isOnlyForEpicBattles():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_EPIC_ONLY)
        if g_currentVehicle.isOnlyForBob():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_BOB_ONLY)
        if g_currentVehicle.isRotationGroupLocked():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_ROTATION_GROUP_LOCKED)
        if not g_currentVehicle.isReadyToPrebattle():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_READY)
        if g_currentVehicle.isUnsuitableToQueue():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        vehicle = g_currentVehicle.item
        shellsList = []
        for shell in vehicle.shells:
            shellsList.extend([shell.intCD, shell.count])

        return isVehicleValid(vehicle.descriptor, shellsList, teamLimits)


class AbstractTeamIsValid(ITeamLimit):

    def _getAccountsInfo(self, rosters, team):
        rosterKey = None
        if team == 1:
            rosterKey = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1
        elif team == 2:
            rosterKey = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2
        if rosterKey in rosters:
            accountsInfo = rosters[rosterKey]
        else:
            accountsInfo = {}
        return accountsInfo


class TeamIsValid(AbstractTeamIsValid):

    def check(self, rosters, team, teamLimits):
        return isTeamValid(self._getAccountsInfo(rosters, team), teamLimits)


class TeamNoPlayersInBattle(ITeamLimit):

    def __init__(self, prbType):
        super(TeamNoPlayersInBattle, self).__init__()
        self.__range = PREBATTLE_ROSTER.getRange(prbType)

    def check(self, rosters, team, teamLimits):
        for rosterKey in self.__range:
            if rosterKey & team and rosterKey in rosters:
                filtered = filter(self.__isPlayerInBattle, rosters[rosterKey].itervalues())
                if filtered:
                    return (False, PREBATTLE_RESTRICTION.HAS_PLAYER_IN_BATTLE)

        return (True, '')

    def __isPlayerInBattle(self, player):
        return player['state'] & PREBATTLE_ACCOUNT_STATE.IN_BATTLE != 0


class MaxCount(ITeamLimit):

    def __init__(self, assigned=True):
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
        maxCount = prb_getters.getMaxSizeLimits(teamLimits)[index]
        return (False, PREBATTLE_RESTRICTION.LIMIT_MAX_COUNT) if key in rosters and len(rosters[key]) >= maxCount else (True, '')


class TotalMaxCount(ITeamLimit):

    def check(self, rosters, team, teamLimits):
        maxCount = sum(prb_getters.getMaxSizeLimits(teamLimits))
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
            minLevel, maxLevel = prb_getters.getClassLevelLimits(teamLimits, classTag)
            currentLevel = classLevels[classTag]
            vClassTags = PREBATTLE_RESTRICTION.getVehClassTags()
            if not (minLevel <= currentLevel <= maxLevel or currentLevel == 0):
                isValid = False
                if classTag in vClassTags:
                    notValidReason = vClassTags[classTag]
                else:
                    notValidReason = PREBATTLE_RESTRICTION.LIMIT_CLASSES

        if isValid:
            minLevel, maxLevel = prb_getters.getTotalLevelLimits(teamLimits)
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
            if vehCompDescr:
                vehType = VehicleDescr(compactDescr=vehCompDescr).type
                level = vehType.level
                union = vehClassTags & vehType.tags
                if union:
                    vehClass = union.pop()
                    classLevels[vehClass] = max(classLevels[vehClass], level)
                totalLevel += level

        return (totalLevel, classLevels)


class LimitsCollection(object):

    def __init__(self, entity, vehicleLimits, teamLimits):
        self.__entity = weakref.proxy(entity)
        self.__vehicleLimits = vehicleLimits
        self.__teamLimits = teamLimits

    def clear(self):
        self.__entity = None
        self.__vehicleLimits = ()
        self.__teamLimits = ()
        return

    def isVehicleValid(self):
        settings = self.__entity.getSettings()
        teamLimits = settings.getTeamLimits(self.__entity.getPlayerTeam())
        for limit in self.__vehicleLimits:
            result, errorCode = limit.check(teamLimits)
            if not result:
                return ValidationResult(result, errorCode)

    def isTeamValid(self, team=None):
        if team is None:
            team = self.__entity.getPlayerTeam()
        settings = self.__entity.getSettings()
        teamLimits = settings.getTeamLimits(team)
        rosters = prb_getters.getPrebattleRosters()
        for limit in self.__teamLimits:
            result, errorCode = limit.check(rosters, team, teamLimits)
            if not result:
                return ValidationResult(result, errorCode)

        return

    def isTeamsValid(self):
        settings = self.__entity.getSettings()
        rosters = prb_getters.getPrebattleRosters()
        for team in [1, 2]:
            teamLimits = settings.getTeamLimits(team)
            for limit in self.__teamLimits:
                result, errorCode = limit.check(rosters, team, teamLimits)
                if not result:
                    return ValidationResult(result, errorCode)

    def isMaxCountValid(self, team, assigned):
        settings = self.__entity.getSettings()
        rosters = prb_getters.getPrebattleRosters()
        result, errorCode = MaxCount(assigned=assigned).check(rosters, team, settings.getTeamLimits(team))
        return ValidationResult(result, errorCode) if not result else None

    def _getEntity(self):
        return self.__entity
