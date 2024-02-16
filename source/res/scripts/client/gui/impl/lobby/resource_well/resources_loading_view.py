# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/resources_loading_view.py
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.auxiliary.resource_well_helper import fillVehicleCounter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.resource_model import ResourceModel
from gui.impl.gen.view_models.views.lobby.resource_well.resources_loading_view_model import ResourcesLoadingViewModel, ProgressionState
from gui.impl.gen.view_models.views.lobby.resource_well.resources_tab_model import ResourcesTabModel
from gui.impl.lobby.resource_well.tooltips.progress_tooltip import ProgressTooltip
from gui.impl.lobby.resource_well.tooltips.max_progress_tooltip import MaxProgressTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.resource_well import resource_well_constants
from gui.resource_well.resource import processResourcesConfig
from gui.resource_well.resource_well_constants import ResourceType, UNAVAILABLE_REWARD_ERROR, RESOURCE_WELL_PDATA_KEY
from gui.resource_well.resource_well_helpers import getProgressionState, getAvailableRewardData
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar, showResourceWellNoVehiclesConfirm
from gui.shared.gui_items.processors.resource_well import ResourceWellPutProcessor, ResourceWellNoTopVehiclesProcessor
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.shared import IItemsCache
_FULL_PROGRESS = 100
_PROGRESSION_STATE_MAPPING = {resource_well_constants.ProgressionState.ACTIVE: ProgressionState.ACTIVE,
 resource_well_constants.ProgressionState.NO_PROGRESS: ProgressionState.NOPROGRESS,
 resource_well_constants.ProgressionState.NO_VEHICLES: ProgressionState.NOVEHICLES}

class ResourcesLoadingView(ViewImpl):
    __slots__ = ('__resources', '__tooltips')
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = ResourcesLoadingViewModel()
        super(ResourcesLoadingView, self).__init__(settings)
        self.__resources = processResourcesConfig(self.__resourceWell.getResources())
        self.__tooltips = []

    @property
    def viewModel(self):
        return super(ResourcesLoadingView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.resource_well.tooltips.ProgressTooltip():
            return ProgressTooltip(progress=self.viewModel.getProgression(), diff=event.getArgument('progressDiff'))
        return MaxProgressTooltip(currentValue=event.getArgument('currentValue'), maxValue=event.getArgument('maxValue'), resourceType=event.getArgument('type')) if contentID == R.views.lobby.resource_well.tooltips.MaxProgressTooltip() else super(ResourcesLoadingView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__tooltips[int(event.getArgument('tooltipId'))]
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
            return super(ResourcesLoadingView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(ResourcesLoadingView, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            self.__fillTabs(model=model)
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            self.__updateLoadingError(isError=False, model=model)

    def _onLoaded(self, *args, **kwargs):
        super(ResourcesLoadingView, self)._onLoaded(*args, **kwargs)
        g_eventBus.handleEvent(events.ResourceWellLoadingViewEvent(events.ResourceWellLoadingViewEvent.LOAD), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        g_eventBus.handleEvent(events.ResourceWellLoadingViewEvent(events.ResourceWellLoadingViewEvent.DESTROY), EVENT_BUS_SCOPE.LOBBY)
        self.__resourceWell.stopNumberRequesters()
        super(ResourcesLoadingView, self)._finalize()

    def _getCallbacks(self):
        return (('stats.gold', self.__updateCurrencies),
         ('stats.credits', self.__updateCurrencies),
         ('stats.crystal', self.__updateCurrencies),
         ('stats.freeXP', self.__updateCurrencies),
         ('blueprints', self.__updateBlueprints),
         ('premium', self.__updatePremiums))

    def _getEvents(self):
        return ((self.viewModel.loadResources, self.__loadResources),
         (self.viewModel.showHangar, self.__showHangar),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated),
         (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated),
         (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated))

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        currentPoints = self.__resourceWell.getCurrentPoints()
        maxPoints = self.__resourceWell.getMaxPoints()
        model.setProgression(_FULL_PROGRESS * currentPoints / (maxPoints or _FULL_PROGRESS))
        model.setProgressionState(_PROGRESSION_STATE_MAPPING.get(getProgressionState(), ProgressionState.NOVEHICLES))

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
        rateCof = self.__resourceWell.getMaxPoints() / _FULL_PROGRESS
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

    def __updatePremiums(self, *_):
        self.__updateResourceModels(ResourceType.PREMIUMS.value)

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
        rewardID, isTop = getAvailableRewardData()
        processor = ResourceWellPutProcessor(resources, rewardID)
        result = yield processor.request()
        if not result.success and result.userMsg == UNAVAILABLE_REWARD_ERROR and isTop:
            self.__showNoTopRewardConfirm(resources)
        else:
            self.__onLoadResources(result, processor.responseCtx)

    @adisp_process
    def __showNoTopRewardConfirm(self, resources):
        self.__updateLoadingError(isError=True)
        processor = ResourceWellNoTopVehiclesProcessor(resources)
        result = yield processor.request()
        self.__onLoadResources(result, processor.responseCtx)

    def __showNoRewardsConfirm(self):
        self.__updateLoadingError(isError=True)
        showResourceWellNoVehiclesConfirm()

    def __onLoadResources(self, result, responseCtx):
        if not result.success and result.userMsg == UNAVAILABLE_REWARD_ERROR:
            self.__showNoRewardsConfirm()
        self.__updateLoadingError(isError=not result.success and not responseCtx.get('isUserCancelAction', False))

    @replaceNoneKwargsModel
    def __updateLoadingError(self, isError, model=None):
        model.setIsLoadingError(isError)

    def __showHangar(self):
        self.destroy()
        showHangar()

    def __onClientUpdated(self, diff, _):
        if RESOURCE_WELL_PDATA_KEY in diff and not self.__resourceWell.isCompleted():
            self.__fillProgression()
            self.__fillTabs()

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.destroy()
            showHangar()


class ResourcesLoadingWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self):
        super(ResourcesLoadingWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ResourcesLoadingView(R.views.lobby.resource_well.ResourcesLoadingView()))
