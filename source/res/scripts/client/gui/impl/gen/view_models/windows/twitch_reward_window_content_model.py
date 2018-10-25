# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/twitch_reward_window_content_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.button_model import ButtonModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class TwitchRewardWindowContentModel(ViewModel):
    __slots__ = ('onConfirmBtnClicked',)

    @property
    def confirmBtn(self):
        return self._getViewModel(0)

    @property
    def rewardsList(self):
        return self._getViewModel(1)

    def getEventName(self):
        return self._getString(2)

    def setEventName(self, value):
        self._setString(2, value)

    def getShowRewards(self):
        return self._getBool(3)

    def setShowRewards(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(TwitchRewardWindowContentModel, self)._initialize()
        self._addViewModelProperty('confirmBtn', ButtonModel())
        self._addViewModelProperty('rewardsList', ListModel())
        self._addStringProperty('eventName', '')
        self._addBoolProperty('showRewards', False)
        self.onConfirmBtnClicked = self._addCommand('onConfirmBtnClicked')
