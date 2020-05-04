# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/tank_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankModel, self).__init__(properties=properties, commands=commands)

    def getTankId(self):
        return self._getNumber(0)

    def setTankId(self, value):
        self._setNumber(0, value)

    def getTankName(self):
        return self._getString(1)

    def setTankName(self, value):
        self._setString(1, value)

    def getTankIcon(self):
        return self._getResource(2)

    def setTankIcon(self, value):
        self._setResource(2, value)

    def getIsComplete(self):
        return self._getBool(3)

    def setIsComplete(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(TankModel, self)._initialize()
        self._addNumberProperty('tankId', 0)
        self._addStringProperty('tankName', '')
        self._addResourceProperty('tankIcon', R.invalid())
        self._addBoolProperty('isComplete', False)
