# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_total_resource_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MarkerType(Enum):
    FRIEND = 'friend'
    DEFAULT = 'default'


class NyTotalResourceMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyTotalResourceMarkerModel, self).__init__(properties=properties, commands=commands)

    def getAmount(self):
        return self._getNumber(0)

    def setAmount(self, value):
        self._setNumber(0, value)

    def getMarkerType(self):
        return MarkerType(self._getString(1))

    def setMarkerType(self, value):
        self._setString(1, value.value)

    def getIsVisible(self):
        return self._getBool(2)

    def setIsVisible(self, value):
        self._setBool(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyTotalResourceMarkerModel, self)._initialize()
        self._addNumberProperty('amount', 0)
        self._addStringProperty('markerType')
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isDisabled', False)
