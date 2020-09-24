# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/vehicle_blocks.py
from block import Block, Meta, SLOT_TYPE

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


class IsVehicleBurning(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(IsVehicleBurning, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._exec)

    def _exec(self):
        v = self._vehicle.getValue()
        extra = v.typeDescriptor.extrasDict['fire']
        res = extra is not None and extra.getStatus(v) != (0, 0)
        self._res.setValue(res)
        return
