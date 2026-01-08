# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/shared/event_dispatcher.py
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController

def showProgressionView(activeTab=None):
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleProgressionState
    from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_main_view_model import MainViews
    if not activeTab:
        activeTab = MainViews.PROGRESSION
    BattleRoyaleProgressionState.goTo(ctx={'menuName': activeTab})


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showAwardsView(stage, notificationMgr=None):
    from battle_royale_progression.gui.impl.lobby.views.battle_quest_awards_view import BattleQuestAwardsViewWindow
    window = BattleQuestAwardsViewWindow(stage)
    notificationMgr.append(WindowNotificationCommand(window))
