# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_auto_open_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class LootBoxAutoOpenViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onOkBtnClick')

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(LootBoxAutoOpenViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onOkBtnClick = self._addCommand('onOkBtnClick')
