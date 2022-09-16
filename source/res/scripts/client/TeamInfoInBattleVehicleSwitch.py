# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamInfoInBattleVehicleSwitch.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import VehicleSelectionPlayerStatus
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from script_component.ScriptComponent import ScriptComponent

class TeamInfoInBattleVehicleSwitch(ScriptComponent):
    REQUIRED_BONUS_CAP = ARENA_BONUS_TYPE_CAPS.VEHICLE_IN_BATTLE_SELECTION
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TeamInfoInBattleVehicleSwitch, self).__init__()
        self.__positionsSet = False

    def _onAvatarReady(self):
        if not self.__positionsSet:
            self.__setPositions()
        self.__updateStatuses(self.statuses)

    def set_positions(self, _):
        if self._isAvatarReady:
            self.__setPositions()

    def set_statuses(self, prevValues):
        if not self._isAvatarReady:
            return
        updatedStatuses = self.__getNewValues(prevValues, self.statuses)
        if updatedStatuses:
            self.__updateStatuses(updatedStatuses)

    def checkVehicleConfirmation(self, vehicleID):
        return self.statuses.get(vehicleID) == VehicleSelectionPlayerStatus.CONFIRMED

    def __setPositions(self):
        if self.positions:
            self.__positionsSet = True
            ctrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
            if ctrl is not None:
                ctrl.updateSpawnPoints(self.positions)
        return

    def __updateStatuses(self, statuses):
        ctrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if ctrl is not None:
            ctrl.updateConfirmationStatuses(statuses)
        return

    @staticmethod
    def __getNewValues(prevValues, newValues):
        updatedValues = {}
        for vehId, value in newValues.iteritems():
            if vehId not in prevValues or prevValues[vehId] != value:
                updatedValues[vehId] = value

        return updatedValues
