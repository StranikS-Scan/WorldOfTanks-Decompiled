# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/event_dispatcher.py
from frameworks.wulf import WindowFlags, WindowLayer
from helpers import dependency
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.lock_overlays import lockNotificationManager
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.lootbox_system.base.common import Views, ViewID
from white_tiger.gui.impl.lobby.feature import WHITE_TIGER_LOCK_SOURCE_NAME
from white_tiger.gui.wt_event_helpers import getInfoPageURL
from white_tiger.gui.sounds.sound_constants import playInfoPageEnter, playInfoPageExit
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.game_control import ILootBoxSystemController

def showWhiteTigerBattleResultView(arenaUniqueID):
    from white_tiger.gui.impl.lobby.states import WhiteTigerPostBattleResultState
    lockNotificationManager(True, source=WHITE_TIGER_LOCK_SOURCE_NAME)
    WhiteTigerPostBattleResultState.goTo(arenaUniqueID=arenaUniqueID)


def showWelcomeScreen():
    from white_tiger.gui.impl.lobby.states import WhiteTigerWelcomeState
    WhiteTigerWelcomeState.goTo()


def showInfoPage():
    playInfoPageEnter()
    showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW), callbackOnClose=playInfoPageExit)


def showHangar():
    from white_tiger.gui.impl.lobby.states import WTHangarState
    WTHangarState.goTo()


def showProgressionScreen():
    from white_tiger.gui.impl.lobby.states import WhiteTigerProgressionState
    WhiteTigerProgressionState.goTo()


def showBuyLootboxOverlay():
    lootBoxes = dependency.instance(ILootBoxSystemController)
    Views.load(ViewID.SHOP, eventName=lootBoxes.mainEntryPoint)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showWtEventAwardWindow(rewardData, addRewards, hasCompletedProgression, notificationsMgr=None):
    from white_tiger.gui.impl.lobby.feature.white_tiger_reward_view import WhiteTigerRewardView
    layoutID = R.views.white_tiger.mono.lobby.reward_screen()
    ctx = {'rewardData': rewardData,
     'addRewards': addRewards,
     'hasCompletedProgression': hasCompletedProgression}
    view = WhiteTigerRewardView(layoutID, ctx)
    window = LobbyNotificationWindow(WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.FULLSCREEN_WINDOW)
    notificationsMgr.append(WindowNotificationCommand(window))
