# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/perk_base_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PerkBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PerkBaseModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getResource(2)

    def setName(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(PerkBaseModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('icon', '')
        self._addResourceProperty('name', R.invalid())
