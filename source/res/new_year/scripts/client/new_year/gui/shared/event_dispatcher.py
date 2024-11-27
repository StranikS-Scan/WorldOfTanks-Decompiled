# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/event_dispatcher.py
from collections import namedtuple
from wg_async import wg_async, wg_await
from new_year.gui.shared.events import NewYearEvent
from new_year.ny_constants import NewYearLootBoxes
from new_year.skeletons.new_year import INewYearController
from frameworks.wulf import WindowLayer, ViewStatus
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import findAndLoadWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
NYViewCtx = namedtuple('NYViewCtx', ('menuName', 'tabName', 'args', 'kwargs'))
NYTabCtx = namedtuple('NYTabCtx', ('tabName', 'menuName'))

def showNewYearMainView(menuName, tabName=None, *args, **kwargs):
    from new_year.gui.impl.lobby.new_year.main_view import MainView
    ctx = NYViewCtx(menuName=menuName, tabName=tabName, args=args, kwargs=kwargs)
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.new_year.lobby.new_year.MainView()
    mainView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if mainView is not None:
        event = NewYearEvent(NewYearEvent.ON_PRE_SWITCH_VIEW, ctx=ctx)
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MainView, ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showNewYearOnboardingView():
    from new_year.gui.impl.lobby.new_year.onboarding_view import OnboardingView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.new_year.lobby.new_year.OnboardingView(), OnboardingView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showNYLevelUpWindow(layer=WindowLayer.OVERLAY, useQueue=True, *args, **kwargs):
    from new_year.gui.impl.lobby.new_year.atmosphere_level_up.ny_level_up_view import NyLevelUpWindow
    window = findAndLoadWindow(useQueue, NyLevelUpWindow, layer=layer, *args, **kwargs)
    view = window.content
    if view is not None and view.viewStatus in (ViewStatus.CREATED, ViewStatus.LOADING, ViewStatus.LOADED):
        view.appendRewards(*args, **kwargs)
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showNYQuestsRewardWindow(data, notificationMgr=None):
    from new_year.gui.impl.lobby.new_year.quests.ny_quests_reward_view import NyQuestRewardWindow
    window = NyQuestRewardWindow(data)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, nyCtrl=INewYearController)
def showLootBoxEntry(lootBoxType=NewYearLootBoxes.NY_24_STANDARD, category='', lobbyCtx=None, nyCtrl=None, isReturnToHangar=True):
    enabled = lobbyCtx.getServerSettings().isLootBoxesEnabled() and nyCtrl.isEnabled()
    if not enabled:
        if nyCtrl.isSuspended():
            from new_year.gui.impl.lobby.loot_box.ny_loot_box_helper import showRestrictedSysMessage
            showRestrictedSysMessage()
        else:
            nyCtrl.showStateMessage()
        return
    from gui_lootboxes.gui.shared.event_dispatcher import showSpecificBoxInStorageView
    from gui_lootboxes.gui.storage_context.context import ReturnPlaces
    returnPlace = ReturnPlaces.TO_HANGAR if isReturnToHangar else ReturnPlaces.TO_SHARDS
    showSpecificBoxInStorageView(category=category, lootBoxType=lootBoxType, returnPlace=returnPlace)


def showVehicleDiscountOverlay():
    from gui.impl.pub.lobby_window import LobbyOverlay
    from new_year.gui.impl.lobby.new_year.vehicle_selection_view import VehicleSelectionView
    window = LobbyOverlay(content=VehicleSelectionView(R.views.new_year.lobby.new_year.VehicleSelectionView()))
    window.load()


def showConfirmUpdateCustomizationZoneOverlay(customizationZone, parent=None):
    from gui.impl.pub.lobby_window import LobbyOverlay
    from new_year.gui.impl.lobby.new_year.customization_zone.customization_level_up_view import CustomizationLevelUpView
    window = LobbyOverlay(content=CustomizationLevelUpView(customizationZone), parent=parent)
    window.load()


@wg_async
def showNYBuyToyDialog(toyID, callback):
    from gui.impl.dialogs import dialogs
    from new_year.gui.impl.lobby.new_year.views.buy_toy_view import BuyToyView
    result = yield wg_await(dialogs.showSingleDialogWithResultData(wrappedViewClass=BuyToyView, layoutID=BuyToyView.LAYOUT_ID, toyID=toyID))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))
