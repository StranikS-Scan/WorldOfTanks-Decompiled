# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/crew_converting_constants.py
from frameworks.wulf import ViewModel

class CrewConvertingConstants(ViewModel):
    __slots__ = ()
    NO_VEHICLE_SELECTED = 'noVehicleSelected'
    NOT_FORMED = 'notFormed'
    LEADERS_OVERFLOW = 'leadersOverflow'
    NEED_RETRAIN = 'needRetrain'
    IN_PLATOON = 'inPlatoon'
    IN_BATTLE = 'inBattle'
    CONVERTING_AVAILABLE = 'convertingAvailable'

    def __init__(self, properties=0, commands=0):
        super(CrewConvertingConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CrewConvertingConstants, self)._initialize()
