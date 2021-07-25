# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_states.py
from frameworks.wulf import ViewModel

class DetachmentStates(ViewModel):
    __slots__ = ()
    DISMISSED = 'dismissed'
    IN_BATTLE = 'inBattle'
    IN_PLATOON = 'inPlatoon'
    SELECTED = 'selected'
    WRONG_SPECIALIZATION = 'wrongSpecialization'
    WRONG_CLASS = 'wrongClass'
    EMPTY_VEHICLE_SLOT = 'emptyVehicleSlot'
    AVAILABLE = 'available'
    UNKNOWN = 'unknown'
    HAS_LOCK_CREW = 'hasLockCrew'

    def __init__(self, properties=0, commands=0):
        super(DetachmentStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DetachmentStates, self)._initialize()
