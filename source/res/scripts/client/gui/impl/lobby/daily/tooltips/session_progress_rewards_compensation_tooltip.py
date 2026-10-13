# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/session_progress_rewards_compensation_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.tooltips.session_progress_rewards_compensation_tooltip_model import SessionProgressRewardsCompensationTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.session_progress_rewards.session_progress_rewards_bonus_packers import getSessionProgressRewardsCompensationTooltipPacker

class SessionProgressRewardsCompensationTooltip(ViewImpl):
    __slots__ = ('__bonusBefore', '__bonusAfter')

    def __init__(self, itemBefore, itemAfter):
        settings = ViewSettings(R.views.lobby.daily.tooltips.SessionProgressRewardsCompensationTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = SessionProgressRewardsCompensationTooltipModel()
        self.__bonusBefore = [itemBefore]
        self.__bonusAfter = [itemAfter]
        super(SessionProgressRewardsCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SessionProgressRewardsCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SessionProgressRewardsCompensationTooltip, self)._onLoading(*args, **kwargs)
        packer = getSessionProgressRewardsCompensationTooltipPacker()
        with self.viewModel.transaction() as model:
            self.__fillItem(model.getItemBefore(), self.__bonusBefore, packer)
            self.__fillItem(model.getItemAfter(), self.__bonusAfter, packer)

    def __fillItem(self, bonusModelsList, bonuses, packer):
        packBonusModelAndTooltipData(bonuses, bonusModelsList, None, packer)
        bonusModelsList.invalidate()
        return
