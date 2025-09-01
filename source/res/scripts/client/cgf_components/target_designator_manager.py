# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/target_designator_manager.py
import BigWorld
import CGF
import SoundGroups
from cgf_script.managers_registrator import autoregister
from chat_commands_consts import LocationMarkerSubType
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.controllers.vehicle_passenger import VehiclePassengerInfoWatcher
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

@autoregister(presentInAllWorlds=True)
class TargetDesignatorSoundManager(CGF.ComponentManager, VehiclePassengerInfoWatcher):
    _SOUND_SPOTTED_VEHICLE_HIT_PC = 'gui_abl_tda_spotted'
    _SOUND_UNSPOTTED_VEHICLE_HIT_PC = 'gui_abl_tda_blindshot'
    _SOUND3D_UNSPOTTED_VEHICLE_HIT = 'gui_abl_tda_marker'
    _SOUND3D_SPOTTED_VEHICLE_HIT = 'gui_abl_tda_enemy_spotted'
    _STATE_VEHICLE_HIT_PC_GROUP = 'STATE_ext_abl_tda'
    _STATE_VEHICLE_HIT_PC_GROUP_ON = 'STATE_ext_abl_tda_on'
    _STATE_VEHICLE_HIT_PC_GROUP_OFF = 'STATE_ext_abl_tda_off'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TargetDesignatorSoundManager, self).__init__()
        self.__markers = None
        self.__currentVehicle = None
        return

    def activate(self):
        self.__markers = set()
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__onStaticMarkerAdded
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        self.startVehiclePassengerLateListening(self.__onVehiclePassengerUpdate, self.__onVehiclePassengerUpdating)
        return

    def deactivate(self):
        self.__markers = None
        self.__currentVehicle = None
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__onStaticMarkerAdded
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        self.stopVehiclePassengerListening(self.__onVehiclePassengerUpdate, self.__onVehiclePassengerUpdating)
        return

    def __onStaticMarkerAdded(self, _, __, position, locationMarkerSubtype, *___):
        if locationMarkerSubtype == LocationMarkerSubType.TARGET_DESIGNATOR_UNSPOTTED_MARKER_HIT:
            self.__play3DSound(self._SOUND3D_UNSPOTTED_VEHICLE_HIT, position)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.TARGET_DESIGNATOR_SPOTTED_MARKER:
            if value.hasUnspottedIndicator:
                if vehicleID == self.__currentVehicle.id:
                    self.__playGlobalSound(self._SOUND_UNSPOTTED_VEHICLE_HIT_PC)
            else:
                marker = value.spottedMarker
                if marker is not None and vehicleID not in self.__markers:
                    self.__markers.add(vehicleID)
                    targetVehicle = BigWorld.entities.get(vehicleID)
                    if vehicleID == self.__currentVehicle.id:
                        self.__playGlobalSound(self._SOUND_SPOTTED_VEHICLE_HIT_PC)
                        self.__setGlobalState(self._STATE_VEHICLE_HIT_PC_GROUP, self._STATE_VEHICLE_HIT_PC_GROUP_ON)
                    elif self.__isEnemyVehicle(targetVehicle):
                        self.__play3DSound(self._SOUND3D_SPOTTED_VEHICLE_HIT, targetVehicle.position)
                elif marker is None and vehicleID in self.__markers:
                    self.__markers.remove(vehicleID)
                    if vehicleID == self.__currentVehicle.id:
                        self.__setGlobalState(self._STATE_VEHICLE_HIT_PC_GROUP, self._STATE_VEHICLE_HIT_PC_GROUP_OFF)
        return

    def __onVehiclePassengerUpdating(self, _):
        if self.__currentVehicle is not None and self.__currentVehicle.id in self.__markers:
            self.__setGlobalState(self._STATE_VEHICLE_HIT_PC_GROUP, self._STATE_VEHICLE_HIT_PC_GROUP_OFF)
        return

    def __onVehiclePassengerUpdate(self, vehicle):
        self.__currentVehicle = vehicle
        if self.__currentVehicle is not None and self.__currentVehicle.id in self.__markers:
            self.__setGlobalState(self._STATE_VEHICLE_HIT_PC_GROUP, self._STATE_VEHICLE_HIT_PC_GROUP_ON)
        return

    def __isEnemyVehicle(self, vehicle):
        return False if vehicle is None or self.__currentVehicle is None else vehicle.publicInfo.team != self.__currentVehicle.publicInfo.team

    @classmethod
    def __playGlobalSound(cls, eventName):
        SoundGroups.g_instance.playSound2D(eventName)

    @classmethod
    def __play3DSound(cls, eventName, position):
        SoundGroups.g_instance.playSoundPos(eventName, position)

    @classmethod
    def __setGlobalState(cls, stateGroup, stateName):
        SoundGroups.g_instance.setState(stateGroup, stateName)
