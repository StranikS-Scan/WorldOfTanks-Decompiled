# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/vehicle_preview_bottom_panel.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelWellMeta import VehiclePreviewBottomPanelWellMeta
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import convertPurchaseToEventMode
from resource_well.gui.impl.gen.view_models.views.lobby.well_panel_model import WellPanelModel
from resource_well.gui.shared.event_dispatcher import showResourcesLoadingWindow
from shared_utils import findFirst
from skeletons.gui.resource_well import IResourceWellController

class VehiclePreviewBottomPanel(VehiclePreviewBottomPanelWellMeta):

    def __init__(self):
        super(VehiclePreviewBottomPanel, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self, *args):
        self.__view = _BottomPanelView()
        return self.__view

    def setRewardID(self, rewardID):
        self.__view.setRewardID(rewardID)


class _BottomPanelView(ViewImpl):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.lobby.feature.WellPanel(), flags=ViewFlags.VIEW, model=WellPanelModel())
        super(_BottomPanelView, self).__init__(settings)
        self.__rewardID = None
        return

    @property
    def viewModel(self):
        return super(_BottomPanelView, self).getViewModel()

    def setRewardID(self, rewardID):
        self.__rewardID = rewardID

    def _onLoaded(self, *args, **kwargs):
        super(_BottomPanelView, self)._onLoaded(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self.__showResourcesLoading), (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated))

    def __showResourcesLoading(self):
        if self.__resourceWell.getPurchaseMode() is PurchaseMode.SEQUENTIAL_PRODUCT:
            if self.__resourceWell.isParentRewardAvailable(self.__rewardID):
                rewardID = self.__resourceWell.config.getRewardConfig(self.__rewardID).availableAfter
            elif self.__resourceWell.isRewardAvailable(self.__rewardID):
                rewardID = self.__rewardID
            else:
                otherReward = findFirst(lambda item: item[0] != self.__rewardID, self.__resourceWell.config.getSortedRewardsByOrder())
                rewardID = otherReward[0] if otherReward is not None else 'None'
        else:
            rewardID = self.__rewardID
        showResourcesLoadingWindow(rewardID)
        return

    def __updateModel(self):
        mode = self.__resourceWell.getPurchaseMode()
        isVisible = self.__resourceWell.isActive() and not self.__resourceWell.isForbiddenAccount()
        if mode == PurchaseMode.SEQUENTIAL_PRODUCT:
            isVisible &= not self.__resourceWell.isRewardsOver()
        else:
            isVisible &= self.__resourceWell.isRewardAvailable(self.__rewardID)
        if mode == PurchaseMode.TWO_PARALLEL_PRODUCTS:
            currentRewardID = self.__resourceWell.getCurrentRewardID()
            isVisible &= not currentRewardID or currentRewardID == self.__rewardID
        with self.viewModel.transaction() as model:
            model.setIsVisible(isVisible)
            model.setEventMode(convertPurchaseToEventMode(mode))
            model.setVehicleName(self.__resourceWell.getRewardVehicle(self.__rewardID).shortUserName)
            for rewardConfig in self.__resourceWell.config.rewards.itervalues():
                if rewardConfig.isSerial:
                    model.setTopRewardsCount(rewardConfig.limit)
                model.setRegularRewardsCount(rewardConfig.limit)

    def __onNumberRequesterUpdated(self):
        self.__updateModel()
