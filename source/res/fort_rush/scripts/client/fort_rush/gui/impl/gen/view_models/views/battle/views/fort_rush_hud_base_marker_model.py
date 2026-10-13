# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/battle/views/fort_rush_hud_base_marker_model.py
from frameworks.wulf import ViewModel

class FortRushHudBaseMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(FortRushHudBaseMarkerModel, self).__init__(properties=properties, commands=commands)

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

    def getLabel(self):
        return self._getString(4)

    def setLabel(self, value):
        self._setString(4, value)

    def getUid(self):
        return self._getNumber(5)

    def setUid(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(FortRushHudBaseMarkerModel, self)._initialize()
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addRealProperty('scale', 1.0)
        self._addBoolProperty('isVisible', False)
        self._addStringProperty('label', '')
        self._addNumberProperty('uid', -1)
