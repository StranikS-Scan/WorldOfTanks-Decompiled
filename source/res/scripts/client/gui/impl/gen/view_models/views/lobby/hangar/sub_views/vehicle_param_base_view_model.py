# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_param_base_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class HighlightType(Enum):
    NONE = 'none'
    INCREASE = 'increase'
    DECREASE = 'decrease'
    SITUATIONAL = 'situational'


class VehicleParamBaseViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleParamBaseViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getTooltipID(self):
        return self._getString(2)

    def setTooltipID(self, value):
        self._setString(2, value)

    def getValue(self):
        return self._getString(3)

    def setValue(self, value):
        self._setString(3, value)

    def getHighlightType(self):
        return HighlightType(self._getString(4))

    def setHighlightType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(VehicleParamBaseViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addBoolProperty('isEnabled', False)
        self._addStringProperty('tooltipID', '')
        self._addStringProperty('value', '')
        self._addStringProperty('highlightType')
