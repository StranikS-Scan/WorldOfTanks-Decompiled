# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/buy_stages_footer_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.buy_stages_footer_tooltip_view_model import BuyStagesFooterTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class BuyStagesFooterTooltipView(ViewImpl):
    __slots__ = ('__isActive',)

    def __init__(self, isActive):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BuyStagesFooterTooltipView())
        settings.model = BuyStagesFooterTooltipViewModel()
        super(BuyStagesFooterTooltipView, self).__init__(settings)
        self.__isActive = isActive

    @property
    def viewModel(self):
        return super(BuyStagesFooterTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BuyStagesFooterTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setIsActive(self.__isActive)
