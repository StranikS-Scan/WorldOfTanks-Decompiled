# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/shared/event_dispatcher.py
from __future__ import absolute_import
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from frameworks.wulf import WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController
FR_INFO_PAGE = 'frEventInfoPage'

@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def isCustomizationHangarDisabled(ctrl=None):
    return ctrl.isEventPrbActive()


def showFortRushBattleResultView(arenaUniqueID):
    from fort_rush.gui.impl.lobby.states import FortRushPostBattleResultState
    FortRushPostBattleResultState.goTo(arenaUniqueID=arenaUniqueID)


@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def showProgressionView(ctrl=None):
    from fort_rush.gui.impl.lobby.states import FortRushProgressionState
    if ctrl.isAvailable():
        FortRushProgressionState.goTo()


@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def showWelcomeScreen(ctrl=None):
    if ctrl.isAvailable():
        from fort_rush.gui.impl.lobby.fort_rush_welcome_screen import FortRushWelcomeScreenViewWindow
        window = FortRushWelcomeScreenViewWindow()
        window.load()


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showAwardWindow(rewardData, notificationsMgr=None):
    if notificationsMgr is None:
        return
    else:
        ctx = {'rewardData': rewardData}
        from fort_rush.gui.impl.lobby.fort_rush_reward_view import FortRushRewardView
        view = FortRushRewardView(ctx)
        window = LobbyNotificationWindow(WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.FULLSCREEN_WINDOW)
        notificationsMgr.append(WindowNotificationCommand(window))
        return


def showFortRushInfoPage():
    url = GUI_SETTINGS.lookup(FR_INFO_PAGE)
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
