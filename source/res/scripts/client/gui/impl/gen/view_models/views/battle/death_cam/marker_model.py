# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/marker_model.py
from frameworks.wulf import ViewModel

class MarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MarkerModel, self).__init__(properties=properties, commands=commands)

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

    def getIsVisible(self):
        return self._getBool(4)

    def setIsVisible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(MarkerModel, self)._initialize()
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addRealProperty('ndcLimitX', 2.0)
        self._addRealProperty('ndcLimitY', 2.0)
        self._addBoolProperty('isVisible', False)
