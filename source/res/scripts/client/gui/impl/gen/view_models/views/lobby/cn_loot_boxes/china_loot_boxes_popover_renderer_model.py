# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/china_loot_boxes_popover_renderer_model.py
from frameworks.wulf import ViewModel

class ChinaLootBoxesPopoverRendererModel(ViewModel):
    __slots__ = ('onEventBtnClick',)

    def __init__(self, properties=4, commands=1):
        super(ChinaLootBoxesPopoverRendererModel, self).__init__(properties=properties, commands=commands)

    def getLootBoxType(self):
        return self._getString(0)

    def setLootBoxType(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getIsOpenBtnEnabled(self):
        return self._getBool(2)

    def setIsOpenBtnEnabled(self, value):
        self._setBool(2, value)

    def getIsBuyBtnEnabled(self):
        return self._getBool(3)

    def setIsBuyBtnEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ChinaLootBoxesPopoverRendererModel, self)._initialize()
        self._addStringProperty('lootBoxType', '')
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isOpenBtnEnabled', True)
        self._addBoolProperty('isBuyBtnEnabled', True)
        self.onEventBtnClick = self._addCommand('onEventBtnClick')
