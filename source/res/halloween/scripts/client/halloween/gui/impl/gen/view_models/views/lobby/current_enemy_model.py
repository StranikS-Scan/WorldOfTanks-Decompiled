# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/current_enemy_model.py
from frameworks.wulf import ViewModel

class CurrentEnemyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CurrentEnemyModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getRole(self):
        return self._getString(1)

    def setRole(self, value):
        self._setString(1, value)

    def getIsAvailable(self):
        return self._getBool(2)

    def setIsAvailable(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CurrentEnemyModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('role', '')
        self._addBoolProperty('isAvailable', False)
