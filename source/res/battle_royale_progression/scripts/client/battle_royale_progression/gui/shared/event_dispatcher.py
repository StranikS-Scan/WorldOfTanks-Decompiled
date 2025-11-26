# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/shared/event_dispatcher.py


def showProgressionView(activeTab=None):
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleProgressionState
    from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_main_view_model import MainViews
    if not activeTab:
        activeTab = MainViews.PROGRESSION
    BattleRoyaleProgressionState.goTo(ctx={'menuName': activeTab})


def showAwardsView(stage):
    from battle_royale_progression.gui.impl.lobby.views.battle_quest_awards_view import BattleQuestAwardsViewWindow
    BattleQuestAwardsViewWindow(stage).load()
