# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_blocks.py
import BigWorld
from visual_script.block import Block, SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from visual_script.vehicle_blocks import VehicleMeta
from visual_script.dependency import dependencyImporter
vehicles, helpers = dependencyImporter('items.vehicles', 'helpers')

class _ExtraDummy(object):

    @staticmethod
    def getDamageLevel(*args, **kwargs):
        pass


def _getPartNames(originalPartName):
    edgeCases = {'track': ('leftTrack', 'rightTrack'),
     'radioman': ('radioman1', 'radioman2'),
     'gunner': ('gunner1', 'gunner2'),
     'loader': ('loader1', 'loader2'),
     'wheel': ('wheel0', 'wheel1', 'wheel2', 'wheel3', 'wheel4', 'wheel5', 'wheel6', 'wheel7')}
    return edgeCases.get(originalPartName, (originalPartName,))


def _getPartState(originalPartName):
    available = _getPartNames(originalPartName)
    deviceStates = BigWorld.player().deviceStates
    states = [ deviceStates.get(name, 'normal') for name in available ]
    if 'destroyed' in states:
        return 2
    return 1 if 'critical' in states else 0


class PlayerVehicleDeviceState(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(PlayerVehicleDeviceState, self).__init__(*args, **kwargs)
        self._device = self._makeDataInputSlot('device', SLOT_TYPE.E_VEHICLE_DEVICE)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.E_MODULE_STATE, self._execState)
        self._hasDevice = self._makeDataOutputSlot('hasDevice', SLOT_TYPE.BOOL, self._execHasDevice)

    def _execState(self):
        if helpers.isPlayerAvatar():
            deviceIdx = self._device.getValue()
            if deviceIdx >= len(vehicles.VEHICLE_DEVICE_TYPE_NAMES):
                errorVScript(self, 'unknown device identifier.')
                return
            state = _getPartState(vehicles.VEHICLE_DEVICE_TYPE_NAMES[deviceIdx])
            self._state.setValue(state)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    def _execHasDevice(self):
        if helpers.isPlayerAvatar():
            deviceIdx = self._device.getValue()
            if deviceIdx >= len(vehicles.VEHICLE_DEVICE_TYPE_NAMES):
                errorVScript(self, 'unknown device identifier.')
                return
            deviceNames = [ pn + 'Health' for pn in _getPartNames(vehicles.VEHICLE_DEVICE_TYPE_NAMES[deviceIdx]) ]
            isHas = any((te.name in deviceNames for te in BigWorld.player().vehicleTypeDescriptor.type.devices))
            self._hasDevice.setValue(isHas)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class PlayerVehicleTankmanState(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(PlayerVehicleTankmanState, self).__init__(*args, **kwargs)
        self._tankman = self._makeDataInputSlot('tankman', SLOT_TYPE.E_VEHICLE_TANKMAN)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.E_MODULE_STATE, self._execState)
        self._hasTankman = self._makeDataOutputSlot('hasTankman', SLOT_TYPE.BOOL, self._execHasTankman)

    def _execState(self):
        if helpers.isPlayerAvatar():
            tankmanIdx = self._tankman.getValue()
            if tankmanIdx >= len(vehicles.VEHICLE_TANKMAN_TYPE_NAMES):
                errorVScript(self, 'unknown tankman identifier.')
                return
            state = _getPartState(vehicles.VEHICLE_TANKMAN_TYPE_NAMES[tankmanIdx])
            self._state.setValue(state)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    def _execHasTankman(self):
        if helpers.isPlayerAvatar():
            tankmanIdx = self._tankman.getValue()
            if tankmanIdx >= len(vehicles.VEHICLE_TANKMAN_TYPE_NAMES):
                errorVScript(self, 'unknown tankman identifier.')
                return
            tankmanName = [ pn + 'Health' for pn in _getPartNames(vehicles.VEHICLE_TANKMAN_TYPE_NAMES[tankmanIdx]) ]
            isHas = any((te.name in tankmanName for te in BigWorld.player().vehicleTypeDescriptor.type.tankmen))
            self._hasTankman.setValue(isHas)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
