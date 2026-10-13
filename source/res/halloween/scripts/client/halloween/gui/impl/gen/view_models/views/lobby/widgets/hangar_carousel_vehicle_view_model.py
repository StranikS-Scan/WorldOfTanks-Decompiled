# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/hangar_carousel_vehicle_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class VehicleTypes(Enum):
    NONE = 'none'
    LIGHTTANK = 'lightTank'
    MEDIUMTANK = 'mediumTank'
    HEAVYTANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'


class VehicleStates(Enum):
    DEFAULT = 'default'
    LOCKED = 'locked'
    INBATTLE = 'inBattle'
    INPLATOON = 'inPlatoon'
    INQUEUE = 'inQueue'


class CarouselTooltips(Enum):
    HALLOWEENCAROUSELVEHICLE = 'halloweenCarouselVehicle'
    HALLOWEENVEHICLEFEATURETOOLTIP = 'halloweenVehicleFeatureTooltip'
    DAILYQUEST = 'dailyQuest'


class HangarCarouselVehicleViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(HangarCarouselVehicleViewModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getInvID(self):
        return self._getNumber(1)

    def setInvID(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getHasDaily(self):
        return self._getBool(4)

    def setHasDaily(self, value):
        self._setBool(4, value)

    def getVehicleType(self):
        return VehicleTypes(self._getString(5))

    def setVehicleType(self, value):
        self._setString(5, value.value)

    def getVehicleState(self):
        return VehicleStates(self._getString(6))

    def setVehicleState(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(HangarCarouselVehicleViewModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('invID', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('iconName', '')
        self._addBoolProperty('hasDaily', False)
        self._addStringProperty('vehicleType')
        self._addStringProperty('vehicleState')
