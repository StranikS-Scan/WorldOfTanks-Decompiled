# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ImprovedRammingController.py
from __future__ import absolute_import
from gui.shared.utils.decorators import ReprInjector
from items.vehicle_mechanics_types import VehicleMechanicKey, VehicleMechanicKeys
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponent

@ReprInjector.withParent()
class ImprovedRammingController(VehicleDynamicComponent, IMechanicComponent):

    def __init__(self):
        super(ImprovedRammingController, self).__init__()
        self._initComponent()

    @property
    def vehicleMechanicKey(self):
        return VehicleMechanicKeys.IMPROVED_RAMMING
