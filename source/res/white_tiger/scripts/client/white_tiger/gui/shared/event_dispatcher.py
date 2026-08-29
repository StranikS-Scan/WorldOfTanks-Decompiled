# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/event_dispatcher.py
import typing
from helpers import dependency
from gui.impl.gen import R
from th_async import th_async, th_await
from gui.impl.dialogs import dialogs
from frameworks.wulf import WindowLayer
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events, g_eventBus
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from gui.impl.pub.notification_commands import WindowNotificationCommand
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from gui.wt_event.wt_event_helpers import getReceivedVehiclesData
from skeletons.gui.game_control import ILootBoxesController
from white_tiger.gui.impl.lobby.wt_video_view import WtVideoViewWindow
from white_tiger.gui.shared import rewardVideoSequencePlayer
from events_core_client.gui.impl.video_with_controls.video_view import VideoPrerequisites
from skeletons.gui.game_control import IWhiteTigerController
if typing.TYPE_CHECKING:
    from typing import Callable

def closePostbattleWindow():

    def filterFunc(window):
        if window.content is None:
            return False
        else:
            return True if window.content.layoutID == R.views.lobby.postbattle.PostbattleScreen() else None

    uiLoader = dependency.instance(IGuiLoader)
    for window in uiLoader.windowsManager.findWindows(filterFunc):
        window.destroy()


def showBattleResultsWindow(arenaUniqueID):
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.white_tiger.lobby.postbattle.PostbattleScreen()
    postbattleView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if postbattleView is not None:
        if arenaUniqueID == postbattleView.arenaUniqueID:
            return
        postbattleView.destroyWindow()
    from white_tiger.gui.impl.lobby.battle_result.wt_battle_result_view import WtBattleResultView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, WtBattleResultView, ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'arenaUniqueID': arenaUniqueID}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showEventPortalAwardsWindow(lootBoxType, awards, boxCount=1, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_portal_awards import WtEventPortalAwardsWindow
    awardView = getEventPortalAwardsWindow()
    if awardView is None:
        window = WtEventPortalAwardsWindow(lootBoxType, awards, boxCount, parent=parent)
        window.load()
    return


def getEventPortalAwardsWindow():
    lootBoxesCtrl = dependency.instance(ILootBoxesController)
    if not lootBoxesCtrl.isEnabled():
        return None
    else:
        uiLoader = dependency.instance(IGuiLoader)
        return uiLoader.windowsManager.getViewByLayoutID(R.views.white_tiger.lobby.WtPortalRewardsView())


def showAwardWindow(boxType, awards=None, boxCount=1, parent=None, callback=None):
    receivedVehicles = getReceivedVehiclesData(awards, boxType)
    if receivedVehicles:
        rewardVideoSequencePlayer.playSequence(parent=parent, boxType=boxType, boxCount=boxCount, mainRewards=receivedVehicles, allRewards=awards)
        awardView = getEventPortalAwardsWindow()
        if awardView:
            awardView.destroy()
    elif callback:
        callback({'awards': awards})
    else:
        showEventPortalAwardsWindow(boxType, awards, boxCount=boxCount, parent=parent)


def showEventStorageWindow(parent=None):
    from white_tiger.gui.impl.lobby.wt_event_storage import WtEventStorageWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.white_tiger.lobby.WtStorageView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = WtEventStorageWindow(parent=parent)
        window.load()
    return


def showEventPortalWindow(portalType, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_portal import WtEventPortalWindow
    from white_tiger.gui.impl.lobby.wt_tank_portal import WtTankPortalWindow
    from white_tiger.gui.impl.gen.view_models.views.common.wt_common_consts import PortalType
    if portalType == PortalType.TANK:
        window = WtTankPortalWindow(parent)
    else:
        window = WtEventPortalWindow(portalType, parent)
    window.load()


def showEventProgressionWindow(fromWelcome=False):
    from white_tiger.gui.impl.lobby.wt_event_progression_view import WTEventProgressionView
    layoutID = R.views.white_tiger.lobby.ProgressionView()
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader.windowsManager.getViewByLayoutID(layoutID) is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, WTEventProgressionView, ScopeTemplates.LOBBY_SUB_SCOPE), fromWelcome=fromWelcome), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showWTWelcomeScreen():
    from white_tiger.gui.impl.lobby.wt_event_welcome import WTEventWelcomeView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.white_tiger.lobby.WelcomeView(), WTEventWelcomeView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showWtEventAwardWindow(questId, parent=None, notificationMgr=None):
    from white_tiger.gui.impl.lobby.wt_event_award_view import WTEventAwardWindow
    window = WTEventAwardWindow(questId, parent=parent)
    notificationMgr.append(WindowNotificationCommand(window))


def showWtEventSpecialAwardWindow(questId, questData=None, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_award_view import WTEventSpecialAwardWindow
    window = WTEventSpecialAwardWindow(questId, questData=questData, parent=parent)
    window.load()


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    if not uiLoader or not uiLoader.windowsManager:
        return False
    else:
        view = uiLoader.windowsManager.getViewByLayoutID(layoutID)
        return view is not None


def showVideo(videoName, onVideoClose=None):
    videoSource = R.videos.wt_event.dyn(videoName)
    if not videoSource or not videoSource.exists():
        if onVideoClose:
            onVideoClose()
        return
    else:
        subtitlesSource = R.subtitles.white_tiger.dyn(videoName)
        window = WtVideoViewWindow(VideoPrerequisites(videoSource(), subtitlesSource(), True, True, None), onVideoClose if onVideoClose else None)
        window.load()
        return


@th_async
def showWTFairplayDialog(penaltyType, data=None, callback=None):
    from white_tiger.gui.impl.lobby.wt_fairplay_windows import WTFairPlayWindow, WTFairPlayWarningWindow
    wtController = dependency.instance(IWhiteTigerController)
    if not wtController.isEventPrbActive():
        return
    else:
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.white_tiger.lobby.WtPortalView()
        restrictView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if restrictView is not None:
            return
        contentResId = R.views.white_tiger.lobby.WtTankPortalView()
        restrictView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if restrictView is not None:
            return
        windowClass = WTFairPlayWindow if penaltyType == 'penalty' else WTFairPlayWarningWindow
        result = yield th_await(dialogs.showSingleDialogWithResultData(data=data or {}, layoutID=windowClass.LAYOUT_ID, wrappedViewClass=windowClass, layer=WindowLayer.WINDOW))
        if result.busy:
            if callback is not None:
                callback(False)
        else:
            isOK, _ = result.result
            if callback is not None:
                callback(isOK)
        return
