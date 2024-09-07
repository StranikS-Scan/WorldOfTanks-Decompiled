# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/tooltips/compensation_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from winback.gui.impl.gen.view_models.views.lobby.tooltips.compensation_tooltip_model import CompensationTooltipModel
from winback.gui.impl.lobby.views.winback_bonus_packer import packWinbackBonusModelAndTooltipData, getWinbackBonusPacker

class CompensationTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.winback.lobby.tooltips.CompensationTooltip(), model=CompensationTooltipModel(), args=args, kwargs=kwargs)
        super(CompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CompensationTooltip, self).getViewModel()

    def _onLoading(self, isDiscount, level, bonuses):
        super(CompensationTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsDiscount(isDiscount)
            model.setVehicleLevel(level)
            rewards = model.getRewards()
            rewards.clear()
            self.__fillItem(bonuses, rewards)

    @staticmethod
    def __fillItem(bonuses, bonusModelsList):
        packWinbackBonusModelAndTooltipData(bonuses, getWinbackBonusPacker(), bonusModelsList)
        for bonusModel in bonusModelsList:
            bonusModel.setIsCompensation(False)

        bonusModelsList.invalidate()
