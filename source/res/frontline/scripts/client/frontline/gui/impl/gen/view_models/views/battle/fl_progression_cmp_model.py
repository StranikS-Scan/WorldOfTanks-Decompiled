# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/battle/fl_progression_cmp_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.battle.fl_progression_model import FlProgressionModel

class MapSize(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class FlProgressionCmpModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FlProgressionCmpModel, self).__init__(properties=properties, commands=commands)

    def getMapSize(self):
        return MapSize(self._getString(0))

    def setMapSize(self, value):
        self._setString(0, value.value)

    def getSectorName(self):
        return self._getString(1)

    def setSectorName(self, value):
        self._setString(1, value)

    def getCurrentFirstProgression(self):
        return self._getNumber(2)

    def setCurrentFirstProgression(self, value):
        self._setNumber(2, value)

    def getCurrentSecondProgression(self):
        return self._getNumber(3)

    def setCurrentSecondProgression(self, value):
        self._setNumber(3, value)

    def getDeltaFirst(self):
        return self._getNumber(4)

    def setDeltaFirst(self, value):
        self._setNumber(4, value)

    def getDeltaSecond(self):
        return self._getNumber(5)

    def setDeltaSecond(self, value):
        self._setNumber(5, value)

    def getIsHidden(self):
        return self._getBool(6)

    def setIsHidden(self, value):
        self._setBool(6, value)

    def getProgressions(self):
        return self._getArray(7)

    def setProgressions(self, value):
        self._setArray(7, value)

    @staticmethod
    def getProgressionsType():
        return FlProgressionModel

    def _initialize(self):
        super(FlProgressionCmpModel, self)._initialize()
        self._addStringProperty('mapSize')
        self._addStringProperty('sectorName', 'A')
        self._addNumberProperty('currentFirstProgression', 0)
        self._addNumberProperty('currentSecondProgression', 0)
        self._addNumberProperty('deltaFirst', 0)
        self._addNumberProperty('deltaSecond', 0)
        self._addBoolProperty('isHidden', False)
        self._addArrayProperty('progressions', Array())
