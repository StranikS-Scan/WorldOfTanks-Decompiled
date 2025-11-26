# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/battle_ability_alt_tooltip_model.py
from frameworks.wulf import ViewModel

class BattleAbilityAltTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattleAbilityAltTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getVideoName(self):
        return self._getString(1)

    def setVideoName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BattleAbilityAltTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('videoName', '')
        self._addStringProperty('description', '')
