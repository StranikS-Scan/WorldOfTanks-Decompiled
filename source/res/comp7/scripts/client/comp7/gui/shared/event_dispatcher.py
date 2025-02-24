# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/shared/event_dispatcher.py
import logging
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from frameworks.wulf import Window
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.server_events.events_dispatcher import ifPrbNavigationEnabled
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar, getParentWindow
from gui.shared.events import LobbyHeaderMenuEvent
from helpers import dependency
from skeletons.gui.game_control import ICollectionsSystemController, IComp7Controller
from skeletons.gui.game_control import IHangarSpaceSwitchController
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
if typing.TYPE_CHECKING:
    from enum import Enum
_logger = logging.getLogger(__name__)

def showComp7PrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showComp7MetaRootView(tabId=None, *args, **kwargs):
    from comp7.gui.impl.lobby.meta_view.meta_root_view import MetaRootView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.comp7.lobby.MetaRootView()
    metaView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if metaView is None:
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.DESELECT_HEADER_BUTTONS), scope=EVENT_BUS_SCOPE.LOBBY)
        event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MetaRootView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId, *args, **kwargs)
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
    elif tabId is not None:
        metaView.switchPage(tabId)
    return


def showComp7NoVehiclesScreen():
    from comp7.gui.impl.lobby.no_vehicles_screen import NoVehiclesScreen
    event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.comp7.lobby.NoVehiclesScreen(), NoVehiclesScreen, ScopeTemplates.LOBBY_SUB_SCOPE))
    g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)


def showComp7IntroScreen():
    from comp7.gui.impl.lobby.intro_screen import IntroScreen
    event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.comp7.lobby.IntroScreen(), IntroScreen, ScopeTemplates.LOBBY_SUB_SCOPE))
    g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7WhatsNewScreen(notificationMgr=None):
    from comp7.gui.impl.lobby.whats_new_view import WhatsNewViewWindow
    notificationMgr.append(WindowNotificationCommand(WhatsNewViewWindow()))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7RanksRewardsScreen(quest, periodicQuests, notificationMgr=None):
    from comp7.gui.impl.lobby.rewards_screen import RanksRewardsWindow
    window = RanksRewardsWindow(quest=quest, periodicQuests=periodicQuests)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7TokensRewardsScreen(quest, notificationMgr=None):
    from comp7.gui.impl.lobby.rewards_screen import TokensRewardsWindow
    window = TokensRewardsWindow(quest=quest)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7QualificationRewardsScreen(quests, notificationMgr=None):
    from comp7.gui.impl.lobby.rewards_screen import QualificationRewardsWindow
    window = QualificationRewardsWindow(quests=quests)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7YearlyRewardsScreen(bonuses, showSeasonResults=True, notificationMgr=None):
    from comp7.gui.impl.lobby.rewards_screen import YearlyRewardsWindow
    window = YearlyRewardsWindow(bonuses=bonuses, showSeasonResults=showSeasonResults)
    notificationMgr.append(WindowNotificationCommand(window))


def showComp7YearlyRewardsSelectionWindow():
    from comp7.gui.impl.lobby.rewards_selection_screen import Comp7RewardsSelectionWindow, Comp7SelectableRewardType
    window = Comp7RewardsSelectionWindow(Comp7SelectableRewardType.YEARLY)
    window.load()


def showComp7WeeklyQuestsRewardsSelectionWindow():
    from comp7.gui.impl.lobby.rewards_selection_screen import Comp7RewardsSelectionWindow, Comp7SelectableRewardType
    window = Comp7RewardsSelectionWindow(Comp7SelectableRewardType.WEEKLY_QUESTS)
    window.load()


def showComp7AllRewardsSelectionWindow():
    from comp7.gui.impl.lobby.rewards_selection_screen import Comp7RewardsSelectionWindow
    window = Comp7RewardsSelectionWindow()
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7SelectedRewardsScreen(bonuses, notificationMgr=None):
    from comp7.gui.impl.lobby.rewards_screen import SelectedRewardsWindow
    window = SelectedRewardsWindow(bonuses=bonuses)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController, comp7Ctrl=IComp7Controller)
def showComp7SeasonStatisticsScreen(seasonNumber=None, force=False, notificationMgr=None, comp7Ctrl=None):
    from comp7.gui.impl.lobby.season_statistics import SeasonStatisticsWindow
    if not seasonNumber:
        seasonInfo = comp7Ctrl.getPreviousSeason()
        if not seasonInfo:
            _logger.error('Could not show Season Statistic view, no season info.')
            return
        seasonNumber = comp7Ctrl.getPreviousSeason().getNumber()
    window = SeasonStatisticsWindow(seasonNumber=seasonNumber, saveViewing=not force)
    if force:
        window.load()
    else:
        notificationMgr.append(WindowNotificationCommand(window))


def showComp7PurchaseDialog(productCode, parent=None):
    from comp7.gui.impl.lobby.dialogs.purchase_dialog import PurchaseDialogWindow
    if not PurchaseDialogWindow.getInstances():
        PurchaseDialogWindow(productCode, parent).load()


@dependency.replace_none_kwargs(guiLoader=IGuiLoader, collections=ICollectionsSystemController)
def showCollectionWindow(collectionId, page=None, backCallback=None, backBtnText='', parent=None, guiLoader=None, collections=None):
    if not collections.isEnabled():
        showHangar()
        return
    else:
        from gui.impl.lobby.collection.collection import CollectionWindow
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.collection.CollectionView())
        if view is None:
            window = CollectionWindow(collectionId, page, backCallback, backBtnText, parent or getParentWindow())
            window.load()
        return


@dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller, spaceSwitchController=IHangarSpaceSwitchController)
def showComp7ShopPage(selectComp7Hangar=None, comp7Ctrl=None, spaceSwitchController=None):
    if not comp7Ctrl.isComp7PrbActive():
        spaceSwitchController.onSpaceUpdated += checkSpaceAndShowShop
        selectComp7Hangar()
        return
    showComp7MetaRootView(tabId=MetaRootViews.SHOP)


@dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller, spaceSwitchController=IHangarSpaceSwitchController)
def checkSpaceAndShowShop(comp7Ctrl, spaceSwitchController):
    if not comp7Ctrl.isComp7PrbActive():
        return
    spaceSwitchController.onSpaceUpdated -= checkSpaceAndShowShop
    showComp7MetaRootView(tabId=MetaRootViews.SHOP)


@ifPrbNavigationEnabled
@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7BanWindow(arenaTypeID, time, duration, penalty, isQualification, notificationMgr=None, force=False):
    from comp7.gui.impl.lobby.hangar.notifications.punishment_notification_view import Comp7BanNotificationWindow
    wnd = Comp7BanNotificationWindow(arenaTypeID, time, duration, penalty, isQualification)
    if force:
        wnd.load()
    else:
        notificationMgr.append(WindowNotificationCommand(wnd))
