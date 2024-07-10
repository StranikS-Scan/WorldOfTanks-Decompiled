# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/ability_tooltip_view_model.py
from frameworks.wulf import ViewModel

class AbilityTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AbilityTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def getCooldownSeconds(self):
        return self._getNumber(2)

    def setCooldownSeconds(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(AbilityTooltipViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('iconName', '')
        self._addNumberProperty('cooldownSeconds', 0)
        self._addStringProperty('description', '')
