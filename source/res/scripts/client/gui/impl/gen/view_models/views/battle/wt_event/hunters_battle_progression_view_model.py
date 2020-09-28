# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/wt_event/hunters_battle_progression_view_model.py
from frameworks.wulf import ViewModel

class HuntersBattleProgressionViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HuntersBattleProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getProgress(self):
        return self._getNumber(0)

    def setProgress(self, value):
        self._setNumber(0, value)

    def getMaxLevel(self):
        return self._getNumber(1)

    def setMaxLevel(self, value):
        self._setNumber(1, value)

    def getIsEnemyMode(self):
        return self._getBool(2)

    def setIsEnemyMode(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(HuntersBattleProgressionViewModel, self)._initialize()
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('maxLevel', 10)
        self._addBoolProperty('isEnemyMode', False)
