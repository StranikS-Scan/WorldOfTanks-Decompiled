# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_indicator_type.py
from enum import Enum
from frameworks.wulf import ViewModel

class IndicatorType(Enum):
    FOOD = 'food'
    FUN = 'fun'
    ACTIVITY = 'activity'


class NyIndicatorType(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyIndicatorType, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return IndicatorType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(NyIndicatorType, self)._initialize()
        self._addStringProperty('type')
