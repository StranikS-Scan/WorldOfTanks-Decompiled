# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_resource_well.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelWellMeta import VehiclePreviewBottomPanelWellMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.buying_panel.well_panel_model import WellPanelModel
from gui.impl.pub import ViewImpl
from gui.resource_well.resource_well_helpers import isForbiddenAccount
from gui.shared.event_dispatcher import showResourcesLoadingWindow
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD
from uilogging.resource_well.constants import ParentScreens

class VehiclePreviewBottomPanelResourceWell(VehiclePreviewBottomPanelWellMeta):

    def _makeInjectView(self, *args):
        return _ResourceWellPanelView()


class _ResourceWellPanelView(ViewImpl):
    __slots__ = ()
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.WellPanel())
        settings.flags = ViewFlags.COMPONENT
        settings.model = WellPanelModel()
        super(_ResourceWellPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(_ResourceWellPanelView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(_ResourceWellPanelView, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        self.__updateModel()

    def _finalize(self):
        self.__resourceWell.stopNumberRequesters()
        super(_ResourceWellPanelView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onAction, self.__showResourcesLoading), (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated))

    def __showResourcesLoading(self):
        showResourcesLoadingWindow(ParentScreens.VEHICLE_PREVIEW)

    def __updateModel(self):
        resourceWell = self.__resourceWell
        isRewardLeft = resourceWell.getRewardLeftCount(isTop=True) or resourceWell.getRewardLeftCount(isTop=False)
        isVisible = resourceWell.isActive() and not isForbiddenAccount(resourceWell=resourceWell) and not resourceWell.isCompleted() and isRewardLeft
        with self.viewModel.transaction() as model:
            model.setIsVisible(isVisible)
            model.setTopRewardsCount(self.__resourceWell.getRewardLimit(isTop=True))
            model.setRegularRewardsCount(self.__resourceWell.getRewardLimit(isTop=False))
            model.setVehicleName(getVehicleByIntCD(self.__resourceWell.getRewardVehicle()).userName)

    def __onNumberRequesterUpdated(self):
        self.__updateModel()
