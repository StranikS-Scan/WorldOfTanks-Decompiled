# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/vehicle_blocks.py
from block import Block, Meta
from constants import NULL_ENTITY_ID
from slot_types import SLOT_TYPE
from visual_script.misc import errorVScript
import items.vehicles as vehicles

class VehicleMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class VehicleEventsMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class GetVehicleId(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleId, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._res = self._makeDataOutputSlot('id', SLOT_TYPE.INT, self._exec)

    def _exec(self):
        vehicle = self._vehicle.getValue()
        try:
            self._res.setValue(vehicle.id)
        except (AttributeError, ReferenceError):
            errorVScript(self, 'Dead weakref')
            self._res.setValue(NULL_ENTITY_ID)
