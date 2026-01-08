# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/event_dispatcher.py
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

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
