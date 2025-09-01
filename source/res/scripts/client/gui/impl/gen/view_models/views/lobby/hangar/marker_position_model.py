# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/marker_position_model.py
from frameworks.wulf import ViewModel

class MarkerPositionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MarkerPositionModel, self).__init__(properties=properties, commands=commands)

    def getPosx(self):
        return self._getReal(0)

    def setPosx(self, value):
        self._setReal(0, value)

    def getPosy(self):
        return self._getReal(1)

    def setPosy(self, value):
        self._setReal(1, value)

    def getNdcLimitX(self):
        return self._getReal(2)

    def setNdcLimitX(self, value):
        self._setReal(2, value)

    def getNdcLimitY(self):
        return self._getReal(3)

    def setNdcLimitY(self, value):
        self._setReal(3, value)

    def getScale(self):
        return self._getReal(4)

    def setScale(self, value):
        self._setReal(4, value)

    def getIsVisible(self):
        return self._getBool(5)

    def setIsVisible(self, value):
        self._setBool(5, value)

    def getAngle(self):
        return self._getReal(6)

    def setAngle(self, value):
        self._setReal(6, value)

    def getDistance(self):
        return self._getNumber(7)

    def setDistance(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(MarkerPositionModel, self)._initialize()
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addRealProperty('ndcLimitX', 1.15)
        self._addRealProperty('ndcLimitY', 1.15)
        self._addRealProperty('scale', 0.0)
        self._addBoolProperty('isVisible', False)
        self._addRealProperty('angle', 0.0)
        self._addNumberProperty('distance', 0)
