# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/tooltips/battle_pass_quests_points.py
from frameworks.wulf import ViewModel

class BattlePassQuestsPoints(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattlePassQuestsPoints, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BattlePassQuestsPoints, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addStringProperty('name', '')
