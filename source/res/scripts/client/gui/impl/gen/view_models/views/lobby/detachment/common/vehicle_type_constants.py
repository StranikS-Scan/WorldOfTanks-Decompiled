# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/vehicle_type_constants.py
from frameworks.wulf import ViewModel

class VehicleTypeConstants(ViewModel):
    __slots__ = ()
    LIGHT_TANK = 'lightTank'
    MEDIUM_TANK = 'mediumTank'
    HEAVY_TANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'

    def __init__(self, properties=0, commands=0):
        super(VehicleTypeConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(VehicleTypeConstants, self)._initialize()
