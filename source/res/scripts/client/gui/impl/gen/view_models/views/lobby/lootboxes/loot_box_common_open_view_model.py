# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_common_open_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootBoxCommonOpenViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick',)
    WINDOW_MAX_BOX_COUNT = 5

    def __init__(self, properties=2, commands=1):
        super(LootBoxCommonOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    def getRewardSize(self):
        return self._getString(1)

    def setRewardSize(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(LootBoxCommonOpenViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('rewardSize', '')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
