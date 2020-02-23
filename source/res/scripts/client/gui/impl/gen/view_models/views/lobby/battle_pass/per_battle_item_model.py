# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/per_battle_item_model.py
from frameworks.wulf import ViewModel

class PerBattleItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PerBattleItemModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getWinPoint(self):
        return self._getNumber(1)

    def setWinPoint(self, value):
        self._setNumber(1, value)

    def getLosePoint(self):
        return self._getNumber(2)

    def setLosePoint(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PerBattleItemModel, self)._initialize()
        self._addStringProperty('label', '')
        self._addNumberProperty('winPoint', 0)
        self._addNumberProperty('losePoint', 0)
