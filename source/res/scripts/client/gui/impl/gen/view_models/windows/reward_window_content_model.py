# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/reward_window_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class RewardWindowContentModel(ViewModel):
    __slots__ = ('onConfirmBtnClicked', 'onHyperLinkClicked')

    @property
    def rewardsList(self):
        return self._getViewModel(0)

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def getShowRewards(self):
        return self._getBool(2)

    def setShowRewards(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(RewardWindowContentModel, self)._initialize()
        self._addViewModelProperty('rewardsList', ListModel())
        self._addStringProperty('eventName', '')
        self._addBoolProperty('showRewards', False)
        self.onConfirmBtnClicked = self._addCommand('onConfirmBtnClicked')
        self.onHyperLinkClicked = self._addCommand('onHyperLinkClicked')
