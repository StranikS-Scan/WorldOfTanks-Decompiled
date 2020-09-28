# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/wt_event/battle_progression_view_model.py
from frameworks.wulf import ViewModel

class BattleProgressionViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BattleProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getMaxLevel(self):
        return self._getNumber(2)

    def setMaxLevel(self, value):
        self._setNumber(2, value)

    def getIsSpecial(self):
        return self._getBool(3)

    def setIsSpecial(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BattleProgressionViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('maxLevel', 10)
        self._addBoolProperty('isSpecial', False)
