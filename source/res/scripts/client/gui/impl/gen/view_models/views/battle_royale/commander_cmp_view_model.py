# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/commander_cmp_view_model.py
from frameworks.wulf import ViewModel

class CommanderCmpViewModel(ViewModel):
    __slots__ = ('onToggleSound',)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def getIsRuRealm(self):
        return self._getBool(1)

    def setIsRuRealm(self, value):
        self._setBool(1, value)

    def getIsRuVoEnabled(self):
        return self._getBool(2)

    def setIsRuVoEnabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CommanderCmpViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addBoolProperty('isRuRealm', True)
        self._addBoolProperty('isRuVoEnabled', True)
        self.onToggleSound = self._addCommand('onToggleSound')
