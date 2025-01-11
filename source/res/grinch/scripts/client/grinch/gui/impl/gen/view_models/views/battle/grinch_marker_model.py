# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MarkerTypeEnum(Enum):
    NONE = 'none'
    CENTRAL = 'central'
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'


class GrinchMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(GrinchMarkerModel, self).__init__(properties=properties, commands=commands)

    def getTeam(self):
        return self._getNumber(0)

    def setTeam(self, value):
        self._setNumber(0, value)

    def getType(self):
        return MarkerTypeEnum(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getPosx(self):
        return self._getReal(2)

    def setPosx(self, value):
        self._setReal(2, value)

    def getPosy(self):
        return self._getReal(3)

    def setPosy(self, value):
        self._setReal(3, value)

    def getScale(self):
        return self._getReal(4)

    def setScale(self, value):
        self._setReal(4, value)

    def getDistance(self):
        return self._getNumber(5)

    def setDistance(self, value):
        self._setNumber(5, value)

    def getAngle(self):
        return self._getReal(6)

    def setAngle(self, value):
        self._setReal(6, value)

    def getIsVisible(self):
        return self._getBool(7)

    def setIsVisible(self, value):
        self._setBool(7, value)

    def getIsEnemy(self):
        return self._getBool(8)

    def setIsEnemy(self, value):
        self._setBool(8, value)

    def getScore(self):
        return self._getNumber(9)

    def setScore(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(GrinchMarkerModel, self)._initialize()
        self._addNumberProperty('team', 0)
        self._addStringProperty('type', MarkerTypeEnum.NONE.value)
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addRealProperty('scale', 1.0)
        self._addNumberProperty('distance', -1)
        self._addRealProperty('angle', 0.0)
        self._addBoolProperty('isVisible', False)
        self._addBoolProperty('isEnemy', False)
        self._addNumberProperty('score', 0)
