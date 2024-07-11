# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/shared/event_dispatcher.py
from typing import TYPE_CHECKING
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from gui import SystemMessages
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from skeletons.gui.game_control import IRacesBattleController
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl import backport
import BigWorld
from functools import partial
if TYPE_CHECKING:
    from typing import Optional
    from typing import Optional, List, Dict

@dependency.replace_none_kwargs(uiLoader=IGuiLoader, racesCtrl=IRacesBattleController)
def showRacesBattleResultView(arenaUniqueID, uiLoader=None, racesCtrl=None):
    if not racesCtrl.isAvailable():
        SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)
        return
    if racesCtrl.isInQueue():
        BigWorld.callback(0, partial(SystemMessages.pushMessage, text=backport.text(R.strings.system_messages.queue.isInQueue()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH))
        return
    from races.gui.impl.lobby.races_post_battle_view import RacesPostBattleView
    contentID = R.views.races.lobby.RacesPostBattleView()
    currentView = uiLoader.windowsManager.getViewByLayoutID(contentID)
    if currentView:
        currentView.destroy()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=RacesPostBattleView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'arenaUniqueID': arenaUniqueID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showRacesProgressionView(*args, **kwargs):
    uiLoader = dependency.instance(IGuiLoader)
    contentID = R.views.races.lobby.RacesProgressionView()
    if uiLoader.windowsManager.getViewByLayoutID(contentID) is None:
        from races.gui.impl.lobby.races_lobby_view.races_progression_view import RacesProgressionView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=RacesProgressionView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showRacesIntro(parent=None, notificationMgr=None):
    from races.gui.impl.lobby.races_lobby_view.races_intro_screen import RacesIntroWindow
    window = RacesIntroWindow(parent=parent)
    notificationMgr.append(WindowNotificationCommand(window))
