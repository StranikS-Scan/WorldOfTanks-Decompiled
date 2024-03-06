# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/prebattle/prebattle_hints_view_model.py
from frameworks.wulf import ViewModel

class PrebattleHintsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PrebattleHintsViewModel, self).__init__(properties=properties, commands=commands)

    def getHintType(self):
        return self._getString(0)

    def setHintType(self, value):
        self._setString(0, value)

    def getCanSkip(self):
        return self._getBool(1)

    def setCanSkip(self, value):
        self._setBool(1, value)

    def getIsColorBlind(self):
        return self._getBool(2)

    def setIsColorBlind(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PrebattleHintsViewModel, self)._initialize()
        self._addStringProperty('hintType', '')
        self._addBoolProperty('canSkip', False)
        self._addBoolProperty('isColorBlind', False)
