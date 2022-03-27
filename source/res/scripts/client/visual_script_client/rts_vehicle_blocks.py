# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/rts_vehicle_blocks.py
import weakref
import BigWorld
from constants import IS_VS_EDITOR
from visual_script.block import Block
from visual_script.misc import errorVScript
from visual_script.slot_types import SLOT_TYPE
from visual_script_client.vehicle_blocks import VehicleMeta
if not IS_VS_EDITOR:
    from constants import ARENA_PERIOD
    from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
    import helpers
    from helpers import dependency, isPlayerAvatar
    from skeletons.gui.battle_session import IBattleSessionProvider

class SetRTSVehicleControl(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(SetRTSVehicleControl, self).__init__(*args, **kwargs)
        self._inSlot = self._makeEventInputSlot('in', self._in)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._isEnabled = self._makeDataInputSlot('isControlEnabled', SLOT_TYPE.BOOL)
        self._outSlot = self._makeEventOutputSlot('out')

    @property
    def _avatar(self):
        if helpers.isPlayerAvatar():
            return BigWorld.player()
        errorVScript(self, 'BigWorld.player is not player avatar.')

    def _in(self):
        if not IS_VS_EDITOR:
            self._execute()
        self._outSlot.call()

    def _execute(self):
        vehicle = self._vehicle.getValue()
        if vehicle is None:
            errorVScript(self, 'Vehicle is None')
            return
        else:
            player = self._avatar
            if player is None:
                return
            if player.arena.period not in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE):
                errorVScript(self, 'Wrong arena period. Only Prebattle or Battle is supported.')
                return
            if not ARENA_BONUS_TYPE_CAPS.checkAny(player.arena.bonusType, ARENA_BONUS_TYPE_CAPS.RTS_COMPONENT):
                errorVScript(self, 'Wrong game mode. Only modes with RTS_COMPONENT supported.')
                return
            sessionProvider = dependency.instance(IBattleSessionProvider)
            vehicles = sessionProvider.dynamic.rtsCommander.vehicles
            if self._isEnabled.getValue():
                vehicles.enableVehicle(vehicle.id)
            else:
                vehicles.disableVehicle(vehicle.id)
            return


class GetRTSVehicleControl(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetRTSVehicleControl, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._isEnabledSlot = self._makeDataOutputSlot('isControlEnabled', SLOT_TYPE.BOOL, self._isEnabled)

    def _isEnabled(self):
        vehicle = self._vehicle.getValue()
        if not IS_VS_EDITOR and vehicle is not None:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            proxy = sessionProvider.dynamic.rtsCommander.vehicles.get(vehicle.id)
            self._isEnabled.setValue(proxy is not None and not proxy.isDisabled)
        self._isEnabled.setValue(False)
        return


class GetRTSCommanderVehicle(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetRTSCommanderVehicle, self).__init__(*args, **kwargs)
        self._team = self._makeDataInputSlot('team', SLOT_TYPE.INT)
        self._slot = self._makeDataInputSlot('slot', SLOT_TYPE.INT)
        self._vehicle = self._makeDataOutputSlot('vehicle', SLOT_TYPE.VEHICLE, self._execute)

    def validate(self):
        if not self._team.hasValue():
            return 'Team ID is required'
        return 'Slot number is required' if not self._slot.hasValue() else super(GetRTSCommanderVehicle, self).validate()

    def _execute(self):
        if not IS_VS_EDITOR and isPlayerAvatar():
            avatar = BigWorld.player()
            for vehicle in avatar.vehicles:
                if vehicle.publicInfo.team == self._team.getValue() and vehicle.slot == self._slot.getValue():
                    self._setVehicle(vehicle)
                    break

    def _setVehicle(self, vehicle):
        if type(vehicle).__name__ != 'weakproxy':
            vehicle = weakref.proxy(vehicle)
        self._vehicle.setValue(vehicle)
