# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/tooltips/early_access_compensation_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_compensation_tooltip_model import EarlyAccessCompensationTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from gui.shared.money import Currency
from gui.impl.gen import R

class EarlyAccessCompensationTooltip(ViewImpl):
    __slots__ = ()
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessCompensationTooltip())
        settings.model = EarlyAccessCompensationTooltipModel()
        super(EarlyAccessCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessCompensationTooltip, self)._onLoading(*args, **kwargs)
        compensationAmount = self.__earlyAccessCtrl.getTokenCompensation(Currency.CREDITS).credits
        with self.getViewModel().transaction() as model:
            model.setTokenCreditsCompensation(compensationAmount)
