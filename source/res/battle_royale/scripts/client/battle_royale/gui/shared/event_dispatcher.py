# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/event_dispatcher.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from battle_royale.gui.impl.lobby.views.battle_result_view import BATTLE_ROYALE_LOCK_SOURCE_NAME
from gui.impl.pub.notification_commands import NonPersistentEventNotificationCommand, NotificationEvent
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INotificationWindowController

@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showBattleRoyaleResultsView(ctx, notificationsMgr=None):
    notificationsMgr.append(NonPersistentEventNotificationCommand(NotificationEvent(method=showBattleRoyaleResultsInfo, ctx=ctx)))


def showBattleRoyaleResultsInfo(ctx):
    lockNotificationManager(True, source=BATTLE_ROYALE_LOCK_SOURCE_NAME)
    from battle_royale.gui.impl.lobby.views.battle_result_view.battle_result_view import BrBattleResultsViewInLobby
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.battle_royale.lobby.views.BattleResultView()
    battleResultView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if battleResultView is not None:
        if battleResultView.arenaUniqueID == ctx.get('arenaUniqueID', -1):
            return
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(layoutID=contentResId))
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, BrBattleResultsViewInLobby, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return
