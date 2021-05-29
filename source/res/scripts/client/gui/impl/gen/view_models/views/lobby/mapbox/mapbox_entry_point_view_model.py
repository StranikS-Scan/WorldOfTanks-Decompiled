# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/mapbox_entry_point_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Seasons(IntEnum):
    SEASON1 = 1
    SEASON2 = 2
    SEASON3 = 3
    SEASON4 = 4


class MapboxEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=2, commands=1):
        super(MapboxEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getSeason(self):
        return Seasons(self._getNumber(0))

    def setSeason(self, value):
        self._setNumber(0, value.value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(MapboxEntryPointViewModel, self)._initialize()
        self._addNumberProperty('season')
        self._addNumberProperty('endDate', -1)
        self.onActionClick = self._addCommand('onActionClick')
