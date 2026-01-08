# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ImprovedRammingController.py
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic

@ReprInjector.withParent()
class ImprovedRammingController(VehicleDynamicComponent, IMechanicComponent):

    def __init__(self):
        super(ImprovedRammingController, self).__init__()
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.IMPROVED_RAMMING
