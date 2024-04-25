# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/ability_tooltip_model.py
from frameworks.wulf import ViewModel

class AbilityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AbilityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsRoleAbility(self):
        return self._getBool(0)

    def setIsRoleAbility(self, value):
        self._setBool(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getDescr(self):
        return self._getString(3)

    def setDescr(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(AbilityTooltipModel, self)._initialize()
        self._addBoolProperty('isRoleAbility', False)
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('descr', '')
