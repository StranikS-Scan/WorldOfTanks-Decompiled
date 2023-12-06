# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_marketplace_token_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_marketplace_token_tooltip_model import NyMarketplaceTokenTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController

class NyMarketplaceTokenTooltip(ViewImpl):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip())
        settings.model = NyMarketplaceTokenTooltipModel()
        super(NyMarketplaceTokenTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMarketplaceTokenTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyMarketplaceTokenTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setMarketplaceIsActive(self.__nyController.isMaxAtmosphereLevel())
