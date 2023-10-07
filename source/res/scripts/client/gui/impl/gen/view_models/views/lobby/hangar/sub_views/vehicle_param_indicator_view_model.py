# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_param_indicator_view_model.py
from frameworks.wulf import ViewModel

class VehicleParamIndicatorViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleParamIndicatorViewModel, self).__init__(properties=properties, commands=commands)

    def getIsUseAnim(self):
        return self._getBool(0)

    def setIsUseAnim(self, value):
        self._setBool(0, value)

    def getDelta(self):
        return self._getNumber(1)

    def setDelta(self, value):
        self._setNumber(1, value)

    def getMarkerValue(self):
        return self._getNumber(2)

    def setMarkerValue(self, value):
        self._setNumber(2, value)

    def getMaxValue(self):
        return self._getNumber(3)

    def setMaxValue(self, value):
        self._setNumber(3, value)

    def getValue(self):
        return self._getNumber(4)

    def setValue(self, value):
        self._setNumber(4, value)

    def getMinValue(self):
        return self._getNumber(5)

    def setMinValue(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(VehicleParamIndicatorViewModel, self)._initialize()
        self._addBoolProperty('isUseAnim', False)
        self._addNumberProperty('delta', 0)
        self._addNumberProperty('markerValue', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('value', 0)
        self._addNumberProperty('minValue', 0)
