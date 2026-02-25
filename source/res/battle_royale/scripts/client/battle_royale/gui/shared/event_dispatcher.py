# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/event_dispatcher.py
from skeletons.gui.impl import IGuiLoader
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController

def showBattleRoyaleResults(ctx):
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleBattleResultsState
    BattleRoyaleBattleResultsState.goTo(**ctx)


def showHangar():
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleHangarState
    BattleRoyaleHangarState.goTo()


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showInfoPage(isModeSelector=False, guiLoader=None):
    from battle_royale.gui.impl.lobby.views.info_page import InfoPageWindow
    view = guiLoader.windowsManager.getViewByLayoutID(InfoPageWindow.LAYOUT_ID)
    if view is None:
        window = InfoPageWindow(isModeSelector)
        window.load()
    return


def showBattleRoyalePrimeTime():
    from battle_royale.gui.impl.lobby.views.states import BattleRoyalePrimeTimeState
    BattleRoyalePrimeTimeState.goTo()


def showHangarVehicleConfigurator():
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleVehicleInfoState
    BattleRoyaleVehicleInfoState.goTo()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showAwardsView(stage, notificationMgr=None):
    from battle_royale.gui.impl.lobby.views.battle_quest_awards_view import BattleQuestAwardsViewWindow
    window = BattleQuestAwardsViewWindow(stage)
    notificationMgr.append(WindowNotificationCommand(window))


def showProgressionView(activeTab=None):
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleProgressionState
    from battle_royale.gui.impl.gen.view_models.views.lobby.views.progression.progression_main_view_model import MainViews
    if not activeTab:
        activeTab = MainViews.PROGRESSION
    BattleRoyaleProgressionState.goTo(ctx={'menuName': activeTab})
