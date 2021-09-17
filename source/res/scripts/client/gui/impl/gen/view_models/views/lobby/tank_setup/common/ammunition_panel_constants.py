# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ammunition_panel_constants.py
from frameworks.wulf import ViewModel

class AmmunitionPanelConstants(ViewModel):
    __slots__ = ()
    NO_GROUP = 0
    EQUIPMENT_AND_SHELLS = 1
    OPTIONAL_DEVICES_AND_BOOSTERS = 2

    def __init__(self, properties=0, commands=0):
        super(AmmunitionPanelConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(AmmunitionPanelConstants, self)._initialize()
