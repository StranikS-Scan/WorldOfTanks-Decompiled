# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_confirm_out_of_the_box_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_item_model import RewardItemModel

class WtEventConfirmOutOfTheBoxViewModel(ViewModel):
    __slots__ = ('onPickReward',)

    def __init__(self, properties=1, commands=1):
        super(WtEventConfirmOutOfTheBoxViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(WtEventConfirmOutOfTheBoxViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self.onPickReward = self._addCommand('onPickReward')
