# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/reward_window_content_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.button_model import ButtonModel

class RewardWindowContentModel(ViewModel):
    __slots__ = ('onConfirmBtnClicked',)

    @property
    def confirmBtn(self):
        return self._getViewModel(0)

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def getRewardsList(self):
        return self._getArray(2)

    def setRewardsList(self, value):
        self._setArray(2, value)

    def getShowRewards(self):
        return self._getBool(3)

    def setShowRewards(self, value):
        self._setBool(3, value)

    def _initialize(self):
        self._addViewModelProperty('confirmBtn', ButtonModel())
        self._addStringProperty('eventName', '')
        self._addArrayProperty('rewardsList', Array())
        self._addBoolProperty('showRewards', False)
        self.onConfirmBtnClicked = self._addCommand('onConfirmBtnClicked')
