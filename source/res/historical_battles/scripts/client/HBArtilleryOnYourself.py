# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBArtilleryOnYourself.py
import typing
import BigWorld
from Math import Vector3
from gui.battle_control import avatar_getter
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles as vehs_core
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from HBVehicleAbilityTimerComponent import HBVehicleAbilityTimerComponent
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class GroundMarker(CallbackDelayer):
    _DEFAULT_STRIKE_DIRECTION = Vector3(1, 0, 0)

    def __init__(self, entity, equipment):
        CallbackDelayer.__init__(self)
        self.__entity = entity
        self.area = BigWorld.player().createEquipmentSelectedArea(self.__entity.position, self._DEFAULT_STRIKE_DIRECTION, equipment, areaVisual=equipment.preparingAreaVisual)
        self.area.setOverTerrainOffset(10.0)
        self.area.setGUIVisible(True)

    def destroy(self):
        super(GroundMarker, self).destroy()
        if self.area is not None:
            self.area.destroy()
            self.area = None
        return


class HBArtilleryOnYourself(HBVehicleAbilityTimerComponent):
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.HB_ARTILLERY_ON_YOURSELF

    def __init__(self):
        super(HBArtilleryOnYourself, self).__init__(self.__TIMER_VIEW_ID)
        avatar = BigWorld.player()
        if self.equipmentID > 0 and avatar.vehicle == self.vehicle:
            equipment = vehs_core.g_cache.equipments()[self.equipmentID]
            self.__equipmentCD = equipment.compactDescr
            self.__marker = GroundMarker(self.entity, equipment)
        else:
            self.__marker = None
            self.__equipmentCD = None
            self.__onActivatedNPC()
        return

    @property
    def vehicle(self):
        return self.entity

    def _updateTimer(self, data):
        data['isActive'] = self.entity.id == BigWorld.player().getObservedVehicleID() and data['duration'] > 0
        data['endTime'] = self.finishTime if data['isActive'] else 0.0
        super(HBArtilleryOnYourself, self)._updateTimer(data)

    def __clear(self):
        if self.__marker:
            self.__marker.destroy()
            self.__marker = None
            self.__equipmentCD = None
        return

    def _destroy(self):
        self.__clear()
        super(HBArtilleryOnYourself, self)._destroy()

    def __onActivatedNPC(self):
        equipment = vehs_core.g_cache.equipments()[self.equipmentID]
        activationSoundNPC = equipment.wwsoundEquipmentUsedNPC
        avatar_getter.getSoundNotifications().play(activationSoundNPC)
