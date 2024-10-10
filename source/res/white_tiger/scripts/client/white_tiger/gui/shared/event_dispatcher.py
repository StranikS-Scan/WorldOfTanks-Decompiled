# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/event_dispatcher.py
import typing
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_vehicle_portal_model import EventTankType
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from helpers import dependency
from gui.impl.gen import R
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events, g_eventBus
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.pub.notification_commands import WindowNotificationCommand
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from gui.Scaleform.genConsts.EVENT_BATTLES_ALIASES import EVENT_BATTLES_ALIASES
from gui.impl.lobby.video.video_view import VideoViewWindow
from white_tiger.gui.impl.lobby.wt_event_sound import WhiteTigerVehicleAwardViewSoundControl
if typing.TYPE_CHECKING:
    from typing import Callable
    from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager
    from gui.shared.gui_items.Vehicle import Vehicle

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
    from gui.impl.lobby.postbattle.postbattle_screen_view import PostbattleScreenView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, PostbattleScreenView, ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'arenaUniqueID': arenaUniqueID}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showEventBattlesPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEventPortalAwardsWindow(lootBoxType, awards, count=1, openedCount=1, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_portal_awards import WtEventPortalAwardsWindow
    lobbyContext = dependency.instance(ILobbyContext)
    isLootBoxesEnabled = lobbyContext.getServerSettings().isLootBoxesEnabled()
    if not isLootBoxesEnabled:
        return
    else:
        uiLoader = dependency.instance(IGuiLoader)
        lootBoxOpenView = uiLoader.windowsManager.getViewByLayoutID(R.views.white_tiger.lobby.PortalAwardsView())
        if lootBoxOpenView is None:
            window = WtEventPortalAwardsWindow(lootBoxType, awards, count, openedCount, parent=parent)
            window.load()
        return


def closeEventPortalAwardsWindow():
    uiLoader = dependency.instance(IGuiLoader)
    lootBoxOpenView = uiLoader.windowsManager.getViewByLayoutID(R.views.white_tiger.lobby.PortalAwardsView())
    if lootBoxOpenView is not None:
        lootBoxOpenView.destroy()
    return


def showEventStorageWindow(parent=None):
    from white_tiger.gui.impl.lobby.wt_event_storage import WtEventStorageWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.white_tiger.lobby.PortalView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = WtEventStorageWindow(parent=parent)
        window.load()
    return


def showEventPortalWindow(portalType, defaultRunPortalTimes=1, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_portal import WtEventPortalWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.white_tiger.lobby.InsidePortalView()
    portalView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if portalView is not None and portalView.portalType == portalType:
        return
    else:
        window = WtEventPortalWindow(portalType, defaultRunPortalTimes, parent)
        window.load()
        return


def showVehicleAwardWindow(boxType=WhiteTigerLootBoxes.WT_BOSS, awards=None, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_vehicle_portal import WtEventVehiclePortalWindow
    window = WtEventVehiclePortalWindow(boxType, awards, parent)
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


def isWTMetaViewExist():
    uiLoader = dependency.instance(IGuiLoader)
    progressionLayoutID = R.views.lobby.white_tiger.ProgressionView()
    welcomeLayoutID = R.views.lobby.white_tiger.lobby.WelcomeView()
    return False if not uiLoader or not uiLoader.windowsManager else not (uiLoader.windowsManager.getViewByLayoutID(progressionLayoutID) is None and uiLoader.windowsManager.getViewByLayoutID(welcomeLayoutID) is None)


def showWTWelcomeScreen():
    from white_tiger.gui.impl.lobby.wt_event_welcome import WTEventWelcomeView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.white_tiger.lobby.WelcomeView(), WTEventWelcomeView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showWtEventAwardWindow(questId, parent=None, notificationMgr=None):
    from white_tiger.gui.impl.lobby.wt_event_award_view import WTEventAwardWindow
    window = WTEventAwardWindow(questId, parent=parent)
    notificationMgr.append(WindowNotificationCommand(window))


def showWtEventSpecialAwardWindow(questId, parent=None):
    from white_tiger.gui.impl.lobby.wt_event_award_view import WTEventSpecialAwardWindow
    window = WTEventSpecialAwardWindow(questId, parent=parent)
    window.load()


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    if not uiLoader or not uiLoader.windowsManager:
        return False
    else:
        view = uiLoader.windowsManager.getViewByLayoutID(layoutID)
        return view is not None


def showVideo(videoName, soundController, onVideoClose=None, canManageWorldDraw=True):
    videoSource = R.videos.wt_event.dyn(videoName)
    if not videoSource or not videoSource.exists():
        if onVideoClose:
            onVideoClose()
        return

    def onVideoCloseWrapper(*args, **kwargs):
        if onVideoClose:
            onVideoClose(*args, **kwargs)

    window = VideoViewWindow(videoSource(), onVideoClosed=onVideoCloseWrapper, isAutoClose=True, soundControl=soundController, canManageWorldDraw=canManageWorldDraw)
    window.load()


def showSpecialVehicleReceivedVideo(specialVehicle, onVideoClose=None, canManageWorldDraw=True):
    tankTypeToVideo = {EventTankType.PRIMARY: 'primary_tank_portal_show',
     EventTankType.SECONDARY: 'secondary_tank_portal_show'}
    specialVehicleName = specialVehicle.name.split(':')[1]
    tankType = EventTankType.PRIMARY if specialVehicleName == EventTankType.PRIMARY else EventTankType.SECONDARY
    videoName = tankTypeToVideo[tankType]

    def onVideoCloseWrapper(*args, **kwargs):
        if onVideoClose:
            onVideoClose(*args, **kwargs)

    showVideo(videoName, soundController=WhiteTigerVehicleAwardViewSoundControl(), onVideoClose=onVideoCloseWrapper, canManageWorldDraw=canManageWorldDraw)
