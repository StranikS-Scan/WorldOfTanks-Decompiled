# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/pet_indicators.py
from enum import Enum
from frameworks.wulf import ViewModel

class Indicators(Enum):
    FOOD = 'food'
    FUN = 'fun'
    ACTIVITY = 'activity'


class PetIndicators(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PetIndicators, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return Indicators(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def getIsOpened(self):
        return self._getBool(1)

    def setIsOpened(self, value):
        self._setBool(1, value)

    def getCountIndicator(self):
        return self._getString(2)

    def setCountIndicator(self, value):
        self._setString(2, value)

    def getCountMails(self):
        return self._getString(3)

    def setCountMails(self, value):
        self._setString(3, value)

    def getBonus(self):
        return self._getString(4)

    def setBonus(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(PetIndicators, self)._initialize()
        self._addStringProperty('name')
        self._addBoolProperty('isOpened', False)
        self._addStringProperty('countIndicator', '')
        self._addStringProperty('countMails', '')
        self._addStringProperty('bonus', '')
