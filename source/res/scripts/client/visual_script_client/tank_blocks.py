# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/tank_blocks.py
import BigWorld
from dependency import editorValue
from visual_script.component import Component, OutputSlot, SLOT_TYPE, ASPECT

class VehicleSpeed(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.FLOAT, VehicleSpeed._execute)]

    @editorValue(0)
    def _execute(self):
        vehicle = BigWorld.player().vehicle
        return BigWorld.player().vehicle.getSpeed() if vehicle is not None else 0

    def captionText(self):
        pass


def _defineMaxVehicleSpeed():
    vehicle = BigWorld.player().vehicle
    if vehicle is not None:
        typeDescriptor = BigWorld.player().vehicle.typeDescriptor
        defaultVehicleCfg = typeDescriptor.type.xphysics['engines'][typeDescriptor.engine.name]
        return defaultVehicleCfg['smplFwMaxSpeed']
    else:
        return


class VehicleMaxSpeed(Component):

    def __init__(self):
        super(VehicleMaxSpeed, self).__init__()
        self.__vehicleMaxSpeed = None
        return

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.FLOAT, VehicleMaxSpeed._execute)]

    @editorValue(0)
    def _execute(self):
        if self.__vehicleMaxSpeed is None:
            self.__vehicleMaxSpeed = _defineMaxVehicleSpeed()
        return self.__vehicleMaxSpeed or 0

    def captionText(self):
        pass


class VehicleMaxSpeedAtBoost(Component):

    def __init__(self):
        super(VehicleMaxSpeedAtBoost, self).__init__()
        self.__vehicleMaxSpeedAtBoost = None
        return

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.FLOAT, VehicleMaxSpeedAtBoost._execute)]

    @editorValue(0)
    def _execute(self):
        if self.__vehicleMaxSpeedAtBoost is None:
            self.__vehicleMaxSpeedAtBoost = _defineMaxVehicleSpeed() * 1.2
        return self.__vehicleMaxSpeedAtBoost or 0

    def captionText(self):
        pass


class IsSurfaceContact(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.BOOL, IsSurfaceContact._execute)]

    @editorValue(False)
    def _execute(self):
        vehicle = BigWorld.player().vehicle
        return bool(vehicle.isSurfaceContact) if vehicle is not None else False

    def captionText(self):
        pass
