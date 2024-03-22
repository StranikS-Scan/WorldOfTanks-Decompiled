# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/clan_supply_helpers.py
import typing
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController

def showClanSupplyView(tabId=None, *args, **kwargs):
    from gui.impl.lobby.clan_supply.main_view import MainView
    event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.clan_supply.ClanSupply(), MainView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId, *args, **kwargs)
    g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showClanSupplyRewardWindow(isElite, rewards, notificationMgr=None):
    from gui.impl.lobby.clan_supply.rewards_view import RewardsViewWindow
    window = RewardsViewWindow(isElite, rewards)
    notificationMgr.append(WindowNotificationCommand(window))
