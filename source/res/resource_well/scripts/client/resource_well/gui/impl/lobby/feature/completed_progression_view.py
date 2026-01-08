# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/completed_progression_view.py
from __future__ import absolute_import
from future.utils import viewitems
from typing import Optional, Tuple
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewImpl
from gui.shared import g_eventBus, events
from gui.shared.event_dispatcher import selectVehicleInHangar
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

    def __init__(self, layoutID=R.views.resource_well.mono.lobby.completed_progression_view()):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=CompletedProgressionViewModel())
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
        return SerialNumberTooltip(parentLayout=self.layoutID) if contentID == R.views.resource_well.mono.lobby.tooltips.serial_number_tooltip() else super(CompletedProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(CompletedProgressionView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.viewModel.onShowVehicle, self.__showVehicle), (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated), (self.__resourceWell.onSettingsChanged, self.__onEventStateUpdated))

    def _onShown(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            serialNumber = getSerialNumber(self.__rewardID, resourceWell=self.__resourceWell)
            model.setHasStyle(bool(serialNumber))
            model.setPersonalNumber(serialNumber)
            fillVehicleInfo(model.vehicleInfo, self.__vehicle)

    def __showVehicle(self):
        if self.__vehicle.isInInventory:
            selectVehicleInHangar(self.__vehicle.intCD)
        else:
            self.__goBack()

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.__goBack()

    def __goBack(self):
        lsm = getLobbyStateMachine()
        lsm.getStateFromView(self).goBack()

    def __searchRewardIDAndVehicle(self):
        for rewardID, rewardConfig in viewitems(self.__resourceWell.config.rewards):
            rewardVehicle = self.__resourceWell.getRewardVehicle(rewardID)
            hasStyle = hasRequiredStyle(rewardID, rewardConfig=rewardConfig, resourceWell=self.__resourceWell)
            if rewardVehicle and rewardVehicle.isInInventory and hasStyle:
                return (rewardID, rewardVehicle)

        return (None, None)


class CompletedProgressionWindow(WindowImpl):

    def __init__(self, layer, *args, **kwargs):
        super(CompletedProgressionWindow, self).__init__(content=CompletedProgressionView(), wndFlags=WindowFlags.WINDOW, layer=layer)
