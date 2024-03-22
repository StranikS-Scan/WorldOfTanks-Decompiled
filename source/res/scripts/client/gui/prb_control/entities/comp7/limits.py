# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/comp7/limits.py
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, ROLE_TYPE, PREBATTLE_TYPE
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.limits import ITeamLimit, TeamNoPlayersInBattle, TeamIsValid, TeamAllPlayersReady, LimitsCollection
from gui.prb_control.entities.training.legacy.limits import TrainingVehicleIsValid, ObserverInTeamIsValid
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_RESTRICTION
from items.vehicles import getVehicleType

class MaxPlayersNumber(ITeamLimit):

    def check(self, rosters, team, teamLimits):
        teamRosterIndex = PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 if team == 1 else PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2
        if teamRosterIndex not in rosters:
            return (True, '')
        teamInfo = rosters[teamRosterIndex]
        totalPlayerNumber = prb_getters.getMaxSizeLimits(teamLimits)[0]
        observersNumber, playersNumber = self.__getPlayerRolesNumber(teamInfo)
        if observersNumber + playersNumber > totalPlayerNumber:
            return (False, PREBATTLE_RESTRICTION.LIMIT_MAX_COUNT)
        if observersNumber > PREBATTLE_MAX_OBSERVERS_IN_TEAM:
            return (False, PREBATTLE_RESTRICTION.LIMIT_MAX_OBSERVERS)
        maxPlayersNumber = totalPlayerNumber - PREBATTLE_MAX_OBSERVERS_IN_TEAM
        return (False, PREBATTLE_RESTRICTION.LIMIT_MAX_COUNT) if playersNumber > maxPlayersNumber else (True, '')

    def __getPlayerRolesNumber(self, teamInfo):
        observersNumber = 0
        playersNumber = 0
        for playerInfo in teamInfo.itervalues():
            vehicleType = getVehicleType(playerInfo['vehCompDescr'])
            isObserver = vehicleType.role == ROLE_TYPE.NOT_DEFINED
            if isObserver:
                observersNumber += 1
            playersNumber += 1

        return (observersNumber, playersNumber)


class Comp7TrainingLimits(LimitsCollection):

    def __init__(self, entity):
        super(Comp7TrainingLimits, self).__init__(entity, (TrainingVehicleIsValid(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.TRAINING),
         TeamIsValid(),
         ObserverInTeamIsValid(),
         TeamAllPlayersReady(),
         MaxPlayersNumber()))
