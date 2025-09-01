# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/base_reward_view.py
import typing
import SoundGroups
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from one_time_gift.gui.impl.lobby.meta_view.sub_view_base import SubViewBase
from one_time_gift.gui.shared.hide_tooltips import hideTooltips
if typing.TYPE_CHECKING:
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import OneTimeGiftRewardViewModel
EXIT_EVENT = 'gui_hangar_award_screen_stop'

class BaseRewardView(SubViewBase):
    _REWARD_TYPE = None

    def __init__(self, viewModel, parentView):
        super(BaseRewardView, self).__init__(viewModel, parentView)
        self._tooltipItems = {}

    @property
    def viewId(self):
        raise NotImplementedError

    @property
    def viewModel(self):
        return super(BaseRewardView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BaseRewardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self._tooltipItems.get(tooltipId)

    def initialize(self, bonuses, onConfirmCallback=None, onCloseCallback=None):
        super(BaseRewardView, self).initialize(onConfirmCallback, onCloseCallback)
        hideTooltips()
        rewards = self._composeRewards(bonuses)
        if not rewards:
            return
        with self.viewModel.transaction() as vm:
            vm.setRewardType(self._REWARD_TYPE)
            self._setResources(vm)
            self._setRewards(vm, rewards)

    def finalize(self):
        SoundGroups.g_instance.playSound2D(EXIT_EVENT)
        self.viewModel.vehicleRewards.clearItems()
        self.viewModel.mainRewards.clearItems()
        self.viewModel.additionalRewards.clearItems()
        self._tooltipItems.clear()
        super(BaseRewardView, self).finalize()

    def _getEvents(self):
        return super(BaseRewardView, self)._getEvents() + ((self.viewModel.onClose, self._onClose),)

    def _composeRewards(self, bonuses):
        raise NotImplementedError

    def _setResources(self, vm):
        raise NotImplementedError

    def _setRewards(self, vm, rewards):
        raise NotImplementedError
