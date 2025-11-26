# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/event_dispatcher.py
from gui.impl.pub.notification_commands import NonPersistentEventNotificationCommand, NotificationEvent
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader, INotificationWindowController

@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showBattleRoyaleResultsView(ctx, notificationsMgr=None):
    notificationsMgr.append(NonPersistentEventNotificationCommand(NotificationEvent(method=showBattleRoyaleResultsInfo, ctx=ctx)))


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def showBattleRoyaleResultsInfo(ctx, appLoader=None):
    from battle_royale.gui.impl.lobby.views.states import BattleRoyaleBattleResultsState
    view = appLoader.getApp().containerManager.getViewByKey(BattleRoyaleBattleResultsState.VIEW_KEY)
    if view is not None:
        if view.content.arenaUniqueID == ctx.get('arenaUniqueID'):
            return
        view.destroy()
    BattleRoyaleBattleResultsState.goTo(**ctx)
    return


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
