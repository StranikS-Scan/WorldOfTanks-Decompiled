# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/TeamInfoWTPlasmaBonusComponentController.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import SoundGroups
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playPlasmaExtractorHunterVO
from gui.wt_event.wt_event_helpers import getBossType
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID

class TeamInfoWTPlasmaBonusComponentController(DynamicScriptComponent):
    _WT23_PLASMA_BOOST_START_SOUND_ID = 'ev_wt_gameplay_plasma_on'
    _WT23_PLASMA_BOOST_UI_SOUND_ID = 'ev_wt_ui_plasma_boost'

    def set_plasmaBonusPerVehicle(self, previousPlasmaCountDict=None):
        self.__updateGameModeSpecificStats(previousPlasmaCountDict)
        self.__notifyPlayersPlugin(previousPlasmaCountDict)

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
        if vehicle and vehicle.appearance and vehicle.appearance.engineAudition and vehicle.isAlive():
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
            if self.__isPlasmaBonusDecreased(vehicleID, previousPlasmaCountDict) and vehicle.health > 0:
                playPlasmaExtractorHunterVO()

    def __isPlasmaBonusChanged(self, vehicleID, previousPlasmaCountDict):
        return True if not previousPlasmaCountDict or vehicleID not in previousPlasmaCountDict or not self.plasmaBonusPerVehicle else previousPlasmaCountDict[vehicleID] != self.plasmaBonusPerVehicle[vehicleID]

    def __isPlasmaBonusDecreased(self, vehicleID, previousPlasmaCountDict):
        if vehicleID in previousPlasmaCountDict:
            if previousPlasmaCountDict[vehicleID] > self.plasmaBonusPerVehicle[vehicleID]:
                return True
        return False

    def set_bossPlasmaCounter(self, prevValue):
        if self.bossPlasmaCounter != prevValue:
            playerVehicle = avatar_getter.getPlayerVehicle()
            arenaDP = self.entity.sessionProvider.getArenaDP()
            for vInfo in arenaDP.getVehiclesInfoIterator():
                if getBossType(vInfo.vehicleType.tags):
                    ctrl = playerVehicle.guiSessionProvider.shared.feedback
                    ctrl.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_VEHICLE_PLASMA_ON_BOSS, vInfo.vehicleID, (self.bossPlasmaCounter,))
                    return
