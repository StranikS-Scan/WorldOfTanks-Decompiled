# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/compensation_model.py
from frameworks.wulf import ViewModel

class CompensationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CompensationModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getLabel(self):
        return self._getString(3)

    def setLabel(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CompensationModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('label', '')
