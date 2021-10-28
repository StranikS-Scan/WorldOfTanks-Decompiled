# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/tank_model.py
from frameworks.wulf import ViewModel

class TankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIconName(self):
        return self._getString(2)

    def setIconName(self, value):
        self._setString(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(TankModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('type', '')
