# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: wt/scripts/client/PlasmaBonusComponentController.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import SoundGroups

class PlasmaBonusComponentController(DynamicScriptComponent):
    _WT23_PLASMA_BOOST_START_SOUND_ID = 'ev_wt_gameplay_plasma_on'
    _WT23_PLASMA_BOOST_UI_SOUND_ID = 'ev_wt_ui_plasma_boost'

    def set_plasmaBonusPerVehicle(self, previousPlasmaCountDict=None):
        self.__updateGameModeSpecificStats(previousPlasmaCountDict)
        self.__notifyPlayersPlugin(previousPlasmaCountDict)

    def getPlasmaBonusForVehicle(self, vehicleID):
        return self.plasmaBonusPerVehicle[vehicleID] if vehicleID in self.plasmaBonusPerVehicle else 0

    def getPlasmaBonusMultiplier(self, plasmaBonus):
        return (self.plasmaBonusLevelMultipliers[plasmaBonus] - 1) * 100

    def _onAvatarReady(self):
        self.__updateGameModeSpecificStats(self.plasmaBonusPerVehicle)

    def __updateGameModeSpecificStats(self, previousPlasmaCountDict):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {}
        for vehID in self.plasmaBonusPerVehicle:
            plasmaBonus = self.plasmaBonusPerVehicle.get(vehID, 0)
            gameModeStats[vehID] = {EventKeys.PLASMA_COUNT.value: plasmaBonus}
            if plasmaBonus == 1:
                self.__playSoundIDOnVehicle(vehID)

        arena.onGameModeSpecificStats(True, gameModeStats)

    def __playSoundIDOnVehicle(self, vehID):
        vehicle = BigWorld.entities.get(vehID)
        if vehicle and vehicle.appearance and vehicle.isAlive():
            soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
            if soundObject:
                soundObject.play(self._WT23_PLASMA_BOOST_START_SOUND_ID)

    def __notifyPlayersPlugin(self, previousPlasmaCountDict):
        vehicle = avatar_getter.getPlayerVehicle()
        vehicleID = avatar_getter.getPlayerVehicleID()
        if not vehicle:
            return
        ctrl = vehicle.guiSessionProvider.shared.vehicleState
        if vehicleID in self.plasmaBonusPerVehicle and ctrl:
            ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.PLASMA, (self.plasmaBonusPerVehicle[vehicleID], self.plasmaBonusLevelMultipliers[self.plasmaBonusPerVehicle[vehicleID]]))
            if self.__isPlasmaBonusChanged(vehicleID, previousPlasmaCountDict):
                SoundGroups.g_instance.playSound2D(self._WT23_PLASMA_BOOST_UI_SOUND_ID)

    def __isPlasmaBonusChanged(self, vehicleID, previousPlasmaCountDict):
        return True if not previousPlasmaCountDict or vehicleID not in previousPlasmaCountDict or not self.plasmaBonusPerVehicle else previousPlasmaCountDict[vehicleID] != self.plasmaBonusPerVehicle[vehicleID]
