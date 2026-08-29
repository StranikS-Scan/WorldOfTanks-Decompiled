# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/battle/boss_status_model.py
from frameworks.wulf import ViewModel

class BossStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BossStatusModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getClan(self):
        return self._getString(1)

    def setClan(self, value):
        self._setString(1, value)

    def getKills(self):
        return self._getNumber(2)

    def setKills(self, value):
        self._setNumber(2, value)

    def getCurrentHP(self):
        return self._getNumber(3)

    def setCurrentHP(self, value):
        self._setNumber(3, value)

    def getMaxHP(self):
        return self._getNumber(4)

    def setMaxHP(self, value):
        self._setNumber(4, value)

    def getIsAnonymized(self):
        return self._getBool(5)

    def setIsAnonymized(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BossStatusModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('clan', '')
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('currentHP', 0)
        self._addNumberProperty('maxHP', 0)
        self._addBoolProperty('isAnonymized', False)
