# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/shared/event_dispatcher.py
from helpers import dependency
from gui.impl.gen import R
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from skeletons.gui.impl import IGuiLoader
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams

def showReplays(location=None):
    from server_side_replay.gui.impl.lobby.replays_root_view import ReplaysRootView
    uiLoader = dependency.instance(IGuiLoader)
    layoutID = R.views.server_side_replay.lobby.MetaReplaysView()
    if uiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=layoutID, viewClass=ReplaysRootView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'location': location}), scope=EVENT_BUS_SCOPE.LOBBY)
    return
