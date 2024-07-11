# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/loot_boxes_lose_reward_screen_model.py
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel

class LootBoxesLoseRewardScreenModel(ViewModel):
    __slots__ = ('onClose', 'onRepeatOpen')

    def __init__(self, properties=5, commands=2):
        super(LootBoxesLoseRewardScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootboxKey(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootboxKeyType():
        return LootboxKeyViewModel

    def getCountFailKey(self):
        return self._getNumber(1)

    def setCountFailKey(self, value):
        self._setNumber(1, value)

    def getLootboxID(self):
        return self._getNumber(2)

    def setLootboxID(self, value):
        self._setNumber(2, value)

    def getLootboxName(self):
        return self._getString(3)

    def setLootboxName(self, value):
        self._setString(3, value)

    def getLootboxNameKey(self):
        return self._getString(4)

    def setLootboxNameKey(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(LootBoxesLoseRewardScreenModel, self)._initialize()
        self._addViewModelProperty('lootboxKey', LootboxKeyViewModel())
        self._addNumberProperty('countFailKey', 0)
        self._addNumberProperty('lootboxID', 0)
        self._addStringProperty('lootboxName', '')
        self._addStringProperty('lootboxNameKey', '')
        self.onClose = self._addCommand('onClose')
        self.onRepeatOpen = self._addCommand('onRepeatOpen')
