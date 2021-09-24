# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_guaranteed_reward_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.portal_premium_tanks import PortalPremiumTanks
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward

class WtGuaranteedRewardTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtGuaranteedRewardTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedAward(self):
        return self._getViewModel(0)

    @property
    def tanks(self):
        return self._getViewModel(1)

    def _initialize(self):
        super(WtGuaranteedRewardTooltipViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addViewModelProperty('tanks', UserListModel())
