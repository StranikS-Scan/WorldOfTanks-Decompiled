# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInBattleVehicleSwitch.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from helpers import dependency
from script_component.ScriptComponent import ScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class AvatarInBattleVehicleSwitch(ScriptComponent):
    REQUIRED_BONUS_CAP = ARENA_BONUS_TYPE_CAPS.VEHICLE_IN_BATTLE_SELECTION
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_vehicleSpawnList(self, _):
        if self._isAvatarReady:
            self.__updateAllVehsList()

    def set_spawnInfoForVehicle(self, _):
        if self._isAvatarReady:
            self.__updateCurrentVehicle()

    def confirmSelection(self):
        self.cell.confirmVehicleSelection()

    def chooseVehicle(self, newCD):
        self.cell.chooseVehicle(newCD)

    def switchSetup(self, vehTypeCD, groupId, layoutIdx):
        if groupId in self.spawnInfoForVehicle['vehDisabledSetupSwitches']:
            return
        self.cell.switchSetup(vehTypeCD, groupId, layoutIdx)

    def _onAvatarReady(self):
        self.__updateAllVehsList()
        if self.spawnInfoForVehicle:
            self.__updateCurrentVehicle()

    def __updateAllVehsList(self):
        self.__sessionProvider.dynamic.comp7PrebattleSetup.setAvailableVehicles(self.vehicleSpawnList)

    def __updateCurrentVehicle(self):
        self.__sessionProvider.dynamic.comp7PrebattleSetup.updateVehicleInfo(self.spawnInfoForVehicle)
