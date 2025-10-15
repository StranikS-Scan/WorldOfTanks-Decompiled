# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalVehicleChangeShotComponent.py
import logging
import BigWorld
import Event
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from DynamicVehicleChangeComponent import DynamicVehicleChangeComponent
from portal.sounds.sound_helpers import playVoiceover
from portal.sounds.sound_constants import PortalAbilityVoiceovers
from portal.gui.portal_event_helpers import useFadingBinocular, PortalBinocularsMode
from portal_common.portal_constants import DynamicVehicleChangeShotStates as changeShotStates
from typing import Optional
_logger = logging.getLogger(__name__)

class PortalVehicleChangeShotComponent(DynamicScriptComponent):
    onControlStarted = Event.Event()

    def __init__(self):
        super(PortalVehicleChangeShotComponent, self).__init__()
        if self.vehicleChangeComponent:
            self.vehicleChangeComponent.onStartVehicleControl += self.__onStartVehicleControlPC
            self.vehicleChangeComponent.onStopVehicleControl += self.__onStopVehicleControlPC

    def onDestroy(self):
        if self.vehicleChangeComponent:
            self.vehicleChangeComponent.onStartVehicleControl -= self.__onStartVehicleControlPC
            self.vehicleChangeComponent.onStopVehicleControl -= self.__onStopVehicleControlPC
        binoculars = BigWorld.binoculars()
        if binoculars and self.entity.avatarID == BigWorld.player().id:
            binoculars.setIsPossession(False)
        super(PortalVehicleChangeShotComponent, self).onDestroy()

    @property
    def vehicleChangeComponent(self):
        return BigWorld.player().DynamicVehicleChangeComponent if self.entity.avatarID == BigWorld.player().id else None

    def set_vehicleChangeShotState(self, prev):
        if self.vehicleChangeShotState == changeShotStates.BEFORE_SHOT:
            self.__onShotPrepared()
        elif self.vehicleChangeShotState == changeShotStates.AFTER_SHOT:
            self.__onShotPerformed()
        elif prev == changeShotStates.BEFORE_SHOT and self.vehicleChangeShotState == changeShotStates.INACTIVE:
            self.__onShotCanceled()
        elif self.vehicleChangeShotState == changeShotStates.ACTIVE:
            self.__onControlStarted()

    def __onShotPrepared(self):
        pass

    def __onShotPerformed(self):
        pass

    def __onShotCanceled(self):
        pass

    def __onControlStarted(self):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        self.onControlStarted(self.entity.avatarID, equipment.duration)

    def __onStartVehicleControlPC(self, newVehicleID):
        playVoiceover(PortalAbilityVoiceovers.CHANGE_SHOT_ENTERING_VOICEOVER)
        self.__toggleBinocular()

    def __onStopVehicleControlPC(self, isInterrupted):
        playVoiceover(PortalAbilityVoiceovers.CHANGE_SHOT_EVICTION_VOICEOVER)
        self.__toggleBinocular()

    @useFadingBinocular(PortalBinocularsMode.VEHICLE_CHANGE)
    def __toggleBinocular(self):
        pass
