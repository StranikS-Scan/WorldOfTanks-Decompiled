# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/shared/event_dispatcher.py
import logging
from typing import Callable, List, Tuple, Optional, TYPE_CHECKING, Type
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.impl.common.fade_manager import UseFading
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import getRewardVehiclesInInventory
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.resource_well import IResourceWellController
from wg_async import wg_await, wg_async
if TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)

def _loadProgressionView(viewRes, view, backCallback):
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(viewRes) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, view, ScopeTemplates.DEFAULT_SCOPE), backCallback=backCallback), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@UseFading(layer=WindowLayer.SUB_VIEW, waitForLayoutReady=R.views.resource_well.lobby.feature.CompletedProgressionView())
def _loadCompletedProgressionView(backCallback):
    from resource_well.gui.impl.lobby.feature.completed_progression_view import CompletedProgressionView
    view = CompletedProgressionView
    viewRes = R.views.resource_well.lobby.feature.CompletedProgressionView()
    _loadProgressionView(viewRes, view, backCallback)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def showResourceWellProgressionWindow(resourceWell=None, backCallback=showHangar):
    mode = resourceWell.getPurchaseMode()
    isCompleted = resourceWell.isActive() and resourceWell.isSeasonNumberDefault() and getRewardVehiclesInInventory() or resourceWell.getReceivedRewardIDs()
    if mode in (PurchaseMode.ONE_SERIAL_PRODUCT, PurchaseMode.SEQUENTIAL_PRODUCT) and isCompleted:
        _loadCompletedProgressionView(backCallback)
    else:
        from resource_well.gui.impl.lobby.feature.progression_view import ProgressionView
        _loadProgressionView(R.views.resource_well.lobby.feature.ProgressionView(), ProgressionView, backCallback)


def showResourcesLoadingWindow(rewardID):
    from resource_well.gui.impl.lobby.feature.resources_loading_view import ResourcesLoadingWindow
    ResourcesLoadingWindow(rewardID).load()


@wg_async
def showResourcesLoadingConfirm(rewardID, resources, isReturnOperation, callback):
    from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
    from resource_well.gui.impl.lobby.feature.resources_loading_confirm import ResourcesLoadingConfirm
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.resource_well.lobby.feature.ResourcesLoadingConfirm(), wrappedViewClass=ResourcesLoadingConfirm, rewardID=rewardID, resources=resources, isReturnOperation=isReturnOperation))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


@wg_async
def showNextSerialVehiclesConfirm(rewardID, callback):
    from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
    from resource_well.gui.impl.lobby.feature.no_serial_vehicles_confirm import NoSerialVehiclesConfirm
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.resource_well.lobby.feature.NoSerialVehiclesConfirm(), wrappedViewClass=NoSerialVehiclesConfirm, rewardID=rewardID))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


def showResourceWellNoVehiclesConfirm(parent=None):
    from resource_well.gui.impl.lobby.feature.no_vehicles_confirm import NoVehiclesConfirmWindow
    NoVehiclesConfirmWindow(parent=parent).load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showResourceWellAwardWindow(rewardID, serialNumber='', notificationMgr=None):
    from resource_well.gui.impl.lobby.feature.award_view import AwardWindow
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(R.views.resource_well.lobby.feature.AwardView()) is None:
        window = AwardWindow(rewardID, serialNumber)
        notificationMgr.append(WindowNotificationCommand(window))
    return


def showResourceWellVehiclePreview(vehicleCD, rewardID, style=None, previewStyle=None, backCallback=None, topPanelData=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW), ctx={'itemCD': vehicleCD,
     'rewardID': rewardID,
     'previewBackCb': backCallback,
     'numberStyle': style,
     'style': previewStyle,
     'topPanelData': topPanelData,
     'previewAlias': VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW}), EVENT_BUS_SCOPE.LOBBY)
