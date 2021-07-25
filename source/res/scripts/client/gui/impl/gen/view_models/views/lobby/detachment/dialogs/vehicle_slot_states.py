# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/vehicle_slot_states.py
from frameworks.wulf import ViewModel

class VehicleSlotStates(ViewModel):
    __slots__ = ()
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    FOR_PURCHASE = 'forPurchase'
    DISABLE = 'disable'

    def __init__(self, properties=0, commands=0):
        super(VehicleSlotStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(VehicleSlotStates, self)._initialize()
