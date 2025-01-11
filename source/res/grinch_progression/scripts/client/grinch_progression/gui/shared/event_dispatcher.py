# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/shared/event_dispatcher.py
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.impl.common.fade_manager import UseFading
from gui.impl.gen import R
from gui.shared import events, g_eventBus
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.framework import ScopeTemplates
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.system_messages import ISystemMessages
from helpers import dependency

@UseFading(layer=WindowLayer.OVERLAY, waitForLayoutReady=R.views.grinch_progression.lobby.GameBoard())
def showGameBoardView():
    from grinch_progression.gui.impl.lobby.views.game_board import GameBoardView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.grinch_progression.lobby.GameBoard()
    gbView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if not gbView:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, GameBoardView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@UseFading(layer=WindowLayer.OVERLAY, waitForLayoutReady=R.views.grinch_progression.lobby.InfoView())
def showGameBoardProgressionInfoView():
    from grinch_progression.gui.impl.lobby.views.info_view import InfoView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.grinch_progression.lobby.InfoView()
    infoView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if not infoView:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, InfoView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showIntoVideoWindow():
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.grinch_progression.lobby.IntroVideo()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        from grinch_progression.gui.impl.lobby.views.intro_video import IntroVideoWindow
        window = IntroVideoWindow()
        window.load()
    return


def showAboutGameBoard():
    url = GUI_SETTINGS.grinchProgressionInfo.get('aboutEventURL')
    if url:
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url))


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def showGPStyleRewardNotification(data, systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientMessage({'data': data,
     'template': 'GpStyleReward'}, msgType=SCH_CLIENT_MSG_TYPE.NY_GF_SM_TYPE)
