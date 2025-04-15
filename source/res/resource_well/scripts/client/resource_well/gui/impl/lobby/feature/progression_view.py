# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/progression_view.py
import typing
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.top_panel_tabs import PERSONAL_NUMBER_STYLE_TABS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showHangar, showBrowserOverlayView
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.processors import ResourceWellTakeBackProcessor
from resource_well.gui.feature.resource_well_helpers import isEventEndingsSoon, getRewardStyle, getSerialNumber
from resource_well.gui.impl.gen.view_models.views.lobby.progression_view_model import ProgressionViewModel, ProgressionState
from resource_well.gui.impl.gen.view_models.views.lobby.reward_model import RewardModel, RewardState
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from resource_well.gui.impl.lobby.feature.tooltips.progress_tooltip import ProgressTooltip
from resource_well.gui.impl.lobby.feature.tooltips.refund_resources_tooltip import RefundResourcesTooltip
from resource_well.gui.impl.lobby.feature.tooltips.serial_number_tooltip import SerialNumberTooltip
from resource_well.gui.shared.event_dispatcher import showResourceWellVehiclePreview, showResourceWellProgressionWindow, showResourcesLoadingWindow
from skeletons.gui.resource_well import IResourceWellController
if typing.TYPE_CHECKING:
    from resource_well.helpers.server_settings import RewardConfig
    from gui.shared.gui_items.Vehicle import Vehicle
_FULL_PROGRESS = 100

class ProgressionView(ViewImpl):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, layoutID, backCallback):
        settings = ViewSettings(R.views.resource_well.lobby.feature.ProgressionView(), model=ProgressionViewModel(), flags=ViewFlags.LOBBY_SUB_VIEW)
        self.__backCallback = backCallback
        super(ProgressionView, self).__init__(settings)
        self.__notifier = None
        self.__selectedRewardId = ''
        return

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.resource_well.lobby.feature.tooltips.SerialNumberTooltip():
            return SerialNumberTooltip(parentLayout=self.layoutID)
        if contentID == R.views.resource_well.lobby.feature.tooltips.RefundResourcesTooltip():
            return RefundResourcesTooltip()
        return ProgressTooltip(progress=self.viewModel.getProgression()) if contentID == R.views.resource_well.lobby.feature.tooltips.ProgressTooltip() else super(ProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ProgressionView, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        self.__selectedRewardId = self.__getCurrentRewardID()
        self.__notifier = SimpleNotifier(self.__getReminderTimeLeft, self.__updateEventTime)
        self.__updateModel()

    def _finalize(self):
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__resourceWell.stopNumberRequesters()
        super(ProgressionView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showEventInfo),
         (self.viewModel.onPreview, self.__showPreview),
         (self.viewModel.onHangarShow, self.__showHangar),
         (self.viewModel.onRewardSelected, self.__selectReward),
         (self.viewModel.onResourcesContribute, self.__contributeResources),
         (self.viewModel.onResourcesReturn, self.__onResourcesReturn),
         (self.viewModel.onClose, self.__close),
         (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated),
         (self.__resourceWell.onEventUpdated, self.__onEventUpdated),
         (self.__resourceWell.onSettingsChanged, self.__onSettingsChanged))

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillEventInfo(model=model)
            self.__fillProgression(model=model)
            self.__updateEventTime(model=model)
            self.__fillRewards(model.getRewards())

    def __getCurrentRewardID(self):
        availableReward = self.__resourceWell.getAvailableRewards()
        lastAvailableReward = availableReward[0] if len(availableReward) == 1 else ''
        return self.__resourceWell.getCurrentRewardID() or lastAvailableReward or self.__selectedRewardId

    @replaceNoneKwargsModel
    def __updateEventTime(self, model=None):
        model.setEndDate(round(time_utils.makeLocalServerTime(self.__resourceWell.config.finishTime), -1))
        isEventEnding = isEventEndingsSoon(resourceWell=self.__resourceWell)
        model.setIsEventEndingSoon(isEventEnding)
        model.setTimeLeft(self.__resourceWell.config.finishTime - time_utils.getServerUTCTime())
        if isEventEnding:
            self.__notifier.stopNotification()
        else:
            self.__notifier.startNotification()

    @replaceNoneKwargsModel
    def __fillEventInfo(self, model=None):
        model.setEventMode(self.__resourceWell.getPurchaseMode())

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        currentRewardID = self.__getCurrentRewardID()
        model.setCurrentRewardId(currentRewardID)
        model.setProgressionState(self.__getProgressionState())
        if currentRewardID:
            currentPoints = self.__resourceWell.getCurrentPoints()
            maxPoints = self.__resourceWell.config.getRewardConfig(currentRewardID).points
            model.setProgression(_FULL_PROGRESS * currentPoints / (maxPoints or _FULL_PROGRESS))

    def __fillRewards(self, rewards):
        rewards.clear()
        for rewardID, reward in self.__resourceWell.config.getSortedRewardsByOrder():
            rewards.addViewModel(self.__getRewardModel(rewardID, reward))

        rewards.invalidate()

    def __fillSelectReward(self, rewardID=None):
        self.__selectedRewardId = rewardID or ''
        self.__fillProgression()

    def __getRewardModel(self, rewardID, reward):
        rewardVehicle = self.__resourceWell.getRewardVehicle(rewardID)
        model = RewardModel()
        model.setRewardId(rewardID)
        model.setHasStyle(reward.isSerial)
        model.setVehiclesLeftCount(self.__resourceWell.getRewardLeftCount(rewardID))
        model.setVehiclesLimit(reward.limit)
        model.setState(self.__getRewardState(rewardID, rewardVehicle))
        if reward.isSerial:
            model.setPersonalNumber(getSerialNumber(rewardID, resourceWell=self.__resourceWell))
        fillVehicleInfo(model.vehicleInfo, rewardVehicle)
        return model

    def __getRewardState(self, rewardID, rewardVehicle):
        if self.__resourceWell.isRewardReceived(rewardID):
            return RewardState.ALREADY_RECEIVED
        if rewardVehicle.isInInventory:
            return RewardState.ALREADY_IN_GARAGE
        if self.__resourceWell.getRewardLeftCount(rewardID) == 0:
            return RewardState.SOLD_OUT
        if not self.__resourceWell.isRewardAvailable(rewardID):
            return RewardState.NOT_AVAILABLE
        return RewardState.COUNT_NOT_AVAILABLE if not self.__resourceWell.isRewardCountAvailable(rewardID) else RewardState.ACTIVE

    def __getProgressionState(self):
        if self.__resourceWell.isForbiddenAccount():
            return ProgressionState.FORBIDDEN
        if self.__resourceWell.isRewardsOver():
            return ProgressionState.NOVEHICLES
        return ProgressionState.ACTIVE if self.__resourceWell.getCurrentPoints() else ProgressionState.NOPROGRESS

    def __close(self):
        if callable(self.__backCallback):
            self.__backCallback()
        else:
            showHangar()

    def __showHangar(self):
        showHangar()
        self.destroyWindow()

    @args2params(str)
    def __showPreview(self, rewardId):
        rewardConfig = self.__resourceWell.config.getRewardConfig(rewardId)
        previewStyle = getRewardStyle(rewardId, resourceWell=self.__resourceWell) if rewardConfig.isSerial else None
        vehicle = self.__resourceWell.getRewardVehicle(rewardId)
        purchaseMode = self.__resourceWell.getPurchaseMode()
        if purchaseMode == PurchaseMode.SEQUENTIAL_PRODUCT:
            style = previewStyle or (getRewardStyle(rewardConfig.availableAfter, resourceWell=self.__resourceWell) if rewardConfig.availableAfter else None)
            topPanelData = {'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
             'tabIDs': PERSONAL_NUMBER_STYLE_TABS,
             'currentTabID': TabID.PERSONAL_NUMBER_VEHICLE if previewStyle else TabID.BASE_VEHICLE}
        else:
            style = previewStyle
            topPanelData = None
        showResourceWellVehiclePreview(vehicle.intCD, rewardId, style, previewStyle, self.__previewCallback, topPanelData)
        return

    @args2params(str)
    def __contributeResources(self, rewardId):
        showResourcesLoadingWindow(rewardId)

    @args2params(str)
    def __selectReward(self, rewardId):
        currentRewardID = self.__resourceWell.getCurrentRewardID()
        if currentRewardID and currentRewardID != rewardId:
            self.__extractResources(rewardId)
        if not currentRewardID:
            self.__fillSelectReward(rewardId)

    @args2params(str)
    def __onResourcesReturn(self, rewardId):
        self.__extractResources(rewardId)

    def __previewCallback(self):
        showResourceWellProgressionWindow(backCallback=self.__backCallback)

    @adisp_process
    def __extractResources(self, rewardID):
        result = yield ResourceWellTakeBackProcessor(rewardID=rewardID).request()
        if result.success:
            self.__fillSelectReward(rewardID)

    def __showEventInfo(self):
        showBrowserOverlayView(self.__resourceWell.config.infoPageUrl, VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW)

    def __onEventUpdated(self):
        if not self.__resourceWell.isActive():
            showHangar()
            return
        with self.viewModel.transaction() as model:
            self.__updateEventTime(model=model)
            self.__fillProgression(model=model)
            self.__fillRewards(model.getRewards())

    def __onSettingsChanged(self):
        if not self.__resourceWell.isActive():
            self.__close()
            return
        self.__updateModel()

    def __getReminderTimeLeft(self):
        return max(0, self.__resourceWell.config.remindTime - time_utils.getServerUTCTime())

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            self.__fillRewards(model.getRewards())
