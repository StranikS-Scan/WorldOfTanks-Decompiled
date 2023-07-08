# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/vehicle_view_states.py
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.vehicle_view_states import SelectedViewState

class FunRandomVehicleViewState(SelectedViewState, FunSubModesWatcher):

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        return vehicle.item.isOnlyForFunRandomBattles

    def setEliteShown(self, eliteShown):
        self._isEliteShown = eliteShown

    def setLevelShown(self, levelShown):
        self._isLevelShown = levelShown

    def setRoleShown(self, roleShown):
        self._isRoleShown = roleShown

    def isCustomizationVisible(self):
        return not self._isOutfitLocked

    def _resolveVehicleState(self, vehicle):
        super(FunRandomVehicleViewState, self)._resolveVehicleState(vehicle)
        self._isMaintenanceVisible = vehicle.item.typeDescr.repairCost > 0
        self.__resolveStateByCurrentSubMode()

    @hasDesiredSubMode()
    def __resolveStateByCurrentSubMode(self):
        self.getDesiredSubMode().resolveVehicleViewState(self)
