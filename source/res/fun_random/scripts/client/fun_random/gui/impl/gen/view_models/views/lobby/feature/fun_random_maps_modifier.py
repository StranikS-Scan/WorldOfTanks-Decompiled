# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_maps_modifier.py
from frameworks.wulf import ViewModel

class FunRandomMapsModifier(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(FunRandomMapsModifier, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getPositionX(self):
        return self._getNumber(2)

    def setPositionX(self, value):
        self._setNumber(2, value)

    def getPositionY(self):
        return self._getNumber(3)

    def setPositionY(self, value):
        self._setNumber(3, value)

    def getTitle(self):
        return self._getString(4)

    def setTitle(self, value):
        self._setString(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(FunRandomMapsModifier, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('type', '')
        self._addNumberProperty('positionX', 0)
        self._addNumberProperty('positionY', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
