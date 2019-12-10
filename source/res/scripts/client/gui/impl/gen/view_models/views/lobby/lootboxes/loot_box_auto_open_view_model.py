# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_auto_open_view_model.py
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_common_open_view_model import LootBoxCommonOpenViewModel

class LootBoxAutoOpenViewModel(LootBoxCommonOpenViewModel):
    __slots__ = ('onOkBtnClick',)

    def __init__(self, properties=2, commands=2):
        super(LootBoxAutoOpenViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootBoxAutoOpenViewModel, self)._initialize()
        self.onOkBtnClick = self._addCommand('onOkBtnClick')
