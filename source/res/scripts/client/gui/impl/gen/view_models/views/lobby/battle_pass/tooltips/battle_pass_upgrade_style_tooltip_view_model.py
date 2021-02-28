# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_upgrade_style_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassUpgradeStyleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BattlePassUpgradeStyleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getStyleId(self):
        return self._getNumber(0)

    def setStyleId(self, value):
        self._setNumber(0, value)

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getVehicles(self):
        return self._getString(3)

    def setVehicles(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BattlePassUpgradeStyleTooltipViewModel, self)._initialize()
        self._addNumberProperty('styleId', 0)
        self._addStringProperty('styleName', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('vehicles', '')
