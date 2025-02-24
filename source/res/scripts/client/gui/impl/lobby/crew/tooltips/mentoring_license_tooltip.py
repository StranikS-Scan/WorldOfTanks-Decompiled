# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/mentoring_license_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.mentoring_license_tooltip_model import MentoringLicenseTooltipModel
from gui.impl.pub import ViewImpl

class MentoringLicenseTooltip(ViewImpl):
    __slots__ = ('__amount',)

    def __init__(self, amount):
        self.__amount = amount
        settings = ViewSettings(R.views.lobby.crew.tooltips.MentoringLicenseTooltip(), model=MentoringLicenseTooltipModel())
        super(MentoringLicenseTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MentoringLicenseTooltip, self).getViewModel()

    def _onLoading(self):
        self.viewModel.setAmount(self.__amount)
