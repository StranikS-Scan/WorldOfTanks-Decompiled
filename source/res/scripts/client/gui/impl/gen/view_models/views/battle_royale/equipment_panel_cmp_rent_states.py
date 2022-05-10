# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/equipment_panel_cmp_rent_states.py
from frameworks.wulf import ViewModel

class EquipmentPanelCmpRentStates(ViewModel):
    __slots__ = ()
    STATE_NORMAL = 'normal'
    STATE_TEST_DRIVE_AVAILABLE = 'testDriveAvailable'
    STATE_TEST_DRIVE_ACTIVE = 'testDriveActive'
    STATE_RENT_AVAILABLE = 'rentAvailable'
    STATE_RENT_ACTIVE = 'rentActive'

    def __init__(self, properties=0, commands=0):
        super(EquipmentPanelCmpRentStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EquipmentPanelCmpRentStates, self)._initialize()
