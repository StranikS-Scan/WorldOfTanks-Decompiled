# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_category_tooltip_model.py
from frameworks.wulf import ViewModel

class LootBoxCategoryTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(LootBoxCategoryTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(LootBoxCategoryTooltipModel, self)._initialize()
        self._addStringProperty('category', '')
