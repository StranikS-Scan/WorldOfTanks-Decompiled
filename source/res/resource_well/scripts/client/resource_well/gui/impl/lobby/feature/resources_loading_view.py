# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/resources_loading_view.py
import logging
from adisp import adisp_process
from frameworks.wulf import ViewSettings, WindowFlags, ViewStatus
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from resource_well.gui.feature.constants import ResourceType, UNAVAILABLE_REWARD_ERROR, PurchaseMode
from resource_well.gui.feature.processors import PutResourcesProcessor, NextSerialVehicleProcessor
from resource_well.gui.feature.resource import processResourcesConfig
from resource_well.gui.feature.resource_well_helpers import fillVehicleCounter, getNextSerialRewardID
from resource_well.gui.impl.gen.view_models.views.lobby.resource_model import ResourceModel
from resource_well.gui.impl.gen.view_models.views.lobby.resources_loading_view_model import ResourcesLoadingViewModel, ProgressionState
from resource_well.gui.impl.gen.view_models.views.lobby.resources_tab_model import ResourcesTabModel
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from resource_well.gui.impl.lobby.feature.tooltips.max_progress_tooltip import MaxProgressTooltip
from resource_well.gui.impl.lobby.feature.tooltips.progress_tooltip import ProgressTooltip
from resource_well.gui.shared import events
from resource_well.gui.shared.event_dispatcher import showResourceWellNoVehiclesConfirm
from shared_utils import findFirst
from skeletons.gui.resource_well import IResourceWellController
_logger = logging.getLogger(__name__)
_FULL_PROGRESS = 100

class ResourcesLoadingView(ViewImpl):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID):
        settings = ViewSettings(R.views.resource_well.lobby.feature.ResourcesLoadingView(), model=ResourcesLoadingViewModel())
        super(ResourcesLoadingView, self).__init__(settings)
        self.__rewardID = rewardID
        self.__rewardConfig = self.__resourceWell.config.getRewardConfig(rewardID)
        self.__resources = processResourcesConfig(self.__rewardConfig.resources)
        self.__tooltips = []

    @property
    def viewModel(self):
        return super(ResourcesLoadingView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.resource_well.lobby.feature.tooltips.ProgressTooltip():
            return ProgressTooltip(progress=self.viewModel.getProgression(), diff=event.getArgument('progressDiff'))
        return MaxProgressTooltip(currentValue=event.getArgument('currentValue'), maxValue=event.getArgument('maxValue'), resourceType=event.getArgument('type')) if contentID == R.views.resource_well.lobby.feature.tooltips.MaxProgressTooltip() else super(ResourcesLoadingView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ResourcesLoadingView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips[int(tooltipId)]

    def _onLoading(self, *args, **kwargs):
        super(ResourcesLoadingView, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        self.__updateModel()

    def _onLoaded(self, *args, **kwargs):
        super(ResourcesLoadingView, self)._onLoaded(*args, **kwargs)
        g_eventBus.handleEvent(events.ResourceWellLoadingViewEvent(events.ResourceWellLoadingViewEvent.LOAD), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__resourceWell.stopNumberRequesters()
        self.__rewardConfig = None
        self.__resources = None
        self.__tooltips = None
        g_eventBus.handleEvent(events.ResourceWellLoadingViewEvent(events.ResourceWellLoadingViewEvent.DESTROY), EVENT_BUS_SCOPE.LOBBY)
        super(ResourcesLoadingView, self)._finalize()
        return

    def _getCallbacks(self):
        return (('stats.gold', self.__updateCurrencies),
         ('stats.credits', self.__updateCurrencies),
         ('stats.crystal', self.__updateCurrencies),
         ('stats.freeXP', self.__updateCurrencies),
         ('blueprints', self.__updateBlueprints))

    def _getEvents(self):
        return ((self.viewModel.loadResources, self.__loadResources),
         (self.viewModel.showHangar, self.__showHangar),
         (self.viewModel.close, self.__close),
         (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated),
         (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated),
         (self.__resourceWell.onSettingsChanged, self.__onEventStateUpdated))

    def __isDestroyed(self):
        return self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING) or self.viewModel is None

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            self.__fillTabs(model=model)
            fillVehicleInfo(model.vehicleInfo, self.__resourceWell.getRewardVehicle(self.__rewardID))
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            self.__updateLoadingError(isError=False, model=model)

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        currentPoints = self.__resourceWell.getCurrentPoints()
        maxPoints = self.__rewardConfig.points
        isRewardAvailable = self.__resourceWell.isRewardAvailable(self.__rewardID)
        isTwoParallelMode = self.__resourceWell.getPurchaseMode() is PurchaseMode.TWO_PARALLEL_PRODUCTS
        if isTwoParallelMode and not isRewardAvailable or self.__resourceWell.isRewardsOver():
            state = ProgressionState.NOVEHICLES
        elif self.__resourceWell.getCurrentPoints():
            state = ProgressionState.ACTIVE
        else:
            state = ProgressionState.NOPROGRESS
        model.setProgressionState(state)
        model.setProgression(_FULL_PROGRESS * currentPoints / (maxPoints or _FULL_PROGRESS))

    @replaceNoneKwargsModel
    def __fillTabs(self, model=None):
        tabModels = model.getResourcesTabs()
        tabModels.clear()
        for resourceType, resources in self.__resources.iteritems():
            tabModel = ResourcesTabModel()
            tabModel.setType(resourceType)
            self.__fillResources(tabModel.getResources(), resources)
            tabModels.addViewModel(tabModel)

        tabModels.invalidate()

    def __fillResources(self, resourceModels, resources):
        rateCof = self.__rewardConfig.points / _FULL_PROGRESS
        resourceModels.clear()
        index = len(self.__tooltips)
        for tooltipId, resource in enumerate(resources, index):
            resourceModel = ResourceModel()
            self.__fillResource(resourceModel, resource, rateCof)
            resourceModel.setTooltipId(str(tooltipId))
            resourceModels.addViewModel(resourceModel)

        resourceModels.invalidate()

    def __fillResource(self, resourceModel, resource, rateCof):
        resourceModel.setLimit(resource.limit)
        resourceModel.setRate(rateCof / resource.rate)
        resourceModel.setInventoryCount(resource.inventoryCount)
        resourceModel.setType(resource.guiName)
        resourceModel.setBalance(resource.balance)
        self.__tooltips.append(resource.tooltip)

    def __updateCurrencies(self, *_):
        self.__updateResourceModels(ResourceType.CURRENCY.value)

    def __updateBlueprints(self, *_):
        self.__updateResourceModels(ResourceType.BLUEPRINTS.value)

    def __updateResourceModels(self, resourceType):
        with self.viewModel.transaction() as model:
            tabModel = findFirst(lambda tab: tab.getType() == resourceType, model.getResourcesTabs())
            for resourceModel in tabModel.getResources():
                resources = self.__resources[resourceType]
                resource = findFirst(lambda r, m=resourceModel: m.getType() == r.guiName, resources)
                resourceModel.setInventoryCount(resource.inventoryCount)

    @adisp_process
    def __loadResources(self, args):
        self.__updateLoadingError(isError=False)
        resources = {resource:int(count) for resource, count in args.iteritems()}
        mode = self.__resourceWell.getPurchaseMode()
        processor = PutResourcesProcessor(self.__rewardID, resources)
        result = yield processor.request()
        isRewardUnavailable = not result.success and result.userMsg == UNAVAILABLE_REWARD_ERROR
        if self.__isDestroyed():
            _logger.info('View is already destroyed.')
            return
        else:
            if isRewardUnavailable and mode is PurchaseMode.SEQUENTIAL_PRODUCT:
                nextRewardID = getNextSerialRewardID(self.__rewardID)
                if nextRewardID is not None:
                    self.__showNextSerialRewardConfirm(nextRewardID, resources)
                else:
                    self.__showNoRewardsConfirm()
            else:
                self.__onLoadResources(result, processor.responseCtx)
            return

    @adisp_process
    def __showNextSerialRewardConfirm(self, rewardID, resources):
        self.__updateLoadingError(isError=True)
        processor = NextSerialVehicleProcessor(rewardID, resources)
        result = yield processor.request()
        if self.__isDestroyed():
            _logger.info('View is already destroyed.')
            return
        if not result.success and processor.responseCtx.get('isUserCancelAction', False):
            self.destroyWindow()
            return
        self.__onLoadResources(result, processor.responseCtx, nextRewardID=rewardID)

    def __onLoadResources(self, result, responseCtx, nextRewardID=None):
        if not result.success and result.userMsg == UNAVAILABLE_REWARD_ERROR:
            self.__showNoRewardsConfirm()
            return
        elif result.success and result.auxData is not None and result.auxData.get('isRewardObtained', False):
            self.destroyWindow()
            return
        else:
            self.__updateLoadingError(isError=not result.success and not responseCtx.get('isUserCancelAction', False))
            if nextRewardID is not None:
                self.__rewardID = nextRewardID
                self.__updateModel()
            return

    def __showNoRewardsConfirm(self):
        self.__updateLoadingError(isError=True)
        showResourceWellNoVehiclesConfirm(parent=self.getParentWindow())

    @replaceNoneKwargsModel
    def __updateLoadingError(self, isError, model=None):
        model.setIsLoadingError(isError)

    def __showHangar(self):
        self.__close()
        showHangar()

    def __close(self):
        self.destroyWindow()

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            self.__fillTabs(model=model)
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.__showHangar()
            return
        self.__fillProgression()
        self.__fillTabs()


class ResourcesLoadingWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, rewardID):
        super(ResourcesLoadingWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ResourcesLoadingView(rewardID))
