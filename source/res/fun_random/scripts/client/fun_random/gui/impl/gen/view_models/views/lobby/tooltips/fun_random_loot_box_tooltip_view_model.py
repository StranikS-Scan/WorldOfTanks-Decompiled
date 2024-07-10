# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/tooltips/fun_random_loot_box_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class FunRandomLootBoxTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FunRandomLootBoxTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getIconKey(self):
        return self._getString(1)

    def setIconKey(self, value):
        self._setString(1, value)

    def getAssetsPointer(self):
        return self._getString(2)

    def setAssetsPointer(self, value):
        self._setString(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(FunRandomLootBoxTooltipViewModel, self)._initialize()
        self._addStringProperty('label', '')
        self._addStringProperty('iconKey', '')
        self._addStringProperty('assetsPointer', 'undefined')
        self._addArrayProperty('rewards', Array())
