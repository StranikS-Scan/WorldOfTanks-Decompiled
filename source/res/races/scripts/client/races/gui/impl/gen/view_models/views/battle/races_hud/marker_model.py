# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/battle/races_hud/marker_model.py
from frameworks.wulf import ViewModel

class MarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MarkerModel, self).__init__(properties=properties, commands=commands)

    def getPosx(self):
        return self._getReal(0)

    def setPosx(self, value):
        self._setReal(0, value)

    def getPosy(self):
        return self._getReal(1)

    def setPosy(self, value):
        self._setReal(1, value)

    def getScale(self):
        return self._getReal(2)

    def setScale(self, value):
        self._setReal(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(MarkerModel, self)._initialize()
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addRealProperty('scale', 0.0)
        self._addBoolProperty('isVisible', True)
