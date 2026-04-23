# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/frontman_tooltip_ability_model.py
from frameworks.wulf import ViewModel

class FrontmanTooltipAbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FrontmanTooltipAbilityModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getDescr(self):
        return self._getString(2)

    def setDescr(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(FrontmanTooltipAbilityModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('descr', '')
