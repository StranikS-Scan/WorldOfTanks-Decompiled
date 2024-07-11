# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/lootbox_key_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel

class LootboxKeyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(LootboxKeyTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootboxKey(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootboxKeyType():
        return LootboxKeyViewModel

    def getLootboxNames(self):
        return self._getArray(1)

    def setLootboxNames(self, value):
        self._setArray(1, value)

    @staticmethod
    def getLootboxNamesType():
        return unicode

    def getIsActionTooltip(self):
        return self._getBool(2)

    def setIsActionTooltip(self, value):
        self._setBool(2, value)

    def getIsShowCount(self):
        return self._getBool(3)

    def setIsShowCount(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(LootboxKeyTooltipModel, self)._initialize()
        self._addViewModelProperty('lootboxKey', LootboxKeyViewModel())
        self._addArrayProperty('lootboxNames', Array())
        self._addBoolProperty('isActionTooltip', False)
        self._addBoolProperty('isShowCount', True)
