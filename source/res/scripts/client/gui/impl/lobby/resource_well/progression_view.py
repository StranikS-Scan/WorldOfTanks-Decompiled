# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/progression_view.py
from PlayerEvents import g_playerEvents
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.top_panel_tabs import PERSONAL_NUMBER_STYLE_TABS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.progression_view_model import ProgressionViewModel, ProgressionState
from gui.impl.gen.view_models.views.lobby.resource_well.reward_model import RewardModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.lobby.resource_well.tooltips.progress_tooltip import ProgressTooltip
from gui.impl.lobby.resource_well.tooltips.refund_resources_tooltip import RefundResourcesTooltip
from gui.impl.lobby.resource_well.tooltips.serial_number_tooltip import SerialNumberTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.resource_well import resource_well_constants
from gui.resource_well.resource_well_constants import RESOURCE_WELL_PDATA_KEY
from gui.resource_well.resource_well_helpers import isEventEndingsSoon, getProgressionState, getRewardStyle
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared.event_dispatcher import showHangar, showResourcesLoadingWindow, showResourceWellVehiclePreview, showResourceWellProgressionWindow, showBrowserOverlayView
from gui.shared.gui_items.processors.resource_well import ResourceWellTakeBackProcessor
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD
from uilogging.resource_well.constants import ParentScreens
from uilogging.resource_well.loggers import ResourceWellMainScreenLogger
_FULL_PROGRESS = 100
_PROGRESSION_STATE_MAPPING = {resource_well_constants.ProgressionState.ACTIVE: ProgressionState.ACTIVE,
 resource_well_constants.ProgressionState.NO_PROGRESS: ProgressionState.NOPROGRESS,
 resource_well_constants.ProgressionState.NO_VEHICLES: ProgressionState.NOVEHICLES,
 resource_well_constants.ProgressionState.FORBIDDEN: ProgressionState.FORBIDDEN}

class ProgressionView(ViewImpl):
    __slots__ = ('__notifier', '__backCallback')
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, layoutID, backCallback):
        settings = ViewSettings(R.views.lobby.resource_well.ProgressionView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionViewModel()
        self.__backCallback = backCallback
        super(ProgressionView, self).__init__(settings)
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.resource_well.tooltips.SerialNumberTooltip():
            return SerialNumberTooltip(parentLayout=self.layoutID)
        if contentID == R.views.lobby.resource_well.tooltips.RefundResourcesTooltip():
            return RefundResourcesTooltip()
        return ProgressTooltip(progress=self.viewModel.getProgression()) if contentID == R.views.lobby.resource_well.tooltips.ProgressTooltip() else super(ProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ProgressionView, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        self.__notifier = SimpleNotifier(self.__getReminderTimeLeft, self.__updateEventTime)
        self.__updateModel()
        ResourceWellMainScreenLogger().onViewOpened(getProgressionState())

    def _finalize(self):
        self.__notifier.stopNotification()
        self.__resourceWell.stopNumberRequesters()
        super(ProgressionView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showEventInfo),
         (self.viewModel.onPreview, self.__showPreview),
         (self.viewModel.onHangarShow, self.__showHangar),
         (self.viewModel.onResourcesContribute, self.__contributeResources),
         (self.viewModel.onResourcesReturn, self.__extractResources),
         (self.viewModel.onClose, self.__close),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated),
         (self.__resourceWell.onNumberRequesterUpdated, self.__onNumberRequesterUpdated),
         (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated))

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillEventInfo(model=model)
            self.__fillProgression(model=model)
            self.__updateEventTime(model=model)
            self.__fillVehicleName(model=model)
            self.__fillRewards(model.getRewards())

    @replaceNoneKwargsModel
    def __updateEventTime(self, model=None):
        model.setEndDate(round(time_utils.makeLocalServerTime(self.__resourceWell.getFinishTime()), -1))
        isEventEnding = isEventEndingsSoon(resourceWell=self.__resourceWell)
        model.setIsEventEndingSoon(isEventEnding)
        model.setTimeLeft(self.__resourceWell.getFinishTime() - time_utils.getServerUTCTime())
        if isEventEnding:
            self.__notifier.stopNotification()
        else:
            self.__notifier.startNotification()

    @replaceNoneKwargsModel
    def __fillEventInfo(self, model=None):
        model.setTopRewardPlayersCount(self.__resourceWell.getRewardLimit(isTop=True))
        model.setRegularRewardVehiclesCount(self.__resourceWell.getRewardLimit(isTop=False))

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        model.setProgressionState(_PROGRESSION_STATE_MAPPING.get(getProgressionState()))
        currentPoints = self.__resourceWell.getCurrentPoints()
        maxPoints = self.__resourceWell.getMaxPoints()
        model.setProgression(_FULL_PROGRESS * currentPoints / (maxPoints or _FULL_PROGRESS))

    def __fillVehicleName(self, model=None):
        vehicle = getVehicleByIntCD(self.__resourceWell.getRewardVehicle())
        model.setVehicleName(vehicle.userName)

    def __fillRewards(self, rewards):
        rewards.clear()
        rewards.addViewModel(self.__getRewardModel(isTop=True))
        rewards.addViewModel(self.__getRewardModel(isTop=False))
        rewards.invalidate()

    def __getRewardModel(self, isTop):
        model = RewardModel()
        model.setIsTop(isTop)
        model.setIsEnabled(self.__resourceWell.isRewardEnabled(isTop))
        model.setVehiclesLeftCount(self.__resourceWell.getRewardLeftCount(isTop))
        model.setIsCountAvailable(self.__resourceWell.isRewardCountAvailable(isTop))
        fillVehicleInfo(model.vehicleInfo, getVehicleByIntCD(self.__resourceWell.getRewardVehicle()))
        return model

    def __close(self):
        if callable(self.__backCallback):
            self.__backCallback()
        else:
            showHangar()

    def __showHangar(self):
        showHangar()
        self.destroyWindow()

    def __showPreview(self, args):
        isStyled = args.get('isStyled', False)
        style = getRewardStyle(resourceWell=self.__resourceWell)
        vehicleCD = self.__resourceWell.getRewardVehicle()
        topPanelData = {'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
         'tabIDs': PERSONAL_NUMBER_STYLE_TABS,
         'currentTabID': TabID.PERSONAL_NUMBER_VEHICLE if isStyled else TabID.BASE_VEHICLE}
        showResourceWellVehiclePreview(vehicleCD, style, self.__previewCallback, topPanelData)

    def __previewCallback(self):
        showResourceWellProgressionWindow(backCallback=self.__backCallback)

    def __contributeResources(self):
        showResourcesLoadingWindow(ParentScreens.MAIN_SCREEN)

    @process
    def __extractResources(self):
        yield ResourceWellTakeBackProcessor().request()

    def __showEventInfo(self):
        showBrowserOverlayView(GUI_SETTINGS.resourceWell.get('infoPage'), VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            showHangar()
        else:
            self.__updateEventTime()

    def __onEventSettingsUpdated(self):
        if not self.__resourceWell.isActive():
            self.__close()
            return
        self.__updateModel()

    def __getReminderTimeLeft(self):
        return max(0, self.__resourceWell.getReminderTime() - time_utils.getServerUTCTime())

    def __onClientUpdated(self, diff, _):
        if RESOURCE_WELL_PDATA_KEY in diff:
            if not self.__resourceWell.isCompleted():
                self.__fillProgression()

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model=model)
            self.__fillRewards(model.getRewards())
