# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/shared/event_dispatcher.py
from __future__ import absolute_import
import logging
from typing import List, Tuple, Optional, TYPE_CHECKING
from BWUtil import AsyncReturn
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import getRewardVehiclesInInventory
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.resource_well import IResourceWellController
from wg_async import wg_await, wg_async
if TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def openInfoPageScreen(resourceWell=None):
    showBrowserOverlayView(resourceWell.config.infoPageUrl, VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def showMainWindow(resourceWell=None):
    mode = resourceWell.getPurchaseMode()
    isCompleted = resourceWell.isActive() and resourceWell.isSeasonNumberDefault() and getRewardVehiclesInInventory() or resourceWell.getReceivedRewardIDs()
    if mode in (PurchaseMode.ONE_SERIAL_PRODUCT, PurchaseMode.SEQUENTIAL_PRODUCT) and isCompleted:
        from resource_well.gui.impl.lobby.feature.states import ProgressionCompletedState
        ProgressionCompletedState.goTo()
    else:
        from resource_well.gui.impl.lobby.feature.states import ProgressionState
        ProgressionState.goTo()


def showResourcesLoadingWindow(rewardID, stopRequesterInDestroy=True):
    from resource_well.gui.impl.lobby.feature.resources_loading_view import ResourcesLoadingWindow
    ResourcesLoadingWindow(rewardID, stopRequesterInDestroy=stopRequesterInDestroy).load()


@wg_async
def showResourcesLoadingConfirm(rewardID, resources, isReturnOperation):
    from gui.impl.dialogs import dialogs
    from resource_well.gui.impl.lobby.feature.resources_loading_confirm import ResourcesLoadingConfirm
    result = yield wg_await(dialogs.showCustomBlurSingleDialog(wrappedViewClass=ResourcesLoadingConfirm, layoutID=R.views.resource_well.mono.lobby.resources_loading_confirm(), rewardID=rewardID, resources=resources, isReturnOperation=isReturnOperation))
    if result.busy:
        raise AsyncReturn((False, {}))
    isOK, data = result.result
    raise AsyncReturn((isOK, data))


@wg_async
def showNextSerialVehiclesConfirm(rewardID):
    from gui.impl.dialogs import dialogs
    from resource_well.gui.impl.lobby.feature.no_serial_vehicles_confirm import NoSerialVehiclesConfirm
    result = yield wg_await(dialogs.showCustomBlurSingleDialog(wrappedViewClass=NoSerialVehiclesConfirm, layoutID=R.views.resource_well.mono.lobby.no_serial_vehicles_confirm(), rewardID=rewardID))
    if result.busy:
        raise AsyncReturn((False, {}))
    isOK, data = result.result
    raise AsyncReturn((isOK, data))


def showResourceWellNoVehiclesConfirm(parent=None):
    from resource_well.gui.impl.lobby.feature.no_vehicles_confirm import NoVehiclesConfirmWindow
    NoVehiclesConfirmWindow(parent=parent).load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showResourceWellAwardWindow(rewardID, serialNumber='', notificationMgr=None):
    from resource_well.gui.impl.lobby.feature.award_view import AwardWindow
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(R.views.resource_well.mono.lobby.award_view()) is None:
        window = AwardWindow(rewardID, serialNumber)
        notificationMgr.append(WindowNotificationCommand(window))
    return


def showResourceWellVehiclePreview(vehicleCD, rewardID, style=None, previewStyle=None, topPanelData=None):
    from resource_well.gui.impl.lobby.feature.states import VehiclePreviewState
    VehiclePreviewState.goTo(itemCD=vehicleCD, rewardID=rewardID, numberStyle=style, style=previewStyle, topPanelData=topPanelData)
