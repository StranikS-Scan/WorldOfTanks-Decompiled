# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_menu_gift_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_menu_gift_tooltip_model import NyMenuGiftTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.new_year import INewYearController

class NyMenuGiftTooltip(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMenuGiftTooltip(), model=NyMenuGiftTooltipModel())
        super(NyMenuGiftTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMenuGiftTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setCoinsCount(self.__nyController.currencies.getCoinsCount())
