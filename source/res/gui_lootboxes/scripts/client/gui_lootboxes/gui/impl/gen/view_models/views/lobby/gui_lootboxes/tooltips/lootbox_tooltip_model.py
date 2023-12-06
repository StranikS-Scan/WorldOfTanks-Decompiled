# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/lootbox_tooltip_model.py
from frameworks.wulf import ViewModel

class LootboxTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(LootboxTooltipModel, self).__init__(properties=properties, commands=commands)

    def getUserNameKey(self):
        return self._getString(0)

    def setUserNameKey(self, value):
        self._setString(0, value)

    def getDescriptionKey(self):
        return self._getString(1)

    def setDescriptionKey(self, value):
        self._setString(1, value)

    def getTier(self):
        return self._getNumber(2)

    def setTier(self, value):
        self._setNumber(2, value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(LootboxTooltipModel, self)._initialize()
        self._addStringProperty('userNameKey', '')
        self._addStringProperty('descriptionKey', '')
        self._addNumberProperty('tier', 0)
        self._addNumberProperty('count', -1)
