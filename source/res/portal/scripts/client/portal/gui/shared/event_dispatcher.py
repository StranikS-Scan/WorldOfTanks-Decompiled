# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/shared/event_dispatcher.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from portal.gui.portal_gui_constants import VIEW_ALIAS
from frameworks.wulf import WindowLayer
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent, WindowNotificationCommand
from skeletons.gui.impl import INotificationWindowController

@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showPortalBattleResultView(arenaUniqueID, notificationsMgr=None):
    notificationsMgr.postponeActive()
    notificationsMgr.append(EventNotificationCommand(NotificationEvent(method=_showPortalBattleResultView, arenaUniqueID=arenaUniqueID)))


def _showPortalBattleResultView(arenaUniqueID):
    from portal.gui.impl.lobby.battle_result.portal_battle_result_view import PortalBattleResultView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.portal.lobby.battle_result.PortalBattleResultView(), PortalBattleResultView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE), arenaUniqueID=arenaUniqueID), scope=EVENT_BUS_SCOPE.LOBBY)


def showPortalBattleQueueView():
    from portal.gui.impl.lobby.portal_battle_queue_view import PortalBattleQueueView
    uiLoader = dependency.instance(IGuiLoader)
    battleResultViewID = R.views.portal.lobby.battle_result.PortalBattleResultView()
    battleResultView = uiLoader.windowsManager.getViewByLayoutID(battleResultViewID)
    if battleResultView is not None:
        battleResultView.destroyWindow()
    layout = R.views.portal.lobby.PortalBattleQueueView()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layout, PortalBattleQueueView, ScopeTemplates.DEFAULT_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showPortalUpgradeView():
    from portal.gui.impl.lobby.portal_upgrade_view import PortalUpgradeView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.portal.lobby.PortalUpgradeView(), PortalUpgradeView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showComplexityUnlockedView(unlockedComplexity):
    from portal.gui.impl.lobby.complexity_unlock_view import ComplexityUnlockedWindow
    window = ComplexityUnlockedWindow(unlockedComplexity)
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showAwardsView(rewardsData, closeCallback=None, notificationMgr=None):
    from portal.gui.impl.lobby.portal_rewards_view import PortalRewardsViewWindow
    window = PortalRewardsViewWindow(rewardsData, closeCallback)
    notificationMgr.postponeActive()
    notificationMgr.append(WindowNotificationCommand(window))


def showPortalProgressionView():
    from portal.gui.impl.lobby.progression_view import ProgressionView
    layoutID = R.views.portal.lobby.ProgressionView()
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader.windowsManager.getViewByLayoutID(layoutID) is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, ProgressionView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showVideo(videoName):
    from portal.gui.impl.lobby.video_view import VideoViewWindow
    window = VideoViewWindow(videoName=videoName)
    window.load()


def showAboutImprovementsView():
    from portal.gui.impl.lobby.portal_upgrade_info_view import PortalUpgradeInfoViewWindow
    window = PortalUpgradeInfoViewWindow()
    window.load()


def showPortalUpgradeResetView():
    from portal.gui.impl.lobby.portal_upgrade_reset_view import PortalUpgradeResetViewWindow
    window = PortalUpgradeResetViewWindow()
    window.load()


def showPortalInfoPage():
    from portal.gui.portal_event_helpers import getInfoPageURL
    showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
