# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_helpers.py
import typing
from async import async, await_callback
from gifts.gifts_common import GiftEventID
from gui.Scaleform.Waiting import Waiting
from gui.shared.events import HasCtxEvent
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import SHOW_TAB_EVENT, SEND_TO_PLAYER_EVENT, MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER, MAIN_VIEW_INIT_CONTEXT_TAB, MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, SEND_TO_PLAYER_EVENT_IS_ENABLED, EnvelopeTypes
from skeletons.gui.impl import INotificationWindowController, IGuiLoader
from gui.shared import events, g_eventBus
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.impl.lobby.lunar_ny.lunar_ny_select_charm_view import LunarNYSelectCharmWindow
from gui.impl.lobby.video.video_view import VideoViewWindow, LunarNYVideoViewWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.Scaleform.framework import ScopeTemplates
from gui.shared.event_bus import EVENT_BUS_SCOPE
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from frameworks.wulf import View

@dependency.replace_none_kwargs(lunarNYController=ILunarNYController, gui=IGuiLoader)
def showLunarNYMainView(initCtx=None, lunarNYController=None, gui=None):
    from gui.impl.lobby.lunar_ny.lunar_new_year import LunarNYMainView
    from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
    if lunarNYController.isActive():
        mainView = gui.windowsManager.getViewByLayoutID(R.views.lobby.lunar_ny.LunarNewYear())
        if mainView is None:
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.lunar_ny.LunarNewYear(), LunarNYMainView, ScopeTemplates.LOBBY_SUB_SCOPE), initCtx=initCtx), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            initTab = initCtx.get(MAIN_VIEW_INIT_CONTEXT_TAB, Tab.SENDENVELOPES)
            g_eventBus.handleEvent(HasCtxEvent(SHOW_TAB_EVENT, initTab))
            if initCtx.get(MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER):
                g_eventBus.handleEvent(HasCtxEvent(SEND_TO_PLAYER_EVENT, initCtx))
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController, gui=IGuiLoader)
def introViewInQueue(notificationMgr=None, gui=None):
    view = gui.windowsManager.getViewByLayoutID(R.views.lobby.lunar_ny.IntroView())
    parentWindow = view.getParentWindow() if view is not None else None
    return notificationMgr.hasWindow(parentWindow)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showLunarNYIntroWindow(notificationMgr=None):
    from gui.impl.lobby.lunar_ny.intro_view import IntroViewWindow
    window = IntroViewWindow()
    if not introViewInQueue():
        notificationMgr.append(WindowNotificationCommand(window))


def showVideoView(videoResID, onVideoStarted=None, onVideoStopped=None, onVideoClosed=None, isAutoClose=False, soundControl=None):
    window = VideoViewWindow(videoResID=videoResID, onVideoStarted=onVideoStarted, onVideoStopped=onVideoStopped, onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=soundControl)
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showVideoViewWithNotificationManager(notificationMgr=None, videoResID=None, onVideoStarted=None, onVideoStopped=None, onVideoClosed=None, isAutoClose=False, soundControl=None):
    window = LunarNYVideoViewWindow(videoResID=videoResID, onVideoStarted=onVideoStarted, onVideoStopped=onVideoStopped, onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=soundControl)
    notificationMgr.append(WindowNotificationCommand(window))


def showSelectCharmView(slotIdx, parent=None):
    guiLoader = dependency.instance(IGuiLoader)
    window = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.lunar_ny.SelectCharmView())
    if window is None:
        LunarNYSelectCharmWindow(slotIdx, parent=parent).load()
    return


@async
@dependency.replace_none_kwargs(lunarNYController=ILunarNYController)
def showEnvelopesHistoryView(parent=None, lunarNYController=None):
    from gui.impl.lobby.lunar_ny.envelopes_history_view import EnvelopesHistoryViewWindow
    from lunar_ny.gift_system.lunar_ny_gift_history_requester import CountGiftHistoryRequester, GiftHistoryRequester
    from gui.impl.gen.view_models.views.lobby.lunar_ny.envelopes_history_view_model import ColumnType, ColumnSortingOrder
    guiLoader = dependency.instance(IGuiLoader)
    window = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.lunar_ny.envelopes.EnvelopesHistoryView())
    if window is None:
        Waiting.show('loadContent')
        countRequester = CountGiftHistoryRequester()
        dataRequester = GiftHistoryRequester()
        countGiftHistoryResult = yield await_callback(countRequester.request)(eventID=GiftEventID.LUNAR_NY)
        if countGiftHistoryResult.success:
            lootboxID = lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(EnvelopeTypes.PREMIUM_PAID)
            yield await_callback(dataRequester.request)(lootboxID=lootboxID, pageNum=0, column=ColumnType.RECEIVEDENVELOPES, order=ColumnSortingOrder.DESC)
        Waiting.hide('loadContent')
        EnvelopesHistoryViewWindow(parent=parent, countRequester=countRequester, dataRequester=dataRequester).load()
    return


def showEnvelopesSendView(envelopeType=None, receiverID=-1):
    from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
    initCtx = {SEND_TO_PLAYER_EVENT_IS_ENABLED: True,
     MAIN_VIEW_INIT_CONTEXT_TAB: Tab.SENDENVELOPES,
     MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE: envelopeType,
     MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER: receiverID}
    showLunarNYMainView(initCtx)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showOpenEnvelopesAwardView(rawData, envelopesType, notificationMgr=None):
    from gui.impl.lobby.lunar_ny.open_envelopes_award_view import OpenEnvelopesAwardViewWindow
    window = OpenEnvelopesAwardViewWindow(rawData, envelopesType)
    notificationMgr.append(WindowNotificationCommand(window))


def createRewardTooltip(contentID, tooltipData):
    from gui.impl.backport.backport_tooltip import createBackportTooltipContent
    from gui.impl.lobby.lunar_ny.tooltips.charm_tooltip import CharmTooltip
    from gui.impl.lobby.lunar_ny.tooltips.envelope_tooltip import EnvelopeTooltip
    if tooltipData is None:
        return
    elif contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
        return createBackportTooltipContent(tooltipData=tooltipData)
    elif contentID == R.views.lobby.lunar_ny.CharmTooltip():
        return CharmTooltip(charmID=tooltipData.specialArgs[0])
    else:
        return EnvelopeTooltip(envelopeType=tooltipData.specialArgs[0]) if contentID == R.views.lobby.lunar_ny.tooltips.EnvelopeTooltip() else None


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showLunarNYProgressionAwardView(rawData, receivedLevel, notificationMgr=None):
    from gui.impl.lobby.lunar_ny.lunar_ny_progression_award_view import LunarNYProgressionAwardWindow
    window = LunarNYProgressionAwardWindow(rawData, receivedLevel)
    notificationMgr.append(WindowNotificationCommand(window))
