# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from portal.gui.impl.gen.view_models.views.lobby.tooltips.banner_tooltip_model import BannerTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController

class BannerTooltip(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IPortalEventController)

    def __init__(self):
        settings = ViewSettings(R.views.portal.lobby.tooltips.BannerTooltip())
        settings.model = BannerTooltipModel()
        super(BannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BannerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BannerTooltip, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillModel(model)

    def __fillModel(self, model):
        model.setPerformance(self.__gameEventController.getPerformanceGroup())
        start, end = self.__gameEventController.getSeasonStartEndDate()
        model.setStartDate(start)
        model.setEndDate(end)
