# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tank_style_model.py
from frameworks.wulf import ViewModel

class TankStyleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankStyleModel, self).__init__(properties=properties, commands=commands)

    def getStyleId(self):
        return self._getNumber(0)

    def setStyleId(self, value):
        self._setNumber(0, value)

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getIsInHangar(self):
        return self._getBool(2)

    def setIsInHangar(self, value):
        self._setBool(2, value)

    def getIsObtained(self):
        return self._getBool(3)

    def setIsObtained(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(TankStyleModel, self)._initialize()
        self._addNumberProperty('styleId', 0)
        self._addStringProperty('styleName', '')
        self._addBoolProperty('isInHangar', False)
        self._addBoolProperty('isObtained', False)
