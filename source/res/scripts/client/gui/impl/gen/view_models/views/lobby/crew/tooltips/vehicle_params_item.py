# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/vehicle_params_item.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ValueStyleEnum(Enum):
    GREENBRIGHT = 'greenBright'
    RED = 'red'
    WHITEORANGE = 'whiteOrange'
    YELLOW = 'yellow'
    WHITESPANISH = 'whiteSpanish'


class VehicleParamsItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleParamsItem, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getAsteriskIcon(self):
        return self._getResource(4)

    def setAsteriskIcon(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(VehicleParamsItem, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('value', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isEnabled', True)
        self._addResourceProperty('asteriskIcon', R.invalid())
