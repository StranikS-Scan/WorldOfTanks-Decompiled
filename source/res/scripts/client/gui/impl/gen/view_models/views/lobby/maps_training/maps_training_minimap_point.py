# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_minimap_point.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MapsTrainingMinimapPoint(ViewModel):
    __slots__ = ()
    POINT_TYPE_DEFAULT = 'point'
    POINT_TYPE_BASE = 'main'
    POINT_TYPE_ENEMY_BASE = 'enemyBase'

    def __init__(self, properties=8, commands=0):
        super(MapsTrainingMinimapPoint, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIsLeft(self):
        return self._getBool(1)

    def setIsLeft(self, value):
        self._setBool(1, value)

    def getTextKeys(self):
        return self._getArray(2)

    def setTextKeys(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTextKeysType():
        return unicode

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getPositionX(self):
        return self._getNumber(4)

    def setPositionX(self, value):
        self._setNumber(4, value)

    def getPositionY(self):
        return self._getNumber(5)

    def setPositionY(self, value):
        self._setNumber(5, value)

    def getIsShowTooltip(self):
        return self._getBool(6)

    def setIsShowTooltip(self, value):
        self._setBool(6, value)

    def getTooltipImage(self):
        return self._getResource(7)

    def setTooltipImage(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(MapsTrainingMinimapPoint, self)._initialize()
        self._addStringProperty('id', '')
        self._addBoolProperty('isLeft', False)
        self._addArrayProperty('textKeys', Array())
        self._addStringProperty('type', '')
        self._addNumberProperty('positionX', 0)
        self._addNumberProperty('positionY', 0)
        self._addBoolProperty('isShowTooltip', False)
        self._addResourceProperty('tooltipImage', R.invalid())
