# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/completed_progression_view.py
from typing import Optional, Tuple
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar, showBrowserOverlayView
from helpers import dependency
from resource_well.gui.feature.resource_well_helpers import getSerialNumber, hasRequiredStyle
from resource_well.gui.impl.gen.view_models.views.lobby.completed_progression_view_model import CompletedProgressionViewModel
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from resource_well.gui.impl.lobby.feature.tooltips.serial_number_tooltip import SerialNumberTooltip
from shared_utils import first
from skeletons.gui.resource_well import IResourceWellController

class CompletedProgressionView(ViewImpl):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, _, backCallback):
        settings = ViewSettings(R.views.resource_well.lobby.feature.CompletedProgressionView(), flags=ViewFlags.LOBBY_SUB_VIEW, model=CompletedProgressionViewModel())
        self.__backCallback = backCallback
        self.__rewardID = first(self.__resourceWell.getReceivedRewardIDs())
        if self.__rewardID is not None:
            self.__vehicle = self.__resourceWell.getRewardVehicle(self.__rewardID)
        else:
            self.__rewardID, self.__vehicle = self.__searchRewardIDAndVehicle()
        super(CompletedProgressionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CompletedProgressionView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SerialNumberTooltip(parentLayout=self.layoutID) if contentID == R.views.resource_well.lobby.feature.tooltips.SerialNumberTooltip() else super(CompletedProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(CompletedProgressionView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showEventInfo),
         (self.viewModel.onClose, self.__close),
         (self.viewModel.onShowVehicle, self.__showVehicle),
         (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated),
         (self.__resourceWell.onSettingsChanged, self.__onEventStateUpdated))

    def _onShown(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            serialNumber = getSerialNumber(self.__rewardID, resourceWell=self.__resourceWell)
            model.setHasStyle(bool(serialNumber))
            model.setPersonalNumber(serialNumber)
            fillVehicleInfo(model.vehicleInfo, self.__vehicle)

    def __close(self):
        if callable(self.__backCallback):
            self.__backCallback()
        else:
            showHangar()
        self.destroyWindow()

    def __showEventInfo(self):
        showBrowserOverlayView(self.__resourceWell.config.infoPageUrl, VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW)

    def __showVehicle(self):
        if self.__vehicle.isInInventory:
            selectVehicleInHangar(self.__vehicle.intCD)
        else:
            showHangar()

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            showHangar()

    def __searchRewardIDAndVehicle(self):
        for rewardID, rewardConfig in self.__resourceWell.config.rewards.items():
            rewardVehicle = self.__resourceWell.getRewardVehicle(rewardID)
            hasStyle = hasRequiredStyle(rewardID, rewardConfig=rewardConfig, resourceWell=self.__resourceWell)
            if rewardVehicle and rewardVehicle.isInInventory and hasStyle:
                return (rewardID, rewardVehicle)

        return (None, None)
