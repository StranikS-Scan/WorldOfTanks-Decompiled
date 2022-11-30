# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_shop_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_shop_tooltip_model import NyResourceShopTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController

class NyResourceShopTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceShopTooltip())
        settings.model = NyResourceShopTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyResourceShopTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceShopTooltip, self).getViewModel()

    def _onLoading(self, resourceType):
        super(NyResourceShopTooltip, self)._onLoading()
        value = dependency.instance(INewYearController).currencies.getResouceBalance(resourceType)
        with self.viewModel.transaction() as model:
            model.resource.setType(resourceType)
            model.resource.setValue(value)
