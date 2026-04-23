# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/entities/limits.py
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, ROLE_TYPE, PREBATTLE_TYPE
from gui.prb_control import prb_getters
from helpers import dependency
from gui.prb_control.entities.base.limits import ITeamLimit, TeamNoPlayersInBattle, TeamIsValid, TeamAllPlayersReady, LimitsCollection
from gui.prb_control.entities.training.legacy.limits import TrainingVehicleIsValid, ObserverInTeamIsValid
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_RESTRICTION
from items.vehicles import getVehicleType
from skeletons.gui.game_control import IComp7Controller

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


class Comp7TrainingVehicleLimits(TrainingVehicleIsValid):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def check(self, teamLimits):
        if not g_currentVehicle.isPresent():
            return (False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
        if not self.__comp7Controller.hasEnoughReadyToFightVehicles():
            return (False, PREBATTLE_RESTRICTION.LIMIT_NOT_ENOUGH_SUITABLE_VEHICLES)
        isValid, restriction = super(Comp7TrainingVehicleLimits, self).check(teamLimits)
        return (isValid, restriction)


class Comp7TrainingLimits(LimitsCollection):

    def __init__(self, entity):
        super(Comp7TrainingLimits, self).__init__(entity, (Comp7TrainingVehicleLimits(),), (TeamNoPlayersInBattle(PREBATTLE_TYPE.TRAINING),
         TeamIsValid(),
         ObserverInTeamIsValid(),
         TeamAllPlayersReady(),
         MaxPlayersNumber()))
