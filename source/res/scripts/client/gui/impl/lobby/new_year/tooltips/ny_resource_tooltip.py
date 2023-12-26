# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_tooltip_model import NyResourceTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from new_year.ny_resource_collecting_helper import getResourceCollectings
from skeletons.new_year import INewYearController

class NyResourceTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceTooltip())
        settings.model = NyResourceTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyResourceTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceTooltip, self).getViewModel()

    def _onLoading(self, resourceType, *args, **kwargs):
        super(NyResourceTooltip, self)._onLoading()
        value = dependency.instance(INewYearController).currencies.getResouceBalance(resourceType)
        with self.viewModel.transaction() as model:
            model.setFirstCollectAmount(getResourceCollectings(resourceType=resourceType, isExtraCollect=False))
            model.setSecondCollectAmount(getResourceCollectings(resourceType=resourceType, isExtraCollect=True))
            model.resource.setType(resourceType)
            model.resource.setValue(value)
