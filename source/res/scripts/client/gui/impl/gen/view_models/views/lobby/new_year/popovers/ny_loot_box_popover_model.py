# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_loot_box_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_item_popover_model import NyLootBoxItemPopoverModel

class NyLootBoxPopoverModel(ViewModel):
    __slots__ = ('onEventBtnClick', 'onBuyBtnClick')
    LOOT_BOX_USUAL = 'newYear_usual'
    LOOT_BOX_PREMIUM = 'newYear_premium'

    def __init__(self, properties=3, commands=2):
        super(NyLootBoxPopoverModel, self).__init__(properties=properties, commands=commands)

    def getBoxesList(self):
        return self._getArray(0)

    def setBoxesList(self, value):
        self._setArray(0, value)

    def getIsCnRealm(self):
        return self._getBool(1)

    def setIsCnRealm(self, value):
        self._setBool(1, value)

    def getIsGiftSystemDisabled(self):
        return self._getBool(2)

    def setIsGiftSystemDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NyLootBoxPopoverModel, self)._initialize()
        self._addArrayProperty('boxesList', Array())
        self._addBoolProperty('isCnRealm', False)
        self._addBoolProperty('isGiftSystemDisabled', False)
        self.onEventBtnClick = self._addCommand('onEventBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
